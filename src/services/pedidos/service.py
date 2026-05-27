from sqlmodel import Session, select
from sqlalchemy import text
from src.config.database import db_engine
from src.models.pedidos.models import Pedidos, PedidosOrdenes
from src.models.pedidos.types import TipoPedidoss, EstadoPedido
from src.services.ordenes import service as ordenesService  # Ajusta si esto también lo cambiaste a funciones
from src.services.auditorias.services import registrar_auditoria_pedido
from src.models.auditorias.types import TipoDeAccion

def validar_cliente_lista_ordenes(listaOrdenes: list[int]) -> bool:
    if not listaOrdenes:
        return False
        
    cliente_fijo = ordenesService.obtener_orden(listaOrdenes[0])["IdCliente"]

    for orden in listaOrdenes:
        if cliente_fijo != ordenesService.obtener_orden(orden)["IdCliente"]:
            return False
            
    return True 

def crear_pedido(listaIdOrdenes: list[int], tipo_pedido: TipoPedidoss, username: str | None = None) -> bool:
    if not validar_cliente_lista_ordenes(listaOrdenes=listaIdOrdenes):
        return False

    with Session(db_engine) as session:
        try:
            nuevo_pedido = Pedidos(
                Estado=EstadoPedido.PENDIENTE, # O el estado inicial por defecto
                TipoPedidos=tipo_pedido
            )
            session.add(nuevo_pedido)
            session.flush() 
            
            for IdOrden in listaIdOrdenes:
                nueva_relacion_ordenes = PedidosOrdenes(
                    IdPedido=nuevo_pedido.IdPedido,
                    IdOrdenes=IdOrden
                )
                session.add(nueva_relacion_ordenes)

            session.commit()
            # Auditoría: creación de pedido
            if username and nuevo_pedido.IdPedido is not None:
                try:
                    registrar_auditoria_pedido(username, nuevo_pedido.IdPedido, TipoDeAccion.CREAR)
                except Exception:
                    pass

            return True
        
        except Exception as e:
            session.rollback()
            print(f"Error al crear pedido: {e}")
            return False

def listar_pedidos(id_orden: int = None, id_pedido: int = None, id_cliente: int = None, 
                   tipo: str = None, pagina: int = 1, rows: int = 10, todo: int = 0):
    with Session(db_engine) as session:
        query = text("""
            EXEC MostrarPedidos 
                @IdOrden = :IdOrden, 
                @IdPedido = :IdPedido, 
                @IdCliente = :IdCliente, 
                @Tipo = :Tipo, 
                @Pagina = :Pagina, 
                @Rows = :Rows, 
                @Todo = :Todo
        """)
        
        params = {
            "IdOrden": id_orden, "IdPedido": id_pedido, "IdCliente": id_cliente,
            "Tipo": tipo, "Pagina": pagina, "Rows": rows, "Todo": todo
        }
        
        resultados = session.execute(query, params).mappings().all()
        return [dict(row) for row in resultados]

def obtener_pedido_por_id(id_pedido: int):
    with Session(db_engine) as session:
        pedido = session.exec(select(Pedidos).where(Pedidos.IdPedido == id_pedido)).first()
        return pedido

def modificar_pedido(id_pedido: int, estado: EstadoPedido = None, tipo_pedido: TipoPedidoss = None, username: str | None = None) -> bool:
    with Session(db_engine) as session:
        try:
            pedido = session.exec(select(Pedidos).where(Pedidos.IdPedido == id_pedido)).first()
            if not pedido:
                return False
                
            if estado:
                pedido.Estado = estado
            if tipo_pedido:
                pedido.TipoPedidos = tipo_pedido
                
            session.add(pedido)
            session.commit()
            # Auditoría: modificación de pedido
            if username:
                try:
                    registrar_auditoria_pedido(username, id_pedido, TipoDeAccion.ACTUALIZAR)
                except Exception:
                    pass

            return True
        except Exception as e:
            session.rollback()
            print(f"Error al modificar pedido: {e}")
            return False

def eliminar_pedido(id_pedido: int, username: str | None = None) -> bool:
    with Session(db_engine) as session:
        try:
            pedido = session.exec(select(Pedidos).where(Pedidos.IdPedido == id_pedido)).first()
            if not pedido:
                return False
            
            # 1. Eliminar relaciones en la tabla intermedia primero (Evita error de Foreign Key)
            relaciones = session.exec(select(PedidosOrdenes).where(PedidosOrdenes.IdPedido == id_pedido)).all()
            for relacion in relaciones:
                session.delete(relacion)
                
            # 2. Eliminar el pedido padre
            session.delete(pedido)
            session.commit()
            # Auditoría: eliminación de pedido
            if username:
                try:
                    registrar_auditoria_pedido(username, id_pedido, TipoDeAccion.ELIMINAR)
                except Exception:
                    pass

            return True
            
        except Exception as e:
            session.rollback()
            print(f"Error al eliminar pedido: {e}")
            return False
        

def obtener_detalles_pedido(id_pedido: int, id_orden: int = None, id_cliente: int = None):
    with Session(db_engine) as session:
        query = text("""
            EXEC MostrarDetallesPedidos 
                @IdPedido = :IdPedido, 
                @IdOrden = :IdOrden, 
                @IdCliente = :IdCliente
        """)
        
        params = {
            "IdPedido": id_pedido,
            "IdOrden": id_orden,
            "IdCliente": id_cliente
        }
        
        # Ejecutamos y parseamos el resultado tabular del SP
        resultados = session.execute(query, params).mappings().all()
        return [dict(row) for row in resultados]