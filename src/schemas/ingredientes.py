from pydantic import BaseModel, Field
from typing import Optional

class IngredienteCreateSchema(BaseModel):
    NombreIngrediente: str = Field(..., max_length=150, description="Nombre del ingrediente")
    StockIngredientes: int = Field(default=0, description="Cantidad actual en stock global")
    # Datos que irán al JSON
    VidaUtilSemanas: int = Field(..., gt=0, description="Tiempo de vida aprox. en semanas")
    ConsumoSemanalAprox: int = Field(..., gt=0, description="Consumo aprox. por semana")

class IngredienteUpdateSchema(BaseModel):
    NombreIngrediente: Optional[str] = Field(None, max_length=150)
    StockIngredientes: Optional[int] = Field(None)
    VidaUtilSemanas: Optional[int] = Field(None, gt=0)
    ConsumoSemanalAprox: Optional[int] = Field(None, gt=0)