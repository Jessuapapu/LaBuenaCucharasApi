"""arreglar tabla Usuarios

Revision ID: d31708db4da9
Revises: 49a4f41fcb55
Create Date: 2026-05-24 20:54:15.365808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'd31708db4da9'
down_revision: Union[str, Sequence[str], None] = '49a4f41fcb55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table('usuario'):
        op.create_table(
            'usuario',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('username', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('password_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('rol', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('activo', sa.Boolean(), nullable=False),
            sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id', name='pk_usuario')
        )
        op.create_index(op.f('ix_usuario_id'), 'usuario', ['id'], unique=True)
    else:
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('usuario')]
        if 'ix_usuario_id' not in existing_indexes:
            op.create_index(op.f('ix_usuario_id'), 'usuario', ['id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table('usuario'):
        # En SQL Server, al borrar la tabla se eliminan sus índices automáticamente
        op.drop_table('usuario')