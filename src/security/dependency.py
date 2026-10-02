from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlmodel import Session, select
from src.config.database import db_engine
from src.models.Usuarios import Usuario
from .security import SECRET_KEY, ALGORITHM

# Esto le dice a FastAPI dónde está el endpoint para loguearse (para la documentación Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),

) -> Usuario:
    credenciales_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
    #Decodificamos el token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: str = payload.get("sub")
        if usuario_id is None:
            raise credenciales_exception

    except jwt.PyJWTError as e:
        raise credenciales_exception
    
    # Consulta directa a la base de datos usando SQLModel por ID
    with Session(db_engine) as session:
        statement = select(Usuario).where(Usuario.id == usuario_id)
        usuario = session.exec(statement).first()

    
    # Si el token es válido pero el usuario ya no existe en la BD
    if usuario is None:
        raise credenciales_exception
        
    # Verificación de seguridad: si el empleado fue desactivado, bloqueamos el acceso inmediatamente
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario deshabilitado o inactivo"
        )
        
    return usuario

# Fábrica de dependencias para verificar cualquier rol
class RequireRole:
    def __init__(self, roles_permitidos: list[str]):
        self.roles_permitidos = roles_permitidos

    def __call__(self, usuario: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
        # Ahora verificamos el rol directamente sobre la entidad Usuario de la base de datos
        if usuario.rol not in self.roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operación no permitida para tu rol"
            )
        return usuario