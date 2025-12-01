from sqlalchemy import null, true
from sqlmodel import Field, SQLModel
import datetime
import decimal

class Platillos(SQLModel, table=True):
    IdPlatillo: int | None = Field(default=None, primary_key=True)
    NombrePlatillo: str = Field(nullable=False)

class Ingredientes(SQLModel, table=True):
    IdIngrediente: int | None = Field(default=None, primary_key=True)
    NombreIngrediente: str = Field(nullable=False)
    StockIngredientes: int = Field(nullable=False)

class MenuDiario(SQLModel, table=True):
    IdMenu: int | None = Field(default=None, primary_key=True)
    IdPlatillo: int = Field(
        default=None, nullable=None, index=True, foreign_key="platillos.IdPlatillo"
    )
    FechaMenu: datetime.datetime = Field(nullable=False)

class CategoriaPlatillos(SQLModel, table=True):
    Id: int = Field(default=None, primary_key=True)
    IdPlatillo: int | None = Field(default=None, foreign_key="platillos.IdPlatillo")
    IdCatalogoPlatillo: int = Field(
        index=True, nullable=False, foreign_key="catalogoplatillos.IdCatalogoPlatillo"
    )

class CatalogoPlatillos(SQLModel, table=True):
    IdCatalogoPlatillo: int | None = Field(default=None, primary_key=True)
    NombreCatalogoPlatillo: str = Field(nullable=False)

class PlatillosIngredientes(SQLModel, table=True):
    IdPlatillo: int | None = Field(default=None, foreign_key="platillos.IdPlatillo", primary_key=True)
    IdIngrediente: int | None = Field(default=None, foreign_key="ingredientes.IdIngrediente", primary_key=True)

class DetallesRegistroIngredientes(SQLModel, table=True):
    IdRegistroAbastecimiento: int | None = Field(default=None, foreign_key="registrodeabastecimiento.IdRegistro", primary_key=True)
    IdIngrediente: int | None = Field(default=None, foreign_key="ingredientes.IdIngrediente", primary_key=True)
    TotalIngresado: int = Field(nullable=False)
    CostoIndividual: decimal.Decimal
