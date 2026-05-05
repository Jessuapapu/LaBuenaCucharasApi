from src.models.comedor import models as comedor
from sqlmodel import Session, select
from src.config.database import db_engine
from src.routes import menu_diario
import datetime

