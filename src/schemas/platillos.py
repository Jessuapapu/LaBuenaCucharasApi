from pydantic import BaseModel

class PlatilloIn(BaseModel):
    nombre_platillo: str
    nombre_categoria: str


class CategoriaIn(BaseModel):
    nombre_categoria: str