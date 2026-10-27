from pydantic import BaseModel, Field
from typing import Optional

class InsumoCreateSchema(BaseModel):
    NombreInsumo: str = Field(..., max_length=200, description="Nombre del insumo")
    Stock: int = Field(default=0, description="Cantidad actual en stock")
    Prioridad: str = Field(..., description="Prioridad del insumo")

class InsumoUpdateSchema(BaseModel):
    NombreInsumo: Optional[str] = Field(None, max_length=200, description="Nombre del insumo")
    Stock: Optional[int] = Field(None, description="Cantidad actual en stock")
    Prioridad: Optional[str] = Field(None, description="Prioridad del insumo")