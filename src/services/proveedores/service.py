from decimal import Decimal
from sqlmodel import Session, select, text
import json
from src.config.database import db_engine
from src.models.insumos.models import DetallesRegistroInsumos

from src.models.proveedores.models import *
from src.models.proveedores.types import TipoDeProveedor
from src.schemas.abastecimineto import *


def obtener_proveedores():
    with Session(db_engine) as session:
        statement = select(Proveedores)
        proveedores = session.exec(statement).all()

        return proveedores


def obtener_proveedor_por_nombre(nombre: str):
    with Session(db_engine) as session:
        statement = select(Proveedores).where(Proveedores.NombreProveedor == nombre)
        proveedores = session.exec(statement).first()

        return proveedores


def registrar_proveedor(nombre: str, direccion: str, tipo: TipoDeProveedor):
    nuevo_proveedor = Proveedores(
        NombreProveedor=nombre, Direccion=direccion, Tipo=tipo
    )
    with Session(db_engine) as session:
        session.add(nuevo_proveedor)
        session.commit()

    return nuevo_proveedor


def obtener_historial_abastecimiento():
    with Session(db_engine) as session:
        statement = select(RegistroDeAbastecimiento)
        historial = session.exec(statement).all()

        return historial


def registrar_abastecimiento(
    costo_total: Decimal, id_proveedor: int, total_ingresado: int, Detalleabatecimiento: AbateciminetoIN
):
    with Session(db_engine) as session:
        nuevo_abastecimiento = RegistroDeAbastecimiento(
            CostoTotal=costo_total,
            IdProveedor=id_proveedor,
            TotalIngresado=total_ingresado,
        )

        session.add(nuevo_abastecimiento)
        session.flush()

        nuevo_detalle_insumo_lista = []

        for insumo in Detalleabatecimiento.listaInsumos:
            nuevo_detalle_insumo_lista.append(
                DetallesRegistroInsumos(
                    IdRegistroAbastecimiento=nuevo_abastecimiento.IdRegistro, IdInsumo= insumo.IdInsumo, TotalIngresado=insumo.TotalIngresado, CostoIndividual=insumo.CostoIndividual
                )
            )
            
        
        nuevo_detalle_ingrediente_lista = []
        for ingrediente in Detalleabatecimiento.listaIngredientes:
            nuevo_detalle_ingrediente_lista.append(
                DetallesRegistroIngredientes(
                    IdRegistroAbastecimiento=nuevo_abastecimiento.IdRegistro,IdIngrediente=ingrediente.IdIngrediente,TotalIngresado=ingrediente.TotalIngresado, CostoIndividual= ingrediente.CostoIndividual
                )
            )
        
        session.add_all(nuevo_detalle_insumo_lista)
        session.add_all(nuevo_detalle_ingrediente_lista)
        session.commit()
        
        return nuevo_abastecimiento


def obtener_detalles_abastecimiento(id_registro: int) -> dict:

    with Session(db_engine) as session:
        query = text("EXEC DetallesAbastIngredientes @IdRegistro = :id_param")
        resultado = session.exec(query, params={"id_param": id_registro})
        json_string = resultado.scalar()
        if not json_string:
            return {"Insumos": [], "Ingredientes": []}

        datos_parseados = json.loads(json_string)
        
        return datos_parseados