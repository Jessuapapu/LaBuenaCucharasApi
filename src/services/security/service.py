from sqlmodel import Session, select
from src.models.Usuarios import Usuario
from src.models.Usuarios.types import Rol
from src.security.security import verificar_password, crear_token_acceso, hashear_password
from src.config.database import db_engine
from sqlmodel import select
import datetime

def autenticar_usuario(username: str, password_plano: str) -> Usuario | None:
    with Session(db_engine) as session:
        statement = select(Usuario).where(Usuario.username == username)
        usuario_bd = session.exec(statement).first()

    if not usuario_bd:
        return None

    if not usuario_bd.activo:
        return None

    if not verificar_password(password_plano, usuario_bd.password_hash):
        return None

    return usuario_bd

def generar_token_para_usuario(usuario: Usuario) -> str:
    """
    Empaqueta los datos del usuario en un token JWT.
    """
    payload = {
        "sub": str(usuario.id),
        "username": usuario.username,
        "rol": usuario.rol.value if hasattr(usuario.rol, 'value') else usuario.rol
    }
    return crear_token_acceso(data=payload)

def registrar_usuario(user: str, contra_plano: str, rol: str, correo: str):
    contra_crifado = hashear_password(contra_plano)
    nuevo_usuario = Usuario(username=user,password_hash=contra_crifado,rol=rol,activo=True,fecha_creacion=datetime.datetime.now(), correo=correo)
    try:
        with Session(db_engine) as session:
            session.add(nuevo_usuario)
            session.commit()
        return True
    
    except:
        return False

def actualizar_usuario(user: str = None, contra_plano: str = None, rol: str = None):
        usuario = None
        try:
            with Session(db_engine) as session:
                statement = select(Usuario).where(Usuario.username == user)
                usuario = session.exec(statement).first()
                if not usuario:
                    return False
                
                usuario.username = user if user else usuario.username
                usuario.rol = rol if rol else usuario.rol
                usuario.password_hash = hashear_password(contra_plano) if contra_plano else usuario.password_hash
                session.add(usuario)
                session.commit()

                session.refresh(usuario)
                return True
            
        except:
            return False
        
def desactivar_usuario(user: str):
    usuario = None
    try:
        with Session(db_engine) as session:
            statement = select(Usuario).where(Usuario.username == user)
            usuario = session.exec(statement).first()
            if not usuario:
                return False
            
            usuario.activo = False
            session.add(usuario)
            session.commit()
            session.refresh(usuario)
            return True
        
    except:
        return False
    
def obtener_todos_usuarios():
    with Session(db_engine) as session:
            statement = select(Usuario)
            usuarios = session.exec(statement).all()
            
            listaUsuarios = []

            for user in usuarios:
                listaUsuarios.append(
                    {

                        "Username": user.username,
                        "fecha_creacion": user.fecha_creacion,
                        "rol": user.rol,
                        "activo": user.activo

                    }
                )

            return listaUsuarios

def validar_rol(usuario: dict, rol: Rol | str, detalle: str):
    if usuario.rol  != rol:
            return True

    return False