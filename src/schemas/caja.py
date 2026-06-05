from pydantic import BaseModel
from typing import Optional

class CuentaOrdenIn(BaseModel):
    IdOrden: int
    Monto: float

class PagoIn(BaseModel):
    IdOrden: int
    Monto: float
    Metodo: str
    Referencia: Optional[str] = ""

class ReembolsoIn(BaseModel):
    IdOrden: int
    Monto: float
    Razon: str
    
class ActualizarMontoIn(BaseModel):
    IdOrden: int
    Monto: float