from sqlmodel import Field, SQLModel
from .types import PrioridadInsumo, TipoDeProveedor
import datetime
import decimal

class Insumos(SQLModel, table=True):
    IdInsumo: int | None = Field(default=None, primary_key=True)
    IdCategoriaInsumo: int | None = Field(default=None, foreign_key="categoriasinsumos.IdCategoriaInsumo")
    NombreInsumo: str = Field()
    Prioridad: PrioridadInsumo

class Proveedores(SQLModel, table=True):
    IdProveedor: int | None = Field(default=None, primary_key=True)
    NombreProveedor: str = Field()
    Direccion: str | None = Field(default=None)
    Tipo: TipoDeProveedor

class CategoriasInsumos(SQLModel, table=True):
    IdCategoriaInsumo: int | None = Field(default=None, primary_key=True)
    NombreCategoriaInsumo: str = Field()

class RegistroDeAbastecimiento(SQLModel, table=True):
    IdRegistro: int | None = Field(default=None, primary_key=True)
    TotalIngresado: int = Field(default=None, nullable=False)
    IdProveedor: int | None = Field(default=None, foreign_key="proveedores.IdProveedor")
    CostoTotal: decimal.Decimal = Field(nullable=False)
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())

class DetallesRegistroInsumos(SQLModel, table=True):
    IdRegistroAbastecimiento: int | None = Field(default=None, foreign_key="registrodeabastecimiento.IdRegistro", primary_key=True)
    IdInsumo: int | None = Field(default=None, foreign_key="insumos.IdInsumo", primary_key=True)
    TotalIngresado: int = Field(nullable=False)
    CostoIndividual: decimal.Decimal
