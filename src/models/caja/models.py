from sqlmodel import Field, SQLModel, Column, String
import decimal
from datetime import datetime
from src.models.ordenes.types import TipoPago

class OrdenEntrando():
    def __init__(self, IdOrden: int, Monto: float):
        self.IdOrden: int = IdOrden
        self.Monto: float = Monto
        self.MontoRestante: float = self.Monto 
        self.HoraFecha: datetime = datetime.now()
        self.HistorialPago: list[dict] = []
        
    def Pagar(self, Monto: float, metodoPagar: str, referencia: str = ""):
        if Monto <= 0:
            return False
        self.MontoRestante -= Monto
        self.HistorialPago.append({
            "Monto": Monto,
            "Metodo": metodoPagar,
            "accion": "pago",
            "fecha": datetime.now(),
            "referencia": referencia
        })
        return self.MontoRestante
    
    def RetornarMonto(self, Monto: float):
        if Monto <= 0:
            return False
        if (self.MontoRestante + Monto) > self.Monto:
            return False
            
        self.MontoRestante += Monto
        self.HistorialPago.append({
            "Monto": Monto,
            "Metodo": None,
            "accion": "cancelacion",
            "fecha": datetime.now()
        })
        return self.MontoRestante
    
    def actualizarMonto(self, Monto: float):
        self.Monto = Monto
        # Recalcular el restante basado en los pagos ya hechos
        pagos_realizados = sum([p["Monto"] for p in self.HistorialPago if p["accion"] == "pago"])
        cancelaciones = sum([p["Monto"] for p in self.HistorialPago if p["accion"] == "cancelacion"])
        neto_pagado = pagos_realizados - cancelaciones
        self.MontoRestante = self.Monto - neto_pagado
        return self.to_dict()
    
    def to_dict(self) -> dict:
        historial_formateado = []
        for pago in self.HistorialPago:
            pago_copia = pago.copy()
            if isinstance(pago_copia["fecha"], datetime):
                pago_copia["fecha"] = pago_copia["fecha"].isoformat()
            historial_formateado.append(pago_copia)

        return {
            "IdOrden": self.IdOrden,
            "Monto": self.Monto,
            "MontoRestante": self.MontoRestante,
            "FechaHora": self.HoraFecha.isoformat() if isinstance(self.HoraFecha, datetime) else self.HoraFecha, 
            "Historial": historial_formateado
        }
    
