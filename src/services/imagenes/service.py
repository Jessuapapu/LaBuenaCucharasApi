from src.config.imagebase import ApiSupebase
from src.config.database import db_engine
from src.models.imagenes.models import *
from src.services.platillos import service as PlatillosServices
from sqlmodel import Session, text, select
import json



CantidadPlatillo = {}
Platillo_JSON_path = "./src/services/imagenes/platillos_imagenes.json"

def cargar_en_json(IdPlatillo: int | None = None):
    with open(mode="w+",file=Platillo_JSON_path) as archivito:
        
        with Session(db_engine) as session:
            parametros = {
            "idplatillo": IdPlatillo
            }
            statement = text("EXEC MostrarCantidadDeImagenes @IdPlatillo = :idplatillo")

            resultados = session.exec(statement, params=parametros).all()

            for row in resultados:
                CantidadPlatillo[str(row.IdPlatillo)] = {
                    "CANTIDAD": int(row.CANTIDAD_IMAGENES),
                    "NOMBRE": row.NombrePlatillo
                    }
        
        json.dump(CantidadPlatillo,archivito,indent=4)
        

def Guardar_json():
    with open(Platillo_JSON_path, 'w') as archivo:
        json.dump(CantidadPlatillo,archivo,indent=4)

def cargar_json_platillos():
    with open(mode="w+",file=Platillo_JSON_path) as archivito:
        try:
            global CantidadPlatillo
            CantidadPlatillo = json.load(archivito)
        except:
            cargar_en_json()



def subir_imagen(extension: str, NombrePlatillo:str, imagen_bytes: bytes, imagen_content: str, NumeroImagen: int | None = 0, username: str | None = None):
    if not CantidadPlatillo.keys():
        cargar_json_platillos()

    #try:
    IdPlatillo = PlatillosServices.obtener_platillo_id_por_nombre(NombrePlatillo)
    if not IdPlatillo:
        return False
    
    NumeroDeImagen = CantidadPlatillo[str(IdPlatillo)]["CANTIDAD"] if NumeroImagen == 0 else NumeroImagen
    NombreDeArchivo = f"{NombrePlatillo}{NumeroDeImagen}.{extension}"
    ApiSupebase.storage.from_("Platillos").upload(file=imagen_bytes, path=NombreDeArchivo, file_options={"content-type": imagen_content})
    url_publica = ApiSupebase.storage.from_("Platillos").get_public_url(NombreDeArchivo)

    nueva_imagen = ImagenesPlatillos(IdPlatillo=IdPlatillo,UrlImagen=url_publica)
    with Session(db_engine) as session:
        session.add(nueva_imagen)
        session.commit()
    CantidadPlatillo[str(IdPlatillo)]["CANTIDAD"] += 1 if not NumeroImagen else 0
    Guardar_json()

        
    return True

    #except Exception as e:
    #    print(e)
    #    return False    
    
def obtener_imagen(NumeroImagen: int, IdPlatillo: int | None = None, NombrePlatillo: str | None = None) -> str | None: 
    if not IdPlatillo and not NombrePlatillo:
        return None
    
    Idplato = IdPlatillo if IdPlatillo else PlatillosServices.obtener_platillo_id_por_nombre(NombrePlatillo)
    
    if not Idplato:
        return None

    if not CantidadPlatillo.keys():
        cargar_json_platillos()
    
    with Session(db_engine) as session:
        Imagenes = select(
            ImagenesPlatillos.UrlImagen
        ).select_from(ImagenesPlatillos).where(ImagenesPlatillos.IdPlatillo == Idplato)
        
        query = session.exec(Imagenes).all()

        try:
            NombrePlato: str = CantidadPlatillo[str(Idplato)]["NOMBRE"]
        except:
            return None
        
        patron = rf"{NombrePlato.replace(" ","%20")}{NumeroImagen}."

        for UrlImagen in query:
            if patron.lower() in UrlImagen.lower():
                return UrlImagen

        # Si no encuentra el link desde la base de datos
        ListaDeArchivos = ApiSupebase.storage.from_("Platillos").list()
        for Archivo in ListaDeArchivos:
            if patron.replace("%20"," ").lower() in Archivo['name'].lower():
                url_publica = ApiSupebase.storage.from_("Platillos").get_public_url(Archivo['name'])
                nueva_imagen = ImagenesPlatillos(IdPlatillo=Idplato,UrlImagen=url_publica)
                session.add(nueva_imagen)
                session.commit()

                CantidadPlatillo[str(IdPlatillo)]["CANTIDAD"] += 1
                Guardar_json()
                return url_publica
    
    return None

def actualizar_imagen(
    NumeroImagen: int, imagen_bytes: bytes, extension: str, imagen_content: str,
    IdPlatillo: int | None = None, NombrePlatillo: str | None = None, username: str | None = None,
    ):
    if not CantidadPlatillo.keys():
        cargar_json_platillos()
    

    if not IdPlatillo and not NombrePlatillo:
        return False

    Idplato = IdPlatillo if IdPlatillo else PlatillosServices.obtener_platillo_id_por_nombre(NombrePlatillo)
    
    if not Idplato:
        return False
    
    if not eliminar_imagen(IdPlatillo=Idplato, NumeroImagen=NumeroImagen):
        return False
    
    if not subir_imagen(imagen_bytes = imagen_bytes, extension= extension, imagen_content= imagen_content, NombrePlatillo=CantidadPlatillo[str(Idplato)]["NOMBRE"], NumeroImagen=NumeroImagen, username=username):
        return True


    
    return True


def eliminar_imagen(NumeroImagen: int, IdPlatillo: int | None = None, NombrePlatillo: str | None = None, username: str | None = None):
    if not IdPlatillo and not NombrePlatillo:
        return None
    
    if not CantidadPlatillo.keys():
        cargar_json_platillos()
    

    Idplato = IdPlatillo if IdPlatillo else PlatillosServices.obtener_platillo_id_por_nombre(NombrePlatillo)
    
    if not Idplato:
        return None
    
    ListaDeArchivos = ApiSupebase.storage.from_("Platillos").list()
    NombrePlato: str = rf"{CantidadPlatillo[str(Idplato)]["NOMBRE"]}{NumeroImagen}."

    for archivo in ListaDeArchivos:
        if NombrePlato in archivo['name']:
            if not ApiSupebase.storage.from_("Platillos").remove(archivo['name']):
                return False



    return True