from enum import Enum

class AccionImagenes(str, Enum):
    CREADO    = "CREADO"
    ELIMINAR  = "ELIMINAR"
    MODIFICAR = "MODIFICAR"
    