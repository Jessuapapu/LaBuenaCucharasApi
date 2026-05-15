from src.config.database import db_engine
from sqlmodel import Session
from sqlalchemy import text
from src.models.pedidos import models as pedidos
from src.services.ordenes import service as ordenesService

def validar_cliente_lista_ordenes(listaOrdenes:list[int]):
    cliente_fijo = ordenesService.obtener_orden(listaOrdenes[0])["IdCliente"]

    for orden in listaOrdenes:
        if cliente_fijo != ordenesService.obtener_orden(orden)["IdCliente"]:
            return False
        
        return True
    

def crear_pedido(listaIdOrdenes: list, TipoPedido: str):

    if not validar_cliente_lista_ordenes(listaOrdenes=listaIdOrdenes):
        return False

    with Session(db_engine) as session:
        try:
            nuevo_pedido = pedidos.Pedidos()
            session.add(nuevo_pedido)
            
            nuevo_estado = pedidos.TipoPedido(TipoPedidos=TipoPedido)
            session.add(nuevo_estado)
            session.flush()
            
            for IdOrden in listaIdOrdenes:
                nueva_relacion_ordenes = pedidos.PedidosOrdenes(IdPedido=nuevo_pedido.IdPedido,IdOrdenes=IdOrden)
                session.add(nueva_relacion_ordenes)

            session.commit()
            return True
        
        except:
            session.rollback()
            return False


def buscar_pedido(IdPedido: int = None, IdCliente: int = None, NombreCliente: str = None):
    
    pass