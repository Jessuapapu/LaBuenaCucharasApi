from enum import Enum

class TipoDeAccion(Enum):
    CREAR = 'CREAR'
    ELIMINAR = 'ELIMINAR'
    ACTUALIZAR = 'ACTUALIZAR'
    MODIFICAR = 'MODIFICAR'


class TipoTransacion(Enum):
    PAGO = "PAGO"
    REEMBOLSO = "REEMBOLSO"

