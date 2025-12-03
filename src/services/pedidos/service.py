from hmac import new
from src.models.pedidos.models import Pedidos
from src.models.pedidos.types import EstadoPedido
from sqlmodel import Session
from src.config.database import db_engine
from src.services.clientes.service import obtener_id_cliente_por_nombre
import datetime

def crear_pedido(nombre_cliente: str, fecha: datetime.date):
    id_cliente = obtener_id_cliente_por_nombre(nombre_cliente)

    if id_cliente is None:
        raise ValueError(f"No se pudo obtener un id de cliente con el nombre de cliente {nombre_cliente}")

    nuevo_pedido = Pedidos(IdCliente=id_cliente, FechaPedido=str(fecha), Estado=EstadoPedido.PENDIENTE)
    
    with Session(db_engine) as session:
        try:
            session.add(nuevo_pedido)
            session.commit()
            return nuevo_pedido
        except Exception as e:
            session.rollback()
            return e
