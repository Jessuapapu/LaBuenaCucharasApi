from enum import Enum

class EstadoPedido(Enum):
    PENDIENTE = "Pendiente"
    ENTREGADO = "Entregado"
    ANULADO = "Anulado"


class EstadoFactura(Enum):
    GENERADA = "Generada"
    ENVIADA = "Enviada"
    ACEPTADA = "Aceptada"
    PAGADA = "Pagada"
    ATRASADA = "Atrasada"
    RECHAZADA = "Rechazada"
    ANULADA = "Anulada"
