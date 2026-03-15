from enum import Enum

class EstadoFactura(Enum):
    GENERADA = "Generada"
    ENVIADA = "Enviada"
    ACEPTADA = "Aceptada"
    PAGADA = "Pagada"
    ATRASADA = "Atrasada"
    RECHAZADA = "Rechazada"
    ANULADA = "Anulada"
