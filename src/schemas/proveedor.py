from pydantic import BaseModel, Field
from typing import Optional

# Asegúrate de importar tu Enum TipoDeProveedor desde donde lo tengas definido
from src.models.types import TipoDeProveedor 

class ProveedorIn(BaseModel):
    NombreProveedor: str = Field(..., max_length=150, description="Nombre comercial o legal del proveedor")
    Direccion: Optional[str] = Field(default=None, description="Dirección física del proveedor")
    Tipo: TipoDeProveedor = Field(..., description="Categoría o tipo de proveedor")

class ProveedorUpdate(BaseModel):
    # Todos los campos son opcionales para permitir actualizaciones parciales (PATCH)
    NombreProveedor: Optional[str] = Field(default=None, max_length=150)
    Direccion: Optional[str] = Field(default=None)
    Tipo: Optional[TipoDeProveedor] = Field(default=None)