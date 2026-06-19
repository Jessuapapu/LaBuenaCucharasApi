from sqlalchemy import null, true
from sqlmodel import Field, SQLModel
import datetime
import decimal

class Platillos(SQLModel, table=True):
    IdPlatillo: int | None = Field(default=None, primary_key=True)
    NombrePlatillo: str = Field(nullable=False)


class MenuDiario(SQLModel, table=True):
    IdMenu: int | None = Field(default=None, primary_key=True)
    IdPlatillo: int = Field(
        default=None, nullable=None, index=True, foreign_key="platillos.IdPlatillo"
    )
    Fecha: datetime.date = Field(nullable=False)
    Monto: int = Field(nullable=False, default=0)
    Hora: datetime.time = Field()



class CategoriaPlatillos(SQLModel, table=True):
    Id: int = Field(default=None, primary_key=True)
    IdPlatillo: int | None = Field(default=None, foreign_key="platillos.IdPlatillo")
    IdCatalogoPlatillo: int = Field(
        index=True, nullable=False, foreign_key="catalogoplatillos.IdCatalogoPlatillo"
    )

class CatalogoPlatillos(SQLModel, table=True):
    IdCatalogoPlatillo: int | None = Field(default=None, primary_key=True)
    NombreCatalogoPlatillo: str = Field(nullable=False)

class PlatillosEIngredientes(SQLModel, table=True):
    IdRelacion: int = Field(primary_key=True)
    IdPlatillo: int | None = Field(default=None, foreign_key="platillos.IdPlatillo")
    IdIngrediente: int | None = Field(default=None, foreign_key="ingredientes.IdIngrediente")

