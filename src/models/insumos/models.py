from sqlmodel import Field, SQLModel
from .types import PrioridadInsumo
import datetime
import decimal

class Insumos(SQLModel, table=True):
    IdInsumo: int | None = Field(default=None, primary_key=True)
    IdCategoriaInsumo: int | None = Field(default=None, foreign_key="categoriasinsumos.IdCategoriaInsumo")
    NombreInsumo: str = Field(max_length= 200, nullable=False)             
    Prioridad: PrioridadInsumo 

class CategoriasInsumos(SQLModel, table=True):
    IdCategoriaInsumo: int | None = Field(default=None, primary_key=True)
    NombreCategoriaInsumo: str = Field(max_length= 150, nullable=False)

class DetallesRegistroInsumos(SQLModel, table=True):
    IdRegistroAbastecimiento: int | None = Field(default=None, foreign_key="registrodeabastecimiento.IdRegistro", primary_key=True)
    IdInsumo: int | None = Field(default=None, foreign_key="insumos.IdInsumo", primary_key=True)
    TotalIngresado: int = Field(nullable=False)
    CostoIndividual: decimal.Decimal = Field(nullable=False)
