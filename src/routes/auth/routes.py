from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.services.security import service as auth_service
from src.security.dependency import obtener_usuario_actual
from src.models.Usuarios import Usuario
from src.schemas.usuarios import UsuarioSchema

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
):
    
    usuario_autenticado = auth_service.autenticar_usuario(
        username=form_data.username,
        password_plano=form_data.password
    )
    
    if not usuario_autenticado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    
    token = auth_service.generar_token_para_usuario(usuario_autenticado)
    
    return {
        "access_token": token, 
        "token_type": "bearer",
        "user_info": {
            "username": usuario_autenticado.username,
            "rol": usuario_autenticado.rol
        }
    }

@router.get("/me")
async def verificar_perfil_actual(usuario_actual: Usuario = Depends(obtener_usuario_actual)):
    """
    Ruta protegida de utilidad. Permite al frontend verificar 
    en cualquier momento si el token almacenado sigue activo y es válido.
    """
    return {
        "id": usuario_actual.id,
        "username": usuario_actual.username,
        "rol": usuario_actual.rol,
        "activo": usuario_actual.activo
    }


@router.post("/")
async def agregar_usuario(payload: UsuarioSchema, usuario_actual: dict = Depends(obtener_usuario_actual)):
    if usuario_actual.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes los permisos de administrador requeridos para esta acción."
        )
    
    nuevo_usuario = auth_service.registrar_usuario(user=payload.user, contra_plano=payload.contra_plano, rol=payload.rol)
    return nuevo_usuario

@router.get("/")
async def obtener_usuarios():
    return auth_service.obtener_todos_usuarios()

@router.put("/")
async def agregar_usuario(payload: UsuarioSchema, usuario_actual: dict = Depends(obtener_usuario_actual)):
    if usuario_actual.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes los permisos de administrador requeridos para esta acción."
        )
    
    nuevo_usuario = auth_service.registrar_usuario(user=payload.user, contra_plano=payload.contra_plano, rol=payload.rol)
    return nuevo_usuario

@router.put("/actualizar")
async def actualizar_usuario(payload: UsuarioSchema, usuario_actual: dict = Depends(obtener_usuario_actual)):
    if usuario_actual.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes los permisos de administrador requeridos para esta acción."
        )
    
    nuevo_usuario = auth_service.actualizar_usuario(user=payload.user, contra_plano=payload.contra_plano, rol=payload.rol)
    return nuevo_usuario

@router.put("/desactivar")
async def desactivar_usuario(payload: UsuarioSchema, usuario_actual: dict = Depends(obtener_usuario_actual)):
    if usuario_actual.get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes los permisos de administrador requeridos para esta acción."
        )
    
    nuevo_usuario = auth_service.desactivar_usuario(user=payload.user)
    return nuevo_usuario