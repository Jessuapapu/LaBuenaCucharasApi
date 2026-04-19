from sqlmodel import Field, SQLModel
from .types import EstadoContrato
import datetime

class Clientes(SQLModel, table=True):
    IdCliente: int | None = Field(default=None, primary_key=True)
    NombreCliente: str = Field(max_length=100, nullable=False)

class Contrato(SQLModel, table=True):
    IdContrato: int | None = Field(default=None, primary_key=True)
    IdCliente: int = Field(foreign_key="clientes.IdCliente", nullable=False)
    Presupuesto: float = Field(nullable=False)
    NumeroContrato: int = Field(nullable=False)
    Estado: EstadoContrato = Field(nullable=False)
    FechaInicio: datetime.datetime = Field(nullable=False)
    FechaVencimiento: datetime.datetime = Field(nullable=True)

class ClienteTelefono(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    IdCliente: int = Field(foreign_key="clientes.IdCliente", nullable=False)
    Telefono: str = Field(max_length=20, nullable=False)

class ClienteCorreo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    IdCliente: int = Field(foreign_key="clientes.IdCliente", nullable=False)
    CorreoElectronico: str = Field(max_length=100, nullable=False)

class ClienteDireccion(SQLModel,table=True):
    id: int | None = Field(default=None, primary_key=True)
    IdCliente: int = Field(foreign_key="clientes.IdCliente", nullable=False)
    Dirreccion: str = Field(max_length=100, nullable=False)