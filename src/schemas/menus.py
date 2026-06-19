from pydantic import BaseModel
import datetime

class MenuIn(BaseModel):
    day: datetime.date
    nombre_platillo: str
    monto: float
    hora: datetime.time


class MenuUpdate(BaseModel):
    nombre_platillo: str
