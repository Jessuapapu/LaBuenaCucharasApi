from sqlmodel import Session
from src.models.insumos.models import Proveedores
from src.models.insumos.types import TipoDeProveedor

def registrar_proveedor(nombre: str, direccion: str, tipo: TipoDeProveedor):
    pass