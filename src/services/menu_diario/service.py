from src.models.platillos.models import MenuDiario, Platillos
from src.models.platillos.types import *
from sqlmodel import Session, select
from src.config.database import db_engine
import os
from src.services.platillos import service
import datetime
from src.services.auditorias.services import registrar_auditoria_platillo
from src.models.auditorias.types import TipoDeAccion
import json
from fastapi.encoders import jsonable_encoder

config_dict: ConfigMenuDiario = ConfigMenuDiario(PlatillosPredefinidosLista={},CambiosDeHora={})

config_json_PATH = './src/services/menu_diario/config_menu.json'

        

def Guardar_json():
    config_dict_serializable = jsonable_encoder(config_dict)
    with open(config_json_PATH, mode='w+') as archivo:
        json.dump(config_dict_serializable,archivo,indent=4)

 
def cargar_json_menu_config():
    if not os.path.exists(config_json_PATH):
        with open(mode="w+",file=config_json_PATH) as archivito:
            pass

        return
    
    with open(mode="r+",file=config_json_PATH) as archivito:
        try:
            global config_dict
            config_dict = ConfigMenuDiario(**json.load(archivito))
        
        except:
            pass

        return
            


def obtener_historial_menu_service():
    with Session(db_engine) as session:
        statement = select(MenuDiario, Platillos).join(Platillos)

        result = session.exec(statement).all()
        if not result:
            return []

        historial = []
        for menu_diario, platillo in result:
            historial.append(
                {
                    "id": menu_diario.IdMenu,
                    "Fecha": menu_diario.Fecha,
                    "NombrePlatillo": platillo.NombrePlatillo,
                    "Monto": menu_diario.Monto
                }
            )

        return historial


def obtener_menu_dia_service(day: datetime.date):
    with Session(db_engine) as session:
        statement = (
            select(MenuDiario, Platillos)
            .join(Platillos)
            .where(MenuDiario.Fecha.day == day)
        )

        result = session.exec(statement).all()
        if result is None:
            return None

        Lista = []
        for menu_diario, platillo in result:

            #if menu_diario.Fecha.hour in config_dict.CambiosDeHora.values()
            Lista.append(
                {
                    "id": menu_diario.IdMenu,
                    "Fecha": menu_diario.Fecha,
                    "NombrePlatillo": platillo.NombrePlatillo,
                    "Monto": menu_diario.Monto,
                    "Hora": menu_diario.Hora
                }
            )

        return Lista
  
def obtener_menu_dia_hoy():
    cargar_json_menu_config()
    day = datetime.datetime.now().date()
    with Session(db_engine) as session:
        statement = (
            select(MenuDiario, Platillos)
            .join(Platillos)
            .where(MenuDiario.Fecha == day)
        )

        result = session.exec(statement).all()
        if result is None:
            return []

        Lista = []
        RangoDeHora: CambioDeHoraModel = None

        if config_dict and len(config_dict.CambiosDeHora.values()) > 0:

            horaActual = datetime.datetime.now().time()
            for cambios in config_dict.CambiosDeHora.values():
                if not cambios.estado:
                    continue

                if horaActual >= cambios.HoraInicio and horaActual < cambios.HoraFinal:
                    RangoDeHora = cambios
                    break
            

        
        for menu_diario, platillo in result:
            if not RangoDeHora or (menu_diario.Hora >= RangoDeHora.HoraInicio and menu_diario.Hora < RangoDeHora.HoraFinal):
                
                Lista.append(
                    {
                        "id": menu_diario.IdMenu,
                        "Fecha": menu_diario.Fecha,
                        "NombrePlatillo": platillo.NombrePlatillo,
                        "Monto": menu_diario.Monto,
                        'Hora': menu_diario.Hora
                    }
                )
        
        for platillo in config_dict.PlatillosPredefinidosLista.values():
            
            if (platillo.Hora >= RangoDeHora.HoraInicio and platillo.Hora < RangoDeHora.HoraFinal) or not RangoDeHora:
                Lista.append(
                    dict(platillo)
                )

        return Lista


def crear_menu_service(day: datetime.date, hora:datetime.time, nombre_platillo: str,monto: float, username: str | None = None):
    id_platillo = service.obtener_platillo_id_por_nombre(nombre_platillo)

    if id_platillo is None:
        raise ValueError("El platillo con el nombre ingresado no existe")

    nuevo_menu = MenuDiario(Fecha=day, IdPlatillo=id_platillo,Monto=monto, Hora=hora)
    with Session(db_engine) as session:
        try:
            session.add(nuevo_menu)
            session.commit()
        except Exception as e:
            session.rollback()
            return e
            
    # Auditoría: creación de menu/platillo en menú diario
    if username and id_platillo is not None:
        try:
            registrar_auditoria_platillo(username, int(id_platillo), TipoDeAccion.CREAR)
        except Exception:
            pass


