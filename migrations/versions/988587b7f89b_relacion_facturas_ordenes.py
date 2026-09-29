"""RELACION facturas ordenes

Revision ID: 988587b7f89b
Revises: e0cf940b7493
Create Date: 2026-04-28 00:22:57.773403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '988587b7f89b'
down_revision: Union[str, Sequence[str], None] = 'e0cf940b7493'
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

    # 1. Si existe la versión vieja de facturasordenes, la borramos para crear la nueva con columna 'Id'
    if inspector.has_table('FacturasOrdenes'):
        op.drop_table('FacturasOrdenes')

    op.create_table(
        'FacturasOrdenes',
        sa.Column('Id', sa.Integer(), nullable=False),
        sa.Column('IdFactura', sa.Integer(), nullable=False),
        sa.Column('IdOrdenes', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['IdFactura'], ['facturas.IdFactura'], name='fk_facturasordenes_facturas'),
        sa.ForeignKeyConstraint(['IdOrdenes'], ['ordenes.IdOrdenes'], name='fk_facturasordenes_ordenes'),
        sa.PrimaryKeyConstraint('Id', name='pk_facturasordenes'),
        sa.UniqueConstraint('IdOrdenes', name='uq_facturasordenes_idordenes')
    )

    # 2. Eliminar la FK y la columna IdOrdenes de 'facturas' de forma segura
    existing_columns = [col['name'] for col in inspector.get_columns('facturas')]
    if 'IdOrdenes' in existing_columns:
        drop_fk_by_column('facturas', 'IdOrdenes')
        op.drop_column('facturas', 'IdOrdenes')


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. Restaurar columna IdOrdenes y su FK en 'facturas'
    existing_columns = [col['name'] for col in inspector.get_columns('facturas')]
    if 'IdOrdenes' not in existing_columns:
        op.add_column('facturas', sa.Column('IdOrdenes', sa.INTEGER(), autoincrement=False, nullable=True))
        op.create_foreign_key('fk_facturas_ordenes', 'facturas', 'ordenes', ['IdOrdenes'], ['IdOrdenes'])

    # 2. Borrar FacturasOrdenes (corregido: antes borraba facturaspedidos por error)
    if inspector.has_table('FacturasOrdenes'):
        op.drop_table('FacturasOrdenes')