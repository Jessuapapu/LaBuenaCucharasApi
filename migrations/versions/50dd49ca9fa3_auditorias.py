"""auditorias 

Revision ID: 50dd49ca9fa3
Revises: fc6e41b08995
Create Date: 2026-05-26 16:51:10.775876

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers, used by Alembic.
revision: str = '50dd49ca9fa3'
down_revision: Union[str, Sequence[str], None] = 'fc6e41b08995'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def drop_fk_by_column(table_name: str, column_name: str) -> None:
    """Busca y elimina dinámicamente la FK de una columna sin importar su nombre en SQL Server."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for fk in inspector.get_foreign_keys(table_name):
        if column_name in fk['constrained_columns'] and fk.get('name'):
            op.drop_constraint(fk['name'], table_name, type_='foreignkey')


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_columns = [col['name'] for col in inspector.get_columns('auditoria_pedidos')]

    # 1. Agregar columna IdPedido y su FK si aún no existe
    if 'IdPedido' not in existing_columns:
        op.add_column('auditoria_pedidos', sa.Column('IdPedido', sa.Integer(), nullable=False))
        op.create_foreign_key(
            'fk_auditoria_pedidos_pedidos',
            'auditoria_pedidos',
            'pedidos',
            ['IdPedido'],
            ['IdPedido']
        )

    # 2. Eliminar FK dinámica y columna IdOrden
    if 'IdOrden' in existing_columns:
        drop_fk_by_column('auditoria_pedidos', 'IdOrden')
        op.drop_column('auditoria_pedidos', 'IdOrden')


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_columns = [col['name'] for col in inspector.get_columns('auditoria_pedidos')]

    # 1. Restaurar IdOrden y su FK
    if 'IdOrden' not in existing_columns:
        op.add_column('auditoria_pedidos', sa.Column('IdOrden', sa.INTEGER(), autoincrement=False, nullable=False))
        op.create_foreign_key(
            'fk_auditoria_pedidos_ordenes',
            'auditoria_pedidos',
            'ordenes',
            ['IdOrden'],
            ['IdOrdenes']
        )

    # 2. Eliminar FK y columna IdPedido
    if 'IdPedido' in existing_columns:
        drop_fk_by_column('auditoria_pedidos', 'IdPedido')
        op.drop_column('auditoria_pedidos', 'IdPedido')