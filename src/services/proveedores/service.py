from sqlmodel import Session, select
from fastapi import HTTPException
from src.models.proveedores.models import Proveedores

def crear_proveedor(session: Session, proveedor: Proveedores):
    session.add(proveedor)
    session.commit()
    session.refresh(proveedor)
    return proveedor

def listar_proveedores(session: Session):
    return session.exec(select(Proveedores)).all()

def actualizar_proveedor(session: Session, id_prov: int, datos: dict):
    proveedor = session.get(Proveedores, id_prov)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    for key, value in datos.items():
        setattr(proveedor, key, value)
    session.add(proveedor)
    session.commit()
    session.refresh(proveedor)
    return proveedor

def eliminar_proveedor(session: Session, id_prov: int):
    proveedor = session.get(Proveedores, id_prov)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    session.delete(proveedor)
    session.commit()
    return {"mensaje": "Proveedor eliminado exitosamente"}