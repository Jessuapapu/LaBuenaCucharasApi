from src.models.ordenes.models import *
from src.models.ordenes.types import *
from src.models.caja.models import Reembolsos, Caja, Pago, ReferenciaPago
from src.services.ordenes import service as OrdenesServices
from src.models.ordenes.types import *
from sqlmodel import Session, text, select
from src.config.database import db_engine
import decimal
from src.services.auditorias.services import registrar_auditoria_Caja
from src.models.auditorias.types import TipoDeAccion
from src.services.ordenes.service import obtener_orden
from src.models.ordenes.types import EstadoOrden

CajaMonitor = Caja()

def abrir_Caja():
    return CajaMonitor.abrirCaja()

def Cerrar_Caja(username: str):
    infoCaja = CajaMonitor.cerrarCaja()
    if not infoCaja:
        return False

    with Session(db_engine) as session:
        try:
            nueva_auditoria = registrar_auditoria_Caja(
                username=username, 
                hora_apertura=infoCaja["HoraApertura"], 
                hora_cerrar=infoCaja["HoraCerrar"]
            )
            session.add(nueva_auditoria)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(e)
            return False

def Mandar_a_caja(IdOrden: int, Monto: float) -> dict | None:
    if not CajaMonitor.HoraApertura:    
        return None
    return CajaMonitor.AgregarOrden(IdOrden=IdOrden, Monto=Monto)

def Pagar_cuenta(IdOrden: int, Monto: float, Metodo: str, Referencia: str = ""):
    if not CajaMonitor.HoraApertura:    
        return False
    estado = CajaMonitor.Pagar(IdOrden=IdOrden, Monto=Monto, metodoPago=Metodo, referencia=Referencia)
    if not estado:
        return False
    
    if estado <= 0.0:
        return Cancelar_Cuenta(IdOrden=IdOrden)
    
def Cancelar_Cuenta(IdOrden: int):
    # Esto ocurre cuando la cuenta ya llegó a 0 y se manda a guardar en BD
    if not CajaMonitor.HoraApertura:    
        return False
    
    historial = CajaMonitor.obtener_Historial(IdOrden)
    if not CajaMonitor.CancelarOrden(IdOrden):
        return False
    
    with Session(db_engine) as session:
        try:
            for pago in historial:
                if pago['accion'] == 'pago':
                    Nuevo_pago = Pago(MetodoPagos=pago['Metodo'], IdOrden=IdOrden, PagoTotal=pago["Monto"], Fecha=pago['fecha'])
                    session.add(Nuevo_pago)
                    session.flush()

                    if Nuevo_pago.MetodoPagos in (TipoPago.TARJETA_CREDITO, TipoPago.TARJETA_DEBITO, TipoPago.TRANSFERENCIA) and pago['referencia']:
                        Nueva_Referencia = ReferenciaPago(IdPago=Nuevo_pago.IdPago, referencia=pago['referencia'])
                        session.add(Nueva_Referencia)

            statement = select(Ordenes).where(Ordenes.IdOrdenes == IdOrden)
            orden_cancelada = session.exec(statement).first()

            if not orden_cancelada:
                return None
            
            orden_cancelada.Estado = EstadoOrden.ENTREGADO
            session.add(orden_cancelada)
            
            session.commit()

            return True

        except Exception as e:
            session.rollback()
            print(e)
            return False

def Anular_Cuenta(IdOrden: int):
    if not CajaMonitor.HoraApertura:    
        return False
    
    OrdenCancelada = CajaMonitor.AnularOrden(IdOrden)
    if not OrdenCancelada:
        return False
    
    with Session(db_engine) as session:
        try:
            ordenActualizar = OrdenesServices.obtener_orden(IdOrden)
            if not ordenActualizar:
                return False
            
            # Ajusta la llamada según tu servicio de órdenes, aquí uso raw query por seguridad
            statement_anular = text("UPDATE ordenes SET Estado = :estado WHERE IdOrdenes = :idOrden")
            session.exec(statement_anular, params={'estado': EstadoOrden.ANULADO.value, 'idOrden': IdOrden})
            
            statement_pagos = text("EXEC ActualizarPagos @IdOrden = :idOrden")
            session.exec(statement=statement_pagos, params={'idOrden': IdOrden})  
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(e)
            return False

def Reembolsar(IdOrden: int, Monto: float, razon: str):
    if not CajaMonitor.to_Estado():
        return False
    
    if not CajaMonitor.ValidarIdTodos(IdOrden):
        return False

    with Session(db_engine) as session:
        try:
            query = select(Pago).where(Pago.IdOrden == IdOrden)
            validacion = session.exec(query).first()
            if not validacion:
                return False

            statement = text("EXEC ActualizarPagos @IdOrden = :idOrden")
            session.exec(statement=statement, params={'idOrden': IdOrden})

            nuevoReembolso = Reembolsos(IdOrden=IdOrden, Monto=decimal.Decimal(Monto), Razones=razon)
            session.add(nuevoReembolso)
            orden_a_cambiar = obtener_orden(IdOrden)

            session.commit()

            
            Anular_Cuenta(IdOrden)


            return True
        except Exception as e:
            session.rollback()
            print(e)
            return False

def Actualizar_Monto(IdOrden: int, Monto: float) -> dict | None:
    return CajaMonitor.actualizarMonto(IdOrden=IdOrden, Monto=Monto)

def obtener_cuenta(IdOrden: int)  -> dict | None:
    return CajaMonitor.obtener_Orden(IdOrden)

def obtener_Caja():
    if not CajaMonitor.to_Estado():
        return False
    return CajaMonitor.to_dict()

def obtener_estado_caja():
    return CajaMonitor.to_Estado()