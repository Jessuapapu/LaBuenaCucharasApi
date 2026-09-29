"""agregar relacion pedidos ordenes

Revision ID: fbb34492c916
Revises: 9c1a538b7431
Create Date: 2026-05-12 15:19:52.387734

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers, used by Alembic.
revision: str = 'fbb34492c916'
down_revision: Union[str, Sequence[str], None] = '9c1a538b7431'
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

    # 1. Crear tabla intermedia pedidosordenes si no existe
    if not inspector.has_table('pedidosordenes'):
        op.create_table(
            'pedidosordenes',
            sa.Column('IdPedidosOrdenes', sa.Integer(), nullable=False),
            sa.Column('IdPedido', sa.Integer(), nullable=False),
            sa.Column('IdOrdenes', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['IdOrdenes'], ['ordenes.IdOrdenes'], name='fk_pedidosordenes_ordenes'),
            sa.ForeignKeyConstraint(['IdPedido'], ['pedidos.IdPedido'], name='fk_pedidosordenes_pedidos'),
            sa.PrimaryKeyConstraint('IdPedidosOrdenes', name='pk_pedidosordenes')
        )

    existing_columns = [col['name'] for col in inspector.get_columns('pedidos')]
    existing_columns_lower = [col.lower() for col in existing_columns]

    # 2. Agregar columna 'fecha' solo si no existe ya como 'fecha' o 'Fecha'
    if 'fecha' not in existing_columns_lower:
        op.add_column('pedidos', sa.Column('fecha', sa.DateTime(), nullable=True))

    # 3. Eliminar FK dinámica y columna IdOrdenes de 'pedidos'
    if 'IdOrdenes' in existing_columns:
        drop_fk_by_column('pedidos', 'IdOrdenes')
        op.drop_column('pedidos', 'IdOrdenes')


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_columns = [col['name'] for col in inspector.get_columns('pedidos')]

    # 1. Restaurar IdOrdenes y su FK en 'pedidos'
    if 'IdOrdenes' not in existing_columns:
        op.add_column('pedidos', sa.Column('IdOrdenes', sa.INTEGER(), autoincrement=False, nullable=True))
        op.create_foreign_key('fk_pedidos_ordenes', 'pedidos', 'ordenes', ['IdOrdenes'], ['IdOrdenes'])

    # 2. Eliminar columna 'fecha' (solo si se llama 'fecha' en minúscula)
    if 'fecha' in existing_columns:
        op.drop_column('pedidos', 'fecha')

    # 3. Eliminar tabla pedidosordenes
    if inspector.has_table('pedidosordenes'):
        op.drop_table('pedidosordenes')