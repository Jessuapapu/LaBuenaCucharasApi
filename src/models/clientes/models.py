from sqlmodel import Field, SQLModel
from .types import EstadoContrato

class Clientes(SQLModel, table=True):
    IdCliente: int | None = Field(default=None, primary_key=True)
    NombreCliente: str = Field(max_length=100, nullable=False)
    DireccionCliente: str = Field(max_length=150, nullable=False)

class Contrato(SQLModel, table=True):
    IdContrato: int | None = Field(default=None, primary_key=True)
    IdCliente: int = Field(foreign_key="clientes.IdCliente", nullable=False)  # corregido
    Presupuesto: float = Field(nullable=False)
    NumeroContrato: int = Field(nullable=False)
    Estado: EstadoContrato = Field(nullable=False)
    FechaInicio: str = Field(max_length=10, nullable=False)
    FechaVencimiento: str = Field(max_length=10, nullable=True)

class ClienteTelefono(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    IdCliente: int = Field(foreign_key="clientes.IdCliente", nullable=False)  # corregido
    Telefono: str = Field(max_length=20, nullable=False)

class ClienteCorreo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    IdCliente: int = Field(foreign_key="clientes.IdCliente", nullable=False)  # corregido
    CorreoElectronico: str = Field(max_length=100, nullable=False)