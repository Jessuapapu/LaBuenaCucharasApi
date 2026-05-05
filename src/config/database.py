from sqlmodel import create_engine
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
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password}"
    f";Trusted_Connection=yes"
)
# Encode for SQLAlchemy
connection_uri = f"mssql+pyodbc:///?odbc_connect={parse.quote_plus(connection_string)}"

db_engine = create_engine(connection_uri, echo=True)