class Caja():
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__constructor()
        return cls._instance
   
    def __constructor(self):
        self.HoraApertura: datetime | None = None
        self.HoraCerrar: datetime | None = None
        self.ListaOrdenesAtender: dict[int,OrdenEntrando] = {}
        self.ListaOrdenesAtendidas: dict[int,OrdenEntrando] = {}
        self.ListaOrdenesCanceladas: dict[int,OrdenEntrando] = {}
        
    def validarId(self, IdOrden: int):
        return IdOrden in self.ListaOrdenesAtender
    
    def ValidarIdTodos(self, IdOrden: int):
        return (IdOrden in self.ListaOrdenesAtender or 
                IdOrden in self.ListaOrdenesAtendidas or 
                IdOrden in self.ListaOrdenesCanceladas)
    
    def limpiar_orden(self):
        hoy = datetime.now().date()
        ids_a_borrar = [id_ord for id_ord, orden in self.ListaOrdenesAtendidas.items() if orden.HoraFecha.date() < hoy]
        for id_ord in ids_a_borrar:
            del self.ListaOrdenesAtendidas[id_ord]

    def Pagar(self, Monto: float, IdOrden: int, metodoPago: str, referencia: str = ""):
        if not self.validarId(IdOrden):
            return False
        restante = self.ListaOrdenesAtender[IdOrden].Pagar(Monto, metodoPago, referencia)
        if restante is False:
            return False
        return restante
    
    def RetornarMonto(self, Monto: float, IdOrden: int):
        if not self.validarId(IdOrden):
            return False
        return self.ListaOrdenesAtender[IdOrden].RetornarMonto(Monto)

    def AgregarOrden(self, Monto: float, IdOrden: int):
        if self.validarId(IdOrden):
            return None
        self.ListaOrdenesAtender[IdOrden] = OrdenEntrando(IdOrden=IdOrden, Monto=Monto)
        return self.ListaOrdenesAtender[IdOrden].to_dict()
    
    def abrirCaja(self):
        self.limpiar_orden()
        if self.HoraApertura:
            return
        self.HoraApertura = datetime.now()

    def cerrarCaja(self):
        if not self.HoraApertura:
            return False
        if len(self.ListaOrdenesAtender) > 0:
            return False # No se puede cerrar con órdenes pendientes
        
        self.HoraCerrar = datetime.now()
        infoRetornar = self.to_dict()
        
        # Reset de caja
        self.HoraApertura = None
        self.HoraCerrar = None
        self.ListaOrdenesAtendidas.clear()
        self.ListaOrdenesCanceladas.clear()
        
        return infoRetornar
    
    def AnularOrden(self, IdOrden: int):
        if not self.validarId(IdOrden):
            return False
        self.ListaOrdenesCanceladas[IdOrden] = self.ListaOrdenesAtender.pop(IdOrden)
        return self.ListaOrdenesCanceladas[IdOrden].to_dict()   
    
    def CancelarOrden(self, IdOrden: int):
        if not self.validarId(IdOrden):
            return False
        if self.obtener_monto(IdOrden).get('MontoRestante', 1) > 0:
            return False # No se puede dar por cancelada/pagada si aún debe
        self.ListaOrdenesAtendidas[IdOrden] = self.ListaOrdenesAtender.pop(IdOrden)
        return self.ListaOrdenesAtendidas[IdOrden].to_dict()

    def obtener_monto(self, IdOrden: int):
        if IdOrden in self.ListaOrdenesAtender:
            return self.ListaOrdenesAtender[IdOrden].to_dict()
        if IdOrden in self.ListaOrdenesAtendidas:
            return self.ListaOrdenesAtendidas[IdOrden].to_dict()
        return None
    
    def obtener_Historial(self, IdOrden: int):
        if IdOrden in self.ListaOrdenesAtender:
            return self.ListaOrdenesAtender[IdOrden].HistorialPago
        if IdOrden in self.ListaOrdenesAtendidas:
            return self.ListaOrdenesAtendidas[IdOrden].HistorialPago
        return []
            
    def obtener_Orden(self, IdOrden: int) -> dict | None:
        if IdOrden in self.ListaOrdenesAtender:
            return self.ListaOrdenesAtender[IdOrden].to_dict()
        if IdOrden in self.ListaOrdenesAtendidas:
            return self.ListaOrdenesAtendidas[IdOrden].to_dict()
        if IdOrden in self.ListaOrdenesCanceladas:
            return self.ListaOrdenesCanceladas[IdOrden].to_dict()
        return None
        
    def to_Estado(self):
        return self.HoraApertura is not None
    
    def actualizarMonto(self, IdOrden: int, Monto: float):
        if not self.validarId(IdOrden):
            return None
        return self.ListaOrdenesAtender[IdOrden].actualizarMonto(Monto)

    def to_dict(self):
        self.limpiar_orden()
        LOA = [orden.to_dict() for orden in self.ListaOrdenesAtender.values()]
        LAOT = [orden.to_dict() for orden in self.ListaOrdenesAtendidas.values()]
        return {
            "HoraApertura": self.HoraApertura.isoformat(),
            "HoraCerrar":  self.HoraCerrar.isoformat() if self.HoraCerrar else None,
            "OrdenesActivas": LOA,
            "OrdenesAtendidas": LAOT
        }

class Reembolsos(SQLModel, table = True):
    IdReembolso: int | None = Field(default=None, primary_key=True)
    IdOrden: int = Field(foreign_key='ordenes.IdOrdenes')
    Monto: decimal.Decimal = Field(nullable= False)
    Razones: str = Field(nullable= False)

class Pago(SQLModel, table = True):
    IdPago: int | None  = Field(default = None, primary_key = True, index = True)
    MetodoPagos: TipoPago = Field(default = None, sa_column=Column(String(50)))
    IdOrden: int | None = Field(default = None, foreign_key = "ordenes.IdOrdenes")
    PagoTotal: decimal.Decimal = Field(default = None)
    Fecha: datetime = Field(default_factory=datetime.now)
    Estado: bool = Field(default=True, nullable=False)

class ReferenciaPago(SQLModel, table = True):
    IdReferenciaPago: int | None = Field(default=None, primary_key=True)
    IdPago: int | None = Field(default = None, foreign_key = "pago.IdPago")
    referencia: str = Field(default = None)