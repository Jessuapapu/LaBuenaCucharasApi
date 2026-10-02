from fastapi import APIRouter, HTTPException, File, UploadFile, Query, Depends
from src.services.imagenes import service as imagenes
from src.security.dependency import obtener_usuario_actual
from src.models.Usuarios.models import Usuario

router = APIRouter(tags=["Imagenes"])

@router.post("/{NombrePlatillo}")
async def crear_imagenes(NombrePlatillo: str, file: UploadFile = File(...), usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    imagen_byte = await file.read()
    
    extension = file.filename.split(".")[-1]    
    FileContent = file.content_type
    
    if not imagenes.subir_imagen(extension=extension, NombrePlatillo=NombrePlatillo, imagen_bytes=imagen_byte, imagen_content=FileContent, username=usuario_actual.username):
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

@router.put("/{NombrePlatillo}/{NumeroImagen}")
async def actualizar_imagen(NombrePlatillo: str, NumeroImagen: int, file: UploadFile = File(...), usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    imagen_byte = await file.read()

    extension = file.filename.split(".")[-1]    
    FileContent = file.content_type

    if not imagenes.actualizar_imagen(NumeroImagen=NumeroImagen,imagen_bytes=imagen_byte,extension=extension,imagen_content=FileContent,NombrePlatillo=NombrePlatillo, username=usuario_actual.username):
        HTTPException(404, {"ERROR AL ACTUALIZAR LA IMAGEN"})
    else:
        return True
    
@router.delete("/{NombrePlatillo}/{NumeroImagen}")
async def eliminar_imagen(NombrePlatillo: str, NumeroImagen: int, usuario_actual: Usuario = Depends(obtener_usuario_actual)):

    if not imagenes.eliminar_imagen(NombrePlatillo=NombrePlatillo, NumeroImagen=NumeroImagen, username=usuario_actual.username):
        HTTPException(404, {"ERROR AL eliminar LA IMAGEN"})
    else:
        return True