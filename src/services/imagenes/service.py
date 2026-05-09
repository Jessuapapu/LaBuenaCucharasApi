from src.config.imagebase import ApiSupebase
from src.config.database import db_engine
from src.models.imagenes import models as imagenes
from src.services.platillos import service as PlatillosServices
from sqlmodel import Session, text
import json

from fastapi import UploadFile

CantidadPlatillo = {}
Platillo_JSON_path = "./src/services/imagenes/platillos_imagenes.json"

def cargar_en_json(IdPlatillo: int | None = None):
    with open(mode="w+",file="./platillos_imagenes.json") as archivito:
        
        with Session(db_engine) as session:
            parametros = {
            "idplatillo": IdPlatillo
            }
            statement = text("EXEC MostrarCantidadDeImagenes @IdPlatillo = :idplatillo")

            resultados = session.exec(statement, params=parametros).all()

            for row in resultados:
                CantidadPlatillo[str(row.IdPlatillo)] = int(row.CANTIDAD_IMAGENES)
        
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

def subir_imagen(extension: str, NombrePlatillo:str, imagen_bytes: bytes, imagen_content):
    if not CantidadPlatillo.keys():
        cargar_json_platillos()

    print(CantidadPlatillo)
    try:
        IdPlatillo = PlatillosServices.obtener_platillo_id_por_nombre(NombrePlatillo)
        NumeroDeImagen = CantidadPlatillo[str(IdPlatillo)]
        
    
        NombreDeArchivo = f"{NombrePlatillo}{NumeroDeImagen}.{extension}"
        ApiSupebase.storage.from_("Platillos").upload(file=imagen_bytes, path=NombreDeArchivo, file_options={"content-type": imagen_content})
        url_publica = ApiSupebase.storage.from_("Platillos").get_public_url(NombreDeArchivo)
        
        nueva_imagen = imagenes.ImagenesPlatillos(IdPlatillo=IdPlatillo,UrlImagen=url_publica)
        with Session(db_engine) as session:
            session.add(nueva_imagen)
            session.commit()
        
        if str(IdPlatillo) in CantidadPlatillo.keys():
            CantidadPlatillo[str(IdPlatillo)] += 1
        else: 
            CantidadPlatillo[str(IdPlatillo)] = 1
        Guardar_json()
        return True

    except Exception as e:
        print(e)
        return False    