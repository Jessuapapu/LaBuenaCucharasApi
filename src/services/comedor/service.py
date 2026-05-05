from src.models import MenuDiario, Platillos, platillos
from sqlmodel import Session, select
from src.config.database import db_engine
from src.routes import menu_diario
import datetime


def 