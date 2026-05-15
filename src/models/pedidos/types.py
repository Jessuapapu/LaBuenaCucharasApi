from enum import Enum

class EstadoPedido(Enum):
    PENDIENTE = "PENDIENTE"
    ENTREGADO = "ENTREGADO"
    ANULADO = "ANULADO"

class TipoPedidos(Enum):
    EVENTO = "EVENTO"
    CONTRATO = "CONTRATO"
