from pydantic import BaseModel
import datetime

class ConfigMenuDiario(BaseModel):
    CambiosDeHora: dict[str,CambioDeHoraModel]
    PlatillosPredefinidosLista: dict[int,PlatillosPredefinidos]

class CambioDeHoraModel(BaseModel):
    nombre: str
    HoraInicio: datetime.time
    HoraFinal: datetime.time
    estado: bool = True

class PlatillosPredefinidos(BaseModel):
    id: int
    NombrePlatillo: str
    Precio: float
    Hora: datetime.time

class CambioDeHoraModelEditar(CambioDeHoraModel):
    nombreNuevo: str = None