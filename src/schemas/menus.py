from pydantic import BaseModel
import datetime

class MenuIn(BaseModel):
    day: datetime.date
    nombre_platillo: str
    monto: float


class MenuUpdate(BaseModel):
    nombre_platillo: str
