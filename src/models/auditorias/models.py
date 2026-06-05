from sqlmodel import Field, SQLModel
from .types import TipoDeAccion
import datetime


class Auditoria_Mesas(SQLModel, table=True):
    IdAuditoria_Mesas: int = Field(primary_key=True, index=True)
    IdMesa: int = Field(nullable=False)
    IdOrden: int = Field(foreign_key = "ordenes.IdOrdenes", unique=True)
    HoraEntrada: datetime.datetime = Field(nullable=False)
    HoraSalida: datetime.datetime = Field()

class Auditoria_Comedor(SQLModel, table=True):
    IdAuditoria_Comedor: int = Field(primary_key=True, index=True)  
    Username: str = Field(nullable=False) 
    HoraApertura: datetime.datetime = Field(nullable=False)
    HoraCerrar: datetime.datetime = Field(nullable=False)

class Auditoria_Usuario(SQLModel, table = True):
    IdAuditoria_Usuario: int = Field(primary_key=True, index=True)
    Username: str = Field(nullable=False)
    IdUsuarioCreado: int = Field(foreign_key= "usuario.id")
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())
    TipoAccion: TipoDeAccion = Field(nullable=False)

class Auditoria_Facturas(SQLModel, table = True):
    IdAuditoria_Facturas: int = Field(primary_key=True, index=True)
    Username: str = Field(nullable=False)
    IdFactura: int = Field(foreign_key= "facturas.IdFactura")
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())
    TipoAccion: TipoDeAccion = Field(nullable=False)

class Auditoria_Ordenes(SQLModel, table = True):
    IdAuditoria_Ordenes: int = Field(primary_key=True, index=True)
    Username: str = Field(nullable=False)
    IdOrden: int = Field(foreign_key= "ordenes.IdOrdenes")
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())
    TipoAccion: TipoDeAccion = Field(nullable=False)

class Auditoria_Pedidos(SQLModel, table = True):
    IdAuditoria_Pedidos: int = Field(primary_key=True, index=True)
    Username: str = Field(nullable=False)
    IdPedido: int = Field(foreign_key= "pedidos.IdPedido")
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())
    TipoAccion: TipoDeAccion = Field(nullable=False)

class Auditoria_Imagenes(SQLModel, table=True):
    IdAuditoria_Imagenes: int = Field(primary_key=True, index=True)
    Username: str = Field(nullable=False)
    IdImagen: int = Field()
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())
    TipoAccion: TipoDeAccion = Field(nullable=False)

class Auditoria_Platillos(SQLModel, table=True):
    IdAuditoria_Platillos: int = Field(primary_key=True, index=True)
    Username: str = Field(nullable=False)
    IdPlatillo: int = Field(foreign_key='platillos.IdPlatillo')
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())
    TipoAccion: TipoDeAccion = Field(nullable=False)

class Auditoria_Cliente(SQLModel, table=True):
    IdAuditoria_Clientes: int = Field(primary_key=True, index=True)
    Username: str = Field(nullable=False)
    IdCliente: int = Field(foreign_key='clientes.IdCliente')
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())
    TipoAccion: TipoDeAccion = Field(nullable=False)

class Auditoria_Pagos(SQLModel, table=True):
    IdAuditoria_Pagos: int = Field(primary_key=True, index=True)
    Username: str = Field(nullable=False)
    IdPago: int = Field(foreign_key='pago.IdPago')
    Fecha: datetime.datetime = Field(default=datetime.datetime.now())
    TipoAccion: TipoDeAccion = Field(nullable=False)

class Auditoria_Caja(SQLModel, table=True):
    IdAuditoria_Caja: int = Field(primary_key=True, index=True)
    Username: str = Field(nullable=False)
    HoraApertura: datetime.datetime = Field(nullable=False)
    HoraCerrar: datetime.datetime = Field(nullable=False)

class Auditoria_Transaciones(SQLModel, table=True):
    IdAuditoria_Transaciones: int = Field(primary_key=True, index=True)
    Username: str = Field(nullable=False)
    IdPago: int = Field(foreign_key='pago.IdPago')
    