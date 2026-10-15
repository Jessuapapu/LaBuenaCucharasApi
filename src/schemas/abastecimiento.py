from pydantic import BaseModel, Field
from typing import List
from decimal import Decimal

class InsumosIN(BaseModel):
    IdInsumo: int
    TotalIngresado: int
    CostoIndividual: float

class IngredienteIN(BaseModel):
    IdIngrediente: int
    TotalIngresado: int
    CostoIndividual: float 

# Unificamos todo el payload en un solo esquema, estilo PedidoCreateSchema
class AbastecimientoCreateSchema(BaseModel):
    IdProveedor: int = Field(..., description="ID del proveedor")
    CostoTotal: Decimal = Field(..., description="Costo total del abastecimiento")
    TotalIngresado: int = Field(..., description="Suma total de items ingresados")
    # Al igualar a [], permitimos que envíen solo insumos, solo ingredientes, o ambos
    listaInsumos: List[InsumosIN] = []
    listaIngredientes: List[IngredienteIN] = []