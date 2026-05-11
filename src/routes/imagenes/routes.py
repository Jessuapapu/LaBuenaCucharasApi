from fastapi import APIRouter, HTTPException, File, UploadFile, Query
from src.services.imagenes import service as imagenes
import datetime

router = APIRouter()

@router.post("/{NombrePlatillo}")
async def crear_imagenes(NombrePlatillo: str, file: UploadFile = File(...)):
    imagen_byte = await file.read()

    extension = file.filename.split(".")[-1]    
    FileContent = file.content_type
    
    if not imagenes.subir_imagen(extension=extension, NombrePlatillo=NombrePlatillo, imagen_bytes=imagen_byte, imagen_content=FileContent):
        HTTPException(500, {"ERROR AL CREAR IMAGEN"})
    else:
        return True
    

@router.get("/")
async def obtener_imagen(
    IdPlatillo: str = Query(description="Buscar por Id de platillo", default= None), 
    NombrePlatillo: str = Query(default= None, description="Buscar por nombre de platillo"),
    NumeroImagen: int = Query(default= 1, description="Numero de imagen")
    ):
    return imagenes.obtener_imagen(NombrePlatillo=NombrePlatillo,NumeroImagen=NumeroImagen,IdPlatillo=IdPlatillo)