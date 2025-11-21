from sqlmodel import Session, create_engine
from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Crear el motor de la base de datos SQL Server usando la URL de la base de datos desde las variables de entorno
if getenv("DATABASE_URL") is None:
    raise ValueError("La variable de entorno DATABASE_URL no está configurada.")

db_engine = create_engine(getenv("DATABASE_URL") or "", echo=True)
