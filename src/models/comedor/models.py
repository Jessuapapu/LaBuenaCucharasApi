from sqlmodel import Field, SQLModel
from datetime import datetime

class OrdenComedor():
    def __init__(self, IdOrden: int):
        self.HoraEntrada = datetime.now() 
        self.HoraSalida: datetime | None = None
        self.IdOrden: int = IdOrden
        self.Activo: bool = True
        
    def to_dict(self):
        return {
            "IdOrden": self.IdOrden,
            "HoraEntrada": self.HoraEntrada.isoformat(),
            "HoraSalida": self.HoraSalida.isoformat() if self.HoraSalida else None,
            "Activo": self.Activo
        }

class Mesa():

    def __init__(self, Id: int):
        self.Id: int = Id 
        self.Ordenes: list[OrdenComedor] = []
        
    def to_dict(self):
        return {
            "Id": self.Id,
            "Ordenes": [orden.to_dict() for orden in self.Ordenes]
        }

class MonitorComedor():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__constructor()
        return cls._instance
   
    def __constructor(self):
        self.NumeroMesas: int = 7
        self.MaxIdGenerado: int = 7
        self.Mesas: list[Mesa] = []

        for i in range(1, self.NumeroMesas + 1):
            self.Mesas.append(Mesa(i))

    def agregar_mesa(self):
        self.NumeroMesas += 1
        self.MaxIdGenerado += 1
        self.Mesas.append(Mesa(self.MaxIdGenerado))
    
    def eliminar_mesa(self, Id: int):
        for mesa in self.Mesas:
            if mesa.Id == Id:
                self.Mesas.remove(mesa)
                self.NumeroMesas -= 1
                return

    def limpiar_orden(self):
        OrdenesABorrar = []
        hoy = datetime.now().date()
        
        for mesa in self.Mesas:
            for orden in mesa.Ordenes:
                if orden.HoraEntrada.date() < hoy:
                    OrdenesABorrar.append((mesa, orden))
            
        for mesa, orden_borrar in OrdenesABorrar:
            mesa.Ordenes.remove(orden_borrar)


    def _obtener_mesa(self, IdMesa: int) -> Mesa | None:
        return next((m for m in self.Mesas if m.Id == IdMesa), None)

    def agregar_orden(self, IdOrden: int, IdMesa: int):
        self.limpiar_orden()
        mesa = self._obtener_mesa(IdMesa)
        if mesa:
            mesa.Ordenes.append(OrdenComedor(IdOrden=IdOrden))

    def guardar_orden(self, IdOrden: int, IdMesa: int):
        self.limpiar_orden()
        mesa = self._obtener_mesa(IdMesa)
        
        if not mesa:
            return False

        for orden in mesa.Ordenes:
            if orden.IdOrden == IdOrden and orden.Activo:
                orden.HoraSalida = datetime.now()
                orden.Activo = False
                return True
        return False

    def eliminar_orden(self, IdOrden: int, IdMesa: int):
        mesa = self._obtener_mesa(IdMesa)
        if not mesa:
            return False
            
        for orden in mesa.Ordenes:
            if orden.IdOrden == IdOrden:
                mesa.Ordenes.remove(orden)
                return True
        return False

    def to_dict(self):
        return {
            "TotalMesasActivas": self.NumeroMesas,
            "Mesas": [mesa.to_dict() for mesa in self.Mesas]
        }
    



class Auditoria_Mesas(SQLModel, table=True):
    IdAuditoria_Mesas: int = Field(primary_key=True)
    IdMesa: int = Field(nullable=False)
    IdOrden: int = Field(foreign_key = "ordenes.IdOrdenes", unique=True)
    HoraEntrada: datetime = Field(nullable=False)
    HoraSalida: datetime = Field(nullable=False)

class Auditoria_Comedor(SQLModel, table=True):
    IdAuditoria_Comedor: int = Field(primary_key=True)   
    HoraApertura: datetime = Field(nullable=False)
    HoraCerrar: datetime = Field(nullable=False)