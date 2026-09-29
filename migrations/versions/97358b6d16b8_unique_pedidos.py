"""unique pedidos

Revision ID: 97358b6d16b8
Revises: 50dd49ca9fa3
Create Date: 2026-06-02 06:19:17.719987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers, used by Alembic.
revision: str = '97358b6d16b8'
down_revision: Union[str, Sequence[str], None] = '50dd49ca9fa3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. Crear auditoriaimagenes solo si no existe en la BD
    if not inspector.has_table('auditoriaimagenes'):
        op.create_table(
            'auditoriaimagenes',
            sa.Column('IDAU_imagenes', sa.Integer(), nullable=False),
            sa.Column('fecha', sa.DateTime(), nullable=False),
            sa.Column('accion', sa.Enum('CREADO', 'ELIMINAR', 'MODIFICAR', name='accionimagenes'), nullable=False),
            sa.PrimaryKeyConstraint('IDAU_imagenes', name='pk_auditoriaimagenes')
        )

    # 2. En SQL Server los Unique Constraints se consultan mediante get_indexes()
    if inspector.has_table('pedidosordenes'):
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('pedidosordenes')]
        if 'uq_pedidosordenes_idordenes' not in existing_indexes:
            op.create_unique_constraint(
                'uq_pedidosordenes_idordenes',
                'pedidosordenes',
                ['IdOrdenes']
            )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. Quitar unique constraint si existe
    if inspector.has_table('pedidosordenes'):
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('pedidosordenes')]
        if 'uq_pedidosordenes_idordenes' in existing_indexes:
            op.drop_constraint('uq_pedidosordenes_idordenes', 'pedidosordenes', type_='unique')

    # 2. Quitar tabla auditoriaimagenes si existe
    if inspector.has_table('auditoriaimagenes'):
        op.drop_table('auditoriaimagenes')