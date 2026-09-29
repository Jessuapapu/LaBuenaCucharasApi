"""Modificar tablas de cliente, facturas y ordenes

Revision ID: 429f53ff53a8
Revises: f24d52ce2c5f
Create Date: 2026-03-18 21:34:02.090642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql
import sqlmodel.sql.sqltypes

# revision identifiers, used by Alembic.
revision: str = '429f53ff53a8'
down_revision: Union[str, Sequence[str], None] = 'f24d52ce2c5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def drop_fk_by_column(table_name: str, column_name: str) -> None:
    """Busca y elimina dinámicamente la FK de una columna sin importar su nombre autogenerado."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for fk in inspector.get_foreign_keys(table_name):
        if column_name in fk['constrained_columns'] and fk.get('name'):
            op.drop_constraint(fk['name'], table_name, type_='foreignkey')


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Crear nuevas tablas
    op.create_table(
        'metodospago',
        sa.Column('IdMetodoPago', sa.Integer(), nullable=False),
        sa.Column('NombreTipo', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.PrimaryKeyConstraint('IdMetodoPago')
    )
    op.create_table(
        'clientedireccion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('IdCliente', sa.Integer(), nullable=False),
        sa.Column('Dirreccion', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.ForeignKeyConstraint(['IdCliente'], ['clientes.IdCliente'], name='fk_clientedireccion_clientes'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'pago',
        sa.Column('IdPago', sa.Integer(), nullable=False),
        sa.Column('IdMetodoPagos', sa.Integer(), nullable=True),
        sa.Column('IdOrden', sa.Integer(), nullable=True),
        sa.Column('PagoTotal', sa.Numeric(), nullable=False),
        sa.Column('Fecha', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['IdMetodoPagos'], ['metodospago.IdMetodoPago'], name='fk_pago_metodospago'),
        sa.ForeignKeyConstraint(['IdOrden'], ['ordenes.IdOrdenes'], name='fk_pago_ordenes'),
        sa.PrimaryKeyConstraint('IdPago')
    )
    op.create_index(op.f('ix_pago_IdPago'), 'pago', ['IdPago'], unique=False)

    # 2. Eliminar tabla antigua pagoordenes (verificando índice primero)
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_indexes = [idx['name'] for idx in inspector.get_indexes('pagoordenes')]
    if 'ix_pagoordenes_IdPagoOrdenes' in existing_indexes:
        op.drop_index(op.f('ix_pagoordenes_IdPagoOrdenes'), table_name='pagoordenes')
    op.drop_table('pagoordenes')

    # 3. Modificar tabla facturas
    op.add_column('facturas', sa.Column('IdOrdenes', sa.Integer(), nullable=True))
    op.alter_column(
        'facturas', 'Fecha',
        existing_type=sa.VARCHAR(length=10, collation='Modern_Spanish_CI_AS'),
        type_=sa.DateTime(),
        existing_nullable=False
    )
    op.create_foreign_key('fk_facturas_ordenes', 'facturas', 'ordenes', ['IdOrdenes'], ['IdOrdenes'])

    # 4. Modificar tabla pedidos
    op.add_column('pedidos', sa.Column('IdOrdenes', sa.Integer(), nullable=True))
    op.alter_column(
        'pedidos', 'Fecha',
        existing_type=sa.VARCHAR(length=10, collation='Modern_Spanish_CI_AS'),
        type_=sa.DateTime(),
        existing_nullable=False
    )
    
    # Elimina la FK de IdCliente buscando su nombre real en el servidor actual
    drop_fk_by_column('pedidos', 'IdCliente')
    
    op.create_foreign_key('fk_pedidos_ordenes', 'pedidos', 'ordenes', ['IdOrdenes'], ['IdOrdenes'])
    op.drop_column('pedidos', 'IdCliente')


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Revertir cambios en pedidos
    op.add_column('pedidos', sa.Column('IdCliente', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint('fk_pedidos_ordenes', 'pedidos', type_='foreignkey')
    op.create_foreign_key('fk_pedidos_clientes', 'pedidos', 'clientes', ['IdCliente'], ['IdCliente'])
    op.alter_column(
        'pedidos', 'Fecha',
        existing_type=sa.DateTime(),
        type_=sa.VARCHAR(length=10, collation='Modern_Spanish_CI_AS'),
        existing_nullable=False
    )
    op.drop_column('pedidos', 'IdOrdenes')

    # 2. Revertir cambios en facturas
    op.drop_constraint('fk_facturas_ordenes', 'facturas', type_='foreignkey')
    op.alter_column(
        'facturas', 'Fecha',
        existing_type=sa.DateTime(),
        type_=sa.VARCHAR(length=10, collation='Modern_Spanish_CI_AS'),
        existing_nullable=False
    )
    op.drop_column('facturas', 'IdOrdenes')

    # 3. Recrear pagoordenes
    op.create_table(
        'pagoordenes',
        sa.Column('IdPagoOrdenes', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('IdMetodoPagoOrdenes', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('IdOrden', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('PagoTotal', sa.NUMERIC(precision=18, scale=0), autoincrement=False, nullable=False),
        sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['IdMetodoPagoOrdenes'], ['metodospagoordenes.IdMetodoPagoOrdenes'], name='fk_pagoordenes_metodospago'),
        sa.ForeignKeyConstraint(['IdOrden'], ['ordenes.IdOrdenes'], name='fk_pagoordenes_ordenes'),
        sa.PrimaryKeyConstraint('IdPagoOrdenes')
    )
    op.create_index(op.f('ix_pagoordenes_IdPagoOrdenes'), 'pagoordenes', ['IdPagoOrdenes'], unique=False)

    # 4. Eliminar tablas nuevas
    op.drop_index(op.f('ix_pago_IdPago'), table_name='pago')
    op.drop_table('pago')
    op.drop_table('clientedireccion')
    op.drop_table('metodospago')