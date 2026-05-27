from datetime import datetime
from sqlmodel import Session

from src.config.database import db_engine
from src.models.auditorias.models import *

def registrar_auditoria_mesa(id_mesa: int, id_orden: int, hora_entrada: datetime, hora_salida: datetime = None) -> bool:
    with Session(db_engine) as session:
        try:
            auditoria = Auditoria_Mesas(
                IdMesa=id_mesa, 
                IdOrden=id_orden, 
                HoraEntrada=hora_entrada, 
                HoraSalida=hora_salida
            )
            session.add(auditoria)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al registrar auditoría de mesa: {e}")
            return False

def registrar_auditoria_comedor(username: str, hora_apertura: datetime, hora_cerrar: datetime) -> bool:
    with Session(db_engine) as session:
        try:
            auditoria = Auditoria_Comedor(
                Username=username, 
                HoraApertura=hora_apertura, 
                HoraCerrar=hora_cerrar
            )
            session.add(auditoria)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al registrar auditoría de comedor: {e}")
            return False

def registrar_auditoria_usuario(username: str, id_usuario_creado: int, tipo_accion: TipoDeAccion) -> bool:
    with Session(db_engine) as session:
        try:
            auditoria = Auditoria_Usuario(
                Username=username, 
                IdUsuarioCreado=id_usuario_creado, 
                TipoAccion=tipo_accion
            )
            session.add(auditoria)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al registrar auditoría de usuario: {e}")
            return False

def registrar_auditoria_factura(username: str, id_factura: int, tipo_accion: TipoDeAccion) -> bool:
    with Session(db_engine) as session:
        try:
            auditoria = Auditoria_Facturas(
                Username=username, 
                IdFactura=id_factura, 
                TipoAccion=tipo_accion
            )
            session.add(auditoria)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al registrar auditoría de factura: {e}")
            return False

def registrar_auditoria_orden(username: str, id_orden: int, tipo_accion: TipoDeAccion) -> bool:
    with Session(db_engine) as session:
        try:
            auditoria = Auditoria_Ordenes(
                Username=username, 
                IdOrden=id_orden, 
                TipoAccion=tipo_accion
            )
            session.add(auditoria)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al registrar auditoría de orden: {e}")
            return False

def registrar_auditoria_pedido(username: str, id_pedido: int, tipo_accion: TipoDeAccion) -> bool:
    with Session(db_engine) as session:
        try:
            auditoria = Auditoria_Pedidos(
                Username=username, 
                IdPedido=id_pedido, 
                TipoAccion=tipo_accion
            )
            session.add(auditoria)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al registrar auditoría de pedido: {e}")
            return False

def registrar_auditoria_imagen(username: str, id_imagen: int, tipo_accion: TipoDeAccion) -> bool:
    with Session(db_engine) as session:
        try:
            auditoria = Auditoria_Imagenes(
                Username=username, 
                IdImagen=id_imagen, 
                TipoAccion=tipo_accion
            )
            session.add(auditoria)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al registrar auditoría de imagen: {e}")
            return False

def registrar_auditoria_platillo(username: str, id_platillo: int, tipo_accion: TipoDeAccion) -> bool:
    with Session(db_engine) as session:
        try:
            auditoria = Auditoria_Platillos(
                Username=username, 
                IdPlatillo=id_platillo, 
                TipoAccion=tipo_accion
            )
            session.add(auditoria)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al registrar auditoría de platillo: {e}")
            return False

def registrar_auditoria_cliente(username: str, id_cliente: int, tipo_accion: TipoDeAccion) -> bool:
    with Session(db_engine) as session:
        try:
            auditoria = Auditoria_Cliente(
                Username=username, 
                IdCliente=id_cliente, 
                TipoAccion=tipo_accion
            )
            session.add(auditoria)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al registrar auditoría de cliente: {e}")
            return False

def registrar_auditoria_pago(username: str, id_pago: int, tipo_accion: TipoDeAccion) -> bool:
    with Session(db_engine) as session:
        try:
            auditoria = Auditoria_Pagos(
                Username=username, 
                IdPago=id_pago, 
                TipoAccion=tipo_accion
            )
            session.add(auditoria)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al registrar auditoría de pago: {e}")
            return False