from sqlmodel import Field, SQLModel

class Ingredientes(SQLModel, table=True):
    IdIngrediente: int | None = Field(default=None, primary_key=True)
    NombreIngrediente: str = Field(nullable=False, max_length=150)
    StockIngredientes: int = Field(nullable=False)
