from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class Usuario(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, nullable=False)
    password_hash: str = Field(nullable=False)
    rol: str = Field(default="mesero", nullable=False)
    activo: bool = Field(default=True)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    