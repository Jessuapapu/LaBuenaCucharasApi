from sqlmodel import Field, SQLModel
import datetime
from .types import AccionImagenes

class ImagenesPlatillos(SQLModel, table=True):
    IdImagen: int = Field(primary_key=True, index=True)
    UrlImagen: str = Field(nullable=False)
    IdPlatillo: int = Field(foreign_key="platillos.IdPlatillo")
