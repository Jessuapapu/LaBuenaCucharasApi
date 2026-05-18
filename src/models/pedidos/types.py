from enum import Enum

class EstadoPedido(Enum):
    PENDIENTE = "PENDIENTE"
    ENTREGADO = "ENTREGADO"
    ANULADO = "ANULADO"

class TipoPedidoss(Enum):
    EVENTO = "EVENTO"
    CONTRATO = "CONTRATO"
    BUFFET = "BUFFET"

