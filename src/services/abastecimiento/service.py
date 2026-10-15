from decimal import Decimal
from sqlmodel import Session, select, text, desc
import json
from typing import Optional
from src.config.database import db_engine
from src.models.proveedores.models import RegistroDeAbastecimiento, DetallesRegistroIngredientes, DetallesRegistroInsumos
from src.schemas.abastecimiento import AbastecimientoCreateSchema

def obtener_historial_abastecimiento():
    with Session(db_engine) as session:
        try:
            statement = select(RegistroDeAbastecimiento).order_by(desc(RegistroDeAbastecimiento.IdRegistro))
            historial = session.exec(statement).all()
            return historial
        except Exception as e:
            print(f"Error al obtener historial: {e}")
            return None

def registrar_abastecimiento(payload: AbastecimientoCreateSchema, username: Optional[str] = None) -> bool:
    with Session(db_engine) as session:
        try:
            # 1. Crear la cabecera
            nuevo_abastecimiento = RegistroDeAbastecimiento(
                CostoTotal=payload.CostoTotal,
                IdProveedor=payload.IdProveedor,
                TotalIngresado=payload.TotalIngresado,
            )
            session.add(nuevo_abastecimiento)
            session.flush()

            # 2. Agregar Insumos (si vienen)
            if payload.listaInsumos:
                nuevo_detalle_insumo_lista = [
                    DetallesRegistroInsumos(
                        IdRegistroAbastecimiento=nuevo_abastecimiento.IdRegistro, 
                        IdInsumo=insumo.IdInsumo, 
                        TotalIngresado=insumo.TotalIngresado, 
                        CostoIndividual=Decimal(str(insumo.CostoIndividual))
                    ) for insumo in payload.listaInsumos
                ]
                session.add_all(nuevo_detalle_insumo_lista)

            # 3. Agregar Ingredientes (si vienen)
            if payload.listaIngredientes:
                nuevo_detalle_ingrediente_lista = [
                    DetallesRegistroIngredientes(
                        IdRegistroAbastecimiento=nuevo_abastecimiento.IdRegistro,
                        IdIngrediente=ingrediente.IdIngrediente,
                        TotalIngresado=ingrediente.TotalIngresado, 
                        CostoIndividual=Decimal(str(ingrediente.CostoIndividual))
                    ) for ingrediente in payload.listaIngredientes
                ]
                session.add_all(nuevo_detalle_ingrediente_lista)
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            print(f"Error al registrar abastecimiento: {e}")
            return False

def obtener_detalles_abastecimiento(id_registro: int):
    with Session(db_engine) as session:
        try:
            query = text("EXEC DetallesAbastIngredientes @IdRegistro = :id_param")
            resultado = session.exec(query, params={"id_param": id_registro})
            json_string = resultado.scalar()
            
            if not json_string:
                return None  # Retornamos None para que el router maneje el 404

            datos_parseados = json.loads(json_string)
            return datos_parseados
        except Exception as e:
            print(f"Error al obtener detalles de abastecimiento: {e}")
            return None