from datetime import date
from sqlmodel import Field, SQLModel
from .types import PrioridadInsumo, TipoDeProveedor

class Insumos(SQLModel, table=True):
    IdInsumo: int | None = Field(default=None, primary_key=True)
    IdCategoriaInsumo: int | None = Field(default=None, foreign_key="categoriasinsumos.IdCategoriaInsumo")
    NombreInsumo: str = Field(index=True)
    Prioridad: PrioridadInsumo

class Proveedores(SQLModel, table=True):
    IdProveedor: int | None = Field(default=None, primary_key=True)
    NombreProveedor: str = Field(index=True)
    Direccion: str | None = Field(default=None)
    Tipo: TipoDeProveedor

class CategoriasInsumos(SQLModel, table=True):
    IdCategoriaInsumo: int | None = Field(default=None, primary_key=True)
    NombreCategoriaInsumo: str = Field(index=True)

class RegistroDeAbastecimiento(SQLModel, table=True):
    IdRegistro: int | None = Field(default=None, primary_key=True)
    IdInsumo: int | None = Field(default=None, foreign_key="insumos.IdInsumo")
    IdProveedor: int | None = Field(default=None, foreign_key="proveedores.IdProveedor")
    Cantidad: int = Field(nullable=False)
    FechaAbastecimiento: date = Field(default=date.today())

class DetallesRegistroInsumos(SQLModel, table=True):
    IdRegistroAbastecimiento: int | None = Field(default=None, foreign_key="registrodeabastecimiento.IdRegistro", primary_key=True)
    IdInsumo: int | None = Field(default=None, foreign_key="insumos.IdInsumo", primary_key=True)
    TotalIngresado: int = Field(nullable=False)
    CostoIndividual: float