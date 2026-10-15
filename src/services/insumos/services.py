from sqlmodel import Session, select
from typing import Optional
from src.config.database import get_session_context
from src.models.insumos.models import Insumos
from src.schemas.insumos import InsumoCreateSchema, InsumoUpdateSchema

def listar_insumos(pagina: int = 1, rows: int = 10, todo: int = 0):
    with get_session_context() as session:
        try:
            query = select(Insumos)
            
            if not todo:
                offset = (pagina - 1) * rows
                query = query.offset(offset).limit(rows)
                
            resultados = session.exec(query).all()
            return resultados
        except Exception as e:
            print(f"Error al listar insumos: {e}")
            return None

def obtener_insumo_por_id(id_insumo: int):
    with get_session_context() as session:
        try:
            insumo = session.get(Insumos, id_insumo)
            return insumo
        except Exception as e:
            print(f"Error al obtener insumo: {e}")
            return None

def crear_insumo(payload: InsumoCreateSchema, username: Optional[str] = None) -> bool:
    with get_session_context() as session:
        try:
            nuevo_insumo = Insumos(
                NombreInsumo=payload.NombreInsumo,
                Stock=payload.Stock,
                Prioridad=payload.Prioridad
            )
            session.add(nuevo_insumo)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al crear insumo: {e}")
            return False

def actualizar_insumo(id_insumo: int, payload: InsumoUpdateSchema, username: Optional[str] = None) -> bool:
    with get_session_context() as session:
        try:
            insumo = session.get(Insumos, id_insumo)
            if not insumo:
                return False
            
            # Extraer solo los datos enviados en la petición
            update_data = payload.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(insumo, key, value)
                
            session.add(insumo)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al actualizar insumo: {e}")
            return False

def eliminar_insumo(id_insumo: int, username: Optional[str] = None) -> bool:
    with get_session_context() as session:
        try:
            insumo = session.get(Insumos, id_insumo)
            if not insumo:
                return False
            
            session.delete(insumo)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error al eliminar insumo: {e}")
            return False