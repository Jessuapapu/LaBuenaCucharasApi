from enum import Enum

class EstadoOrden(str, Enum):
    PENDIENTE = "PENDIENTE"
    ENTREGADO = "ENTREGADO"
    PAGADO    = "PAGADO"
    ANULADO   = "ANULADO"
