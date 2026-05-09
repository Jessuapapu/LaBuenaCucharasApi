from sqlmodel import Field, SQLModel
import datetime
from .types import AccionImagenes

class ImagenesPlatillos(SQLModel, table=True):
    IdImagen: int = Field(primary_key=True, index=True)
    UrlImagen: str = Field(nullable=False)
    IdPlatillo: int = Field(foreign_key="platillos.IdPlatillo")

class auditoriaImagenes(SQLModel, table=True):
    IDAU_imagenes: int = Field(primary_key=True)
    fecha: datetime.datetime = Field(default=datetime.datetime.now())
    accion: AccionImagenes = Field(nullable=False)