from pydantic import BaseModel

class AbateciminetoIN(BaseModel):
    listaInsumos: list[InsumosIN]
    listaIngredientes: list[IngredienteIN]

class InsumosIN(BaseModel):
    IdInsumo: int
    TotalIngresado: int
    CostoIndividual: float

class IngredienteIN(BaseModel):
    IdIngrediente: int
    TotalIngresado: int
    CostoIndividual: float    