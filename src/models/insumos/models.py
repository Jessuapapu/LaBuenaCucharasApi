from sqlmodel import Field, SQLModel
from .types import PrioridadInsumo
import datetime
import decimal

class Insumos(SQLModel, table=True):
    IdInsumo: int | None = Field(default=None, primary_key=True)
    NombreInsumo: str = Field(max_length= 200, nullable=False)   
    Stock: int = Field(nullable=False)          
    Prioridad: PrioridadInsumo 

class DetallesRegistroInsumos(SQLModel, table=True):
    IdRegistroAbastecimiento: int | None = Field(default=None, foreign_key="registrodeabastecimiento.IdRegistro", primary_key=True)
    IdInsumo: int | None = Field(default=None, foreign_key="insumos.IdInsumo", primary_key=True)
    TotalIngresado: int = Field(nullable=False)
    CostoIndividual: decimal.Decimal = Field(nullable=False)
