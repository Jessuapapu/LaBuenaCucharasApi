from sqlmodel import Session, create_engine
from dotenv import load_dotenv
import os
from urllib import parse

load_dotenv()

# Read variables
server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

connection_string = (
    f"DRIVER={{{driver}}};"  # NOTA: DOBLE LLAVE para ODBC
    f"SERVER={server},{os.getenv('DB_PORT', '1433')};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password}"
)

# Encode for SQLAlchemy
connection_uri = (
    f"mssql+pyodbc://{username}:{password}@{server}:1433/{database}?"
    f"driver={parse.quote_plus(driver)}"
)

db_engine = create_engine(connection_uri, echo=True)
