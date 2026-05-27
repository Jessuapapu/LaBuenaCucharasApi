from pydantic import BaseModel
import datetime
from src.models.clientes.types import EstadoContrato

class ClientesIn(BaseModel):
    nombre: str
    direccion: str
    telefono: str
    correo: str


class ContratosIn(BaseModel):
    nombre_cliente: str
    numero_contrato: int
    fecha_inicio: datetime.datetime
    fecha_fin: datetime.datetime
    presupuesto: float


class ContratoUpdateEstadoIn(BaseModel):
    nuevo_estado: EstadoContrato
