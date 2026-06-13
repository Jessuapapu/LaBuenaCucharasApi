from pydantic import BaseModel

class ingrediente(BaseModel):
    NombreIngrediente: str

class PlatilloIngredienteIn(BaseModel):
    IdPLatillo: str
    ingredientes: list[int]