def editar_menu_service(id_menu, hora:datetime.time, nombre_platillo: str, username: str | None = None):
    id_platillo = service.obtener_platillo_id_por_nombre(nombre_platillo)

    if id_platillo is None:
        raise ValueError("El platillo con el nombre ingresado no existe")

    with Session(db_engine) as session:
        statement = select(MenuDiario).where(MenuDiario.IdMenu == id_menu)
        menu_a_editar = session.exec(statement).first()

        if menu_a_editar is None:
            raise ValueError("No existe el menu con el Id ingresado")

        menu_a_editar.IdPlatillo = id_platillo
        menu_a_editar.Hora = hora

        try:
            session.add(menu_a_editar)
            session.commit()
        except Exception as e:
            session.rollback()
            return e
    # Auditoría: actualización de platillo en menú
    if username and id_platillo is not None:
        try:
            registrar_auditoria_platillo(username, int(id_platillo), TipoDeAccion.ACTUALIZAR)
        except Exception:
            pass


def nuevo_cambio_de_hora(Nombre: str, HoraInicio: datetime.datetime.hour, HoraFinal: datetime.datetime.hour):
    cargar_json_menu_config()
    for cambio in config_dict.CambiosDeHora.values():
        if not cambio.estado:
            continue

        if HoraInicio >= cambio.HoraInicio and HoraFinal < cambio.HoraFinal:
            return False
    
    config_dict.CambiosDeHora[Nombre] = CambioDeHoraModel(nombre=Nombre,HoraInicio=HoraInicio, HoraFinal=HoraFinal)

    Guardar_json()

def editar_cambio_de_hora(
        Nombre: str, NombreNuevo:str = None, HoraInicio: datetime.datetime.hour = None, HoraFinal: datetime.datetime.hour = None,
        Estado: bool = None
        ):
    
    cargar_json_menu_config()

    try:
        for cambios in config_dict.CambiosDeHora.values():
            if not cambios.estado:
                continue
            
            if (cambios.nombre != Nombre and
                ((HoraInicio and (HoraInicio >= cambios.HoraInicio and HoraInicio < cambios.HoraFinal)) or 
                 (HoraFinal and (HoraFinal >= cambios.HoraInicio and HoraFinal < cambios.HoraFinal)))):
                return False
        

        if NombreNuevo:
            config_dict.CambiosDeHora[NombreNuevo] = NombreNuevo
            config_dict.CambiosDeHora[NombreNuevo].HoraInicio = HoraInicio if HoraInicio else config_dict.CambiosDeHora[Nombre].HoraInicio
            config_dict.CambiosDeHora[NombreNuevo].HoraFinal= HoraFinal if HoraFinal else config_dict.CambiosDeHora[Nombre].HoraFinal
            config_dict.CambiosDeHora[NombreNuevo].estado = Estado if Estado else config_dict.CambiosDeHora[Nombre].estado

            config_dict.CambiosDeHora.pop(Nombre)
            Guardar_json()
            return True

        config_dict.CambiosDeHora[Nombre].HoraInicio = HoraInicio if HoraInicio else config_dict.CambiosDeHora[Nombre].HoraInicio
        config_dict.CambiosDeHora[Nombre].HoraFinal = HoraFinal if HoraFinal else config_dict.CambiosDeHora[Nombre].HoraFinal
        config_dict.CambiosDeHora[Nombre].estado = Estado if Estado else config_dict.CambiosDeHora[Nombre].estado
        Guardar_json()
        return True
    

    except:
        return False


def eliminar_cambio_de_hora(Nombre: str):
    cargar_json_menu_config()
    try:
        config_dict.CambiosDeHora.pop(config_dict.CambiosDeHora[Nombre])
        return True
    
    except:
        return False
    
def obtener_cambios_de_hora():
    cargar_json_menu_config()
    listaCambmbiosDeHora = []

    for cambio in config_dict.CambiosDeHora.values():
        listaCambmbiosDeHora.append(cambio)
    
    return listaCambmbiosDeHora

def obtener_cambio_de_hora(Nombre: str):
    cargar_json_menu_config()
    for cambio in config_dict.CambiosDeHora.values():
        if cambio.nombre == Nombre:
            return cambio
        
    return None