from sqlmodel import Session, select
from sqlalchemy import text
from src.config.database import db_engine
from typing import List, Optional
from src.models.pedidos.models import Pedidos, PedidosOrdenes
from src.models.pedidos.types import TipoPedidoss, EstadoPedido
from src.services.ordenes import service as ordenesService  # Ajusta si esto también lo cambiaste a funciones
from src.services.auditorias.services import registrar_auditoria_pedido
from src.models.auditorias.types import TipoDeAccion
import datetime

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

                StatementValidar = select(PedidosOrdenes.IdOrdenes).select_from(PedidosOrdenes).where(PedidosOrdenes.IdOrdenes == IdOrden)
                if session.exec(statement=StatementValidar).first():
                    return False

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

def listar_pedidos(
                id_orden: int = None,
                id_pedido: int = None, 
                id_cliente: int = None, 
                tipo: str = None, 
                pagina: int = 1, 
                rows: int = 10, 
                todo: int = 0,
                fecha_inicio: datetime.datetime | None = None,
                fecha_fin: datetime.datetime | None = None,
                monto: float | None = None,
                monto_fin: float | None = None,

):
    with Session(db_engine) as session:
        query = text("""
            EXEC MostrarPedidos 
                @IdOrden = :IdOrden, 
                @IdPedido = :IdPedido, 
                @IdCliente = :IdCliente, 
                @Tipo = :Tipo, 
                @Pagina = :Pagina, 
                @Rows = :Rows, 
                @Todo = :Todo,
                @FechaInicio = :fecha_inicio,
                @FechaFin = :fecha_fin,
                @Monto = :monto,
                @MontoFin = :monto_fin
        """)
        
        params = {
            "IdOrden": id_orden, 
            "IdPedido": id_pedido, 
            "IdCliente": id_cliente,
            "Tipo": tipo, 
            "Pagina": pagina, 
            "Rows": rows,
            "Todo": todo,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "monto": monto,
            "monto_fin": monto_fin
        }
        
        resultados = session.exec(query, params=params).mappings().all()
        return [dict(row) for row in resultados]

def obtener_pedido_por_id(id_pedido: int):
    with Session(db_engine) as session:
        pedido = session.exec(select(Pedidos).where(Pedidos.IdPedido == id_pedido)).first()
        return pedido
    
def modificar_pedido(
    id_pedido: int, 
    estado: Optional[EstadoPedido] = None, 
    tipo_pedido: Optional[TipoPedidoss] = None, 
    listaIdOrdenes: Optional[List[int]] = None, # 🆕 Soporte para modificar las órdenes asignadas
    username: Optional[str] = None
) -> bool:
    with Session(db_engine) as session:
        try:
            pedido = session.exec(select(Pedidos).where(Pedidos.IdPedido == id_pedido)).first()
            if not pedido:
                return False
                
            # 🛡️ VALIDACIÓN: Si el pedido ya está ENTREGADO o ANULADO, congelar modificaciones estructurales
            if pedido.Estado in [EstadoPedido.ENTREGADO, EstadoPedido.ANULADO] and listaIdOrdenes is not None:
                print("No se pueden alterar las órdenes de un pedido finalizado o anulado.")
                return False
                
            # 🆕 VALIDACIÓN DE INTEGRIDAD PARA NUEVAS ÓRDENES
            if listaIdOrdenes is not None:
                # 1. Validar que todas las órdenes pertenezcan al mismo cliente
                if not validar_cliente_lista_ordenes(listaIdOrdenes):
                    return False
                
                # 2. Validar masivamente que las órdenes no estén en OTROS pedidos distintos a este
                declaracion_validar = (
                    select(PedidosOrdenes.IdOrdenes)
                    .where(PedidosOrdenes.IdOrdenes.in_(listaIdOrdenes))
                    .where(PedidosOrdenes.IdPedido != id_pedido)
                )
                ordenes_ocupadas = session.exec(declaracion_validar).all()
                if ordenes_ocupadas:
                    print(f"Error: Las órdenes {ordenes_ocupadas} ya están ocupadas por otros pedidos.")
                    return False

                # 3. Reestructurar relaciones: Eliminar vínculos anteriores e insertar los nuevos
                # Usamos un delete directo para limpiar la tabla intermedia de este pedido específico
                session.exec(
                    text("DELETE FROM pedidosordenes WHERE IdPedido = :id_pedido"),
                    {"id_pedido": id_pedido}
                )
                
                for id_orden in listaIdOrdenes:
                    nueva_relacion = PedidosOrdenes(IdPedido=id_pedido, IdOrdenes=id_orden)
                    session.add(nueva_relacion)

            # Actualización de campos nativos
            if estado:
                pedido.Estado = estado
            if tipo_pedido:
                pedido.TipoPedidos = tipo_pedido
                
            session.add(pedido)
            session.commit()
            
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