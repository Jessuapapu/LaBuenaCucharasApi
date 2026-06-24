from src.models.insumos.models import *
from src.models.platillos.models import *
from src.services.platillos.service import *
from sqlmodel import Session, select, desc
from src.config.database import db_engine

def obtener_ingredientes():
    with Session(db_engine) as session:
        statement = select(Insumos, CategoriasInsumos.NombreCategoriaInsumo).join(CategoriasInsumos).order_by(desc(Insumos.IdInsumo))

        result = session.exec(statement).all()

        if not result:
            return []
        
        ListInsumo = []
        for insumo, categoria in result:
            ListInsumo.append({
                "id_insumo": insumo.IdInsumo,
                'Nombre': insumo.NombreInsumo,
                'categoria': categoria
            })

        return ListInsumo
    
def crear_ingrediente(Nombre: str):
    if not Nombre:
        return False

    with Session(db_engine) as session:
        try:
            nuevo_ingrediente = Ingredientes(NombreIngrediente=Nombre, StockIngredientes= 0)

            session.add(nuevo_ingrediente)

            session.commit()

        except Exception as e:
            session.rollback()
            return e
        
    return True


def actualizar_Ingrediente(IdIngrediente: int, NombreNuevo: str, stock: int):
    if not IdIngrediente or not NombreNuevo:
        return False
    
    with Session(db_engine) as session:
        try:
            statemed = select(Ingredientes).where(Ingredientes.IdIngrediente == IdIngrediente)

            ingrediente = session.exec(statemed).first()

            if not ingrediente:
                return False
            

            ingrediente.NombreIngrediente = NombreNuevo
            ingrediente.StockIngredientes = stock

            session.add(ingrediente)
            session.commit()
            session.refresh(ingrediente)


        except Exception as e:
            session.rollback()
            return e
        
    return True

def obtener_ingrediente(IdIngrediente: int = None, Nombre: str = None):
    if not IdIngrediente and not Nombre:
        return None

    with Session(db_engine) as session:
        try:
            validacion = (Ingredientes.IdIngrediente == IdIngrediente) if IdIngrediente else (Ingredientes.NombreIngrediente == Nombre)
            statemed = select(Ingredientes).where(validacion)

            ingrediente = session.exec(statemed).first()

            return ingrediente
        
        except Exception as e:
            session.rollback()
            return e


def crear_relacion_platillo_ingrediente(listaIngrediente: list[int], IdPlatillo: int | None = None, NombrePlatillo: str | None = None):
    if not IdPlatillo and not NombrePlatillo:
        return False
    

    IdPlatillo = IdPlatillo if IdPlatillo else obtener_platillo_id_por_nombre(NombrePlatillo)

    if not IdPlatillo:
        return False

    with Session(db_engine) as session:
        try:
            listaRelaciones = []

            for id in listaIngrediente:
                if not obtener_ingrediente(IdIngrediente=id):
                    return False

                listaIngrediente.append(PlatillosEIngredientes(IdPlatillo=IdPlatillo,IdIngrediente=id))


            
            session.add_all(listaRelaciones)
            session.commit()
            


        except Exception as e:
            session.rollback()
            return e
    
    return True
    