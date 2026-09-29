"""agregar tipo pedidos

Revision ID: c6a8ce2ddef4
Revises: fbb34492c916
Create Date: 2026-05-14 22:36:47.906605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers, used by Alembic.
revision: str = 'c6a8ce2ddef4'
down_revision: Union[str, Sequence[str], None] = 'fbb34492c916'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. Crear tabla tipopedido con nombres de restricciones explícitos
    if not inspector.has_table('tipopedido'):
        op.create_table(
            'tipopedido',
            sa.Column('IdTipoPedido', sa.Integer(), nullable=False),
            sa.Column('IdPedido', sa.Integer(), nullable=False),
            sa.Column('TipoPedidos', sa.Enum('EVENTO', 'CONTRATO', name='tipopedido'), nullable=False),
            sa.ForeignKeyConstraint(['IdPedido'], ['pedidos.IdPedido'], name='fk_tipopedido_pedidos'),
            sa.PrimaryKeyConstraint('IdTipoPedido', name='pk_tipopedido'),
            sa.UniqueConstraint('IdPedido', name='uq_tipopedido_idpedido')
        )

    # 2. Asegurar que no existan valores NULL antes de volver la columna NOT NULL
    existing_columns = {col['name'].lower(): col['name'] for col in inspector.get_columns('pedidos')}
    if 'fecha' in existing_columns:
        col_name = existing_columns['fecha']
        op.execute(sa.text(f"UPDATE pedidos SET [{col_name}] = GETDATE() WHERE [{col_name}] IS NULL"))
        op.alter_column(
            'pedidos',
            col_name,
            existing_type=sa.DATETIME(),
            nullable=False
        )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. Revertir fecha a nullable=True
    existing_columns = {col['name'].lower(): col['name'] for col in inspector.get_columns('pedidos')}
    if 'fecha' in existing_columns:
        col_name = existing_columns['fecha']
        op.alter_column(
            'pedidos',
            col_name,
            existing_type=sa.DATETIME(),
            nullable=True
        )

    # 2. Eliminar tabla tipopedido
    if inspector.has_table('tipopedido'):
        op.drop_table('tipopedido')