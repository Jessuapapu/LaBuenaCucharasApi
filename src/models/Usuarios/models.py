from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime
from .types import Rol

class Usuario(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, nullable=False, max_length=150)
    password_hash: str = Field(nullable=False)
    rol: Rol
    activo: bool = Field(default=True)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)