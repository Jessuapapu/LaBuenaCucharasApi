"""ESTADO DE LAS ORDENES

Revision ID: e0cf940b7493
Revises: b5e5dc1f6eed
Create Date: 2026-04-25 22:21:30.162852

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers, used by Alembic.
revision: str = 'e0cf940b7493'
down_revision: Union[str, Sequence[str], None] = 'b5e5dc1f6eed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def drop_column_constraints(table_name: str, column_name: str) -> None:
    """Elimina dinámicamente los DEFAULT y CHECK constraints de una columna en SQL Server antes de borrarla."""
    bind = op.get_bind()
    # Buscar y eliminar DEFAULT constraint autogenerado por SQL Server
    default_query = sa.text("""
        SELECT dc.name
        FROM sys.default_constraints dc
        JOIN sys.columns c ON dc.parent_object_id = c.object_id AND dc.parent_column_id = c.column_id
        WHERE dc.parent_object_id = OBJECT_ID(:table) AND c.name = :column
    """)
    default_name = bind.execute(default_query, {"table": table_name, "column": column_name}).scalar()
    if default_name:
        op.execute(f"ALTER TABLE [{table_name}] DROP CONSTRAINT [{default_name}]")

    # Buscar y eliminar CHECK constraint (creado por sa.Enum)
    check_query = sa.text("""
        SELECT cc.name
        FROM sys.check_constraints cc
        JOIN sys.columns c ON cc.parent_object_id = c.object_id AND cc.parent_column_id = c.column_id
        WHERE cc.parent_object_id = OBJECT_ID(:table) AND c.name = :column
    """)
    check_name = bind.execute(check_query, {"table": table_name, "column": column_name}).scalar()
    if check_name:
        op.execute(f"ALTER TABLE [{table_name}] DROP CONSTRAINT [{check_name}]")


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. Solo borrar metodospagoordenes si aún existe en la BD del usuario
    if inspector.has_table('metodospagoordenes'):
        op.drop_table('metodospagoordenes')

    # NOTA: Si 'AuditoriaActualizacionPrecios' es de un Trigger que quieren conservar, 
    # deja comentadas las siguientes 2 líneas. Si de verdad quieren borrarla, descoméntalas:
    # if inspector.has_table('AuditoriaActualizacionPrecios'):
    #     op.drop_table('AuditoriaActualizacionPrecios')

    # 2. Agregar columna Estado a ordenes (verificando que no exista ya)
    existing_columns = [col['name'] for col in inspector.get_columns('ordenes')]
    if 'Estado' not in existing_columns:
        op.add_column(
            'ordenes',
            sa.Column(
                'Estado',
                sa.Enum('PENDIENTE', 'ENTREGADO', 'PAGADO', name='estadoorden'),
                nullable=False,
                server_default='PENDIENTE'
            )
        )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. En SQL Server hay que borrar el DEFAULT ('PENDIENTE') antes de hacer drop_column
    existing_columns = [col['name'] for col in inspector.get_columns('ordenes')]
    if 'Estado' in existing_columns:
        drop_column_constraints('ordenes', 'Estado')
        op.drop_column('ordenes', 'Estado')

    # 2. Recrear metodospagoordenes si no existe
    if not inspector.has_table('metodospagoordenes'):
        op.create_table(
            'metodospagoordenes',
            sa.Column('IdMetodoPagoOrdenes', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
            sa.Column('NombreTipo', sa.VARCHAR(length=100, collation='Modern_Spanish_CI_AS'), autoincrement=False, nullable=False),
            sa.PrimaryKeyConstraint('IdMetodoPagoOrdenes', name='pk_metodospagoordenes')
        )