"""caja

Revision ID: bc060befdd19
Revises: 4f6032df4fa4
Create Date: 2026-06-03 23:14:50.573010

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'bc060befdd19'
down_revision: Union[str, Sequence[str], None] = '4f6032df4fa4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def drop_fk_by_column(table_name: str, column_name: str) -> None:
    """Busca y elimina dinámicamente la FK de una columna sin importar su nombre en SQL Server."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for fk in inspector.get_foreign_keys(table_name):
        if column_name in fk['constrained_columns'] and fk.get('name'):
            op.drop_constraint(fk['name'], table_name, type_='foreignkey')


def drop_default_constraint(table_name: str, column_name: str) -> None:
    """Elimina dinámicamente el DEFAULT constraint autogenerado por SQL Server antes de borrar la columna."""
    bind = op.get_bind()
    query = sa.text("""
        SELECT dc.name
        FROM sys.default_constraints dc
        JOIN sys.columns c ON dc.parent_object_id = c.object_id AND dc.parent_column_id = c.column_id
        WHERE dc.parent_object_id = OBJECT_ID(:table) AND c.name = :column
    """)
    default_name = bind.execute(query, {"table": table_name, "column": column_name}).scalar()
    if default_name:
        op.execute(f"ALTER TABLE [{table_name}] DROP CONSTRAINT [{default_name}]")


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. Crear tabla reembolsos si no existe
    if not inspector.has_table('reembolsos'):
        op.create_table(
            'reembolsos',
            sa.Column('IdReembolso', sa.Integer(), nullable=False),
            sa.Column('IdOrden', sa.Integer(), nullable=False),
            sa.Column('Monto', sa.Numeric(), nullable=False),
            sa.Column('Razones', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.ForeignKeyConstraint(['IdOrden'], ['ordenes.IdOrdenes'], name='fk_reembolsos_ordenes'),
            sa.PrimaryKeyConstraint('IdReembolso', name='pk_reembolsos')
        )

    # 2. Crear tabla referenciapago si no existe
    if not inspector.has_table('referenciapago'):
        op.create_table(
            'referenciapago',
            sa.Column('IdReferenciaPago', sa.Integer(), nullable=False),
            sa.Column('IdPago', sa.Integer(), nullable=True),
            sa.Column('referencia', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.ForeignKeyConstraint(['IdPago'], ['pago.IdPago'], name='fk_referenciapago_pago'),
            sa.PrimaryKeyConstraint('IdReferenciaPago', name='pk_referenciapago')
        )

    # 3. Quitar FK y columna IdMetodoPagos de 'pago'
    existing_columns = [col['name'] for col in inspector.get_columns('pago')]
    if 'IdMetodoPagos' in existing_columns:
        drop_fk_by_column('pago', 'IdMetodoPagos')
        op.drop_column('pago', 'IdMetodoPagos')

    # 4. Eliminar tabla metodospago si existe
    if inspector.has_table('metodospago'):
        op.drop_table('metodospago')

    # 5. Agregar nuevas columnas a 'pago' si no existen
    if 'MetodoPagos' not in existing_columns:
        op.add_column('pago', sa.Column('MetodoPagos', sa.String(length=50), nullable=True))

    if 'Estado' not in existing_columns:
        op.add_column('pago', sa.Column('Estado', sa.Boolean(), nullable=False, server_default='1'))


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. Recrear tabla metodospago primero (para poder apuntar la FK hacia ella)
    if not inspector.has_table('metodospago'):
        op.create_table(
            'metodospago',
            sa.Column('IdMetodoPago', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
            sa.Column('NombreTipo', sa.VARCHAR(length=100, collation='Modern_Spanish_CI_AS'), autoincrement=False, nullable=False),
            sa.PrimaryKeyConstraint('IdMetodoPago', name='pk_metodospago')
        )

    # 2. Revertir columnas en 'pago'
    existing_columns = [col['name'] for col in inspector.get_columns('pago')]
    if 'IdMetodoPagos' not in existing_columns:
        op.add_column('pago', sa.Column('IdMetodoPagos', sa.INTEGER(), autoincrement=False, nullable=True))
        op.create_foreign_key('fk_pago_metodospago', 'pago', 'metodospago', ['IdMetodoPagos'], ['IdMetodoPago'])

    if 'Estado' in existing_columns:
        drop_default_constraint('pago', 'Estado')
        op.drop_column('pago', 'Estado')

    if 'MetodoPagos' in existing_columns:
        op.drop_column('pago', 'MetodoPagos')

    # 3. Eliminar tablas nuevas
    if inspector.has_table('referenciapago'):
        op.drop_table('referenciapago')

    if inspector.has_table('reembolsos'):
        op.drop_table('reembolsos')