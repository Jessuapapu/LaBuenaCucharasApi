from pydantic import BaseModel

class ingrediente(BaseModel):
    NombreIngrediente: str
    Stock: int 

class PlatilloIngredienteIn(BaseModel):
    IdPLatillo: str
    ingredientes: list[int]
