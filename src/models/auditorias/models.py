from sqlmodel import Field, SQLModel
import datetime


class Auditoria_Mesas(SQLModel, table=True):
    IdAuditoria_Mesas: int = Field(primary_key=True, index=True)
    IdMesa: int = Field(nullable=False)
    IdOrden: int = Field(foreign_key = "ordenes.IdOrdenes", unique=True)
    HoraEntrada: datetime.datetime = Field(nullable=False)
    HoraSalida: datetime.datetime = Field()

class Auditoria_Comedor(SQLModel, table=True):
    IdAuditoria_Comedor: int = Field(primary_key=True, index=True)  
    Username: str = Field(nullable=False, max_length=150) 
    HoraApertura: datetime.datetime = Field(nullable=False)
    HoraCerrar: datetime.datetime = Field(nullable=False)

class Auditoria_Caja(SQLModel, table=True):
    IdAuditoria_Caja: int = Field(primary_key=True, index=True)
    Username: str = Field(nullable=False, max_length=150)
    HoraApertura: datetime.datetime = Field(nullable=False)
    HoraCerrar: datetime.datetime = Field(nullable=False)
