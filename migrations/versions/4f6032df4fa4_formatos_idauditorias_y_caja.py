"""formatos IdAuditorias y caja

Revision ID: 4f6032df4fa4
Revises: 97358b6d16b8
Create Date: 2026-06-03 07:36:15.669731

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '4f6032df4fa4'
down_revision: Union[str, Sequence[str], None] = '97358b6d16b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Crear la nueva tabla auditoria_caja
    op.create_table('auditoria_caja',
    sa.Column('IdAuditoria_Caja', sa.Integer(), nullable=False),
    sa.Column('Username', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('HoraApertura', sa.DateTime(), nullable=False),
    sa.Column('HoraCerrar', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('IdAuditoria_Caja')
    )
    op.create_index(op.f('ix_auditoria_caja_IdAuditoria_Caja'), 'auditoria_caja', ['IdAuditoria_Caja'], unique=False)

    # 2. Renombrar columnas e índices (Drop índice anterior -> Renombrar -> Crear índice nuevo)
    
    # auditoria_cliente
    op.drop_index(op.f('ix_auditoria_cliente_IdAuditoria_Platillos'), table_name='auditoria_cliente')
    op.alter_column('auditoria_cliente', 'IdAuditoria_Platillos', new_column_name='IdAuditoria_Clientes')
    op.create_index(op.f('ix_auditoria_cliente_IdAuditoria_Clientes'), 'auditoria_cliente', ['IdAuditoria_Clientes'], unique=False)

    # auditoria_ordenes
    op.drop_index(op.f('ix_auditoria_ordenes_IdAuditoria_Facturas'), table_name='auditoria_ordenes')
    op.alter_column('auditoria_ordenes', 'IdAuditoria_Facturas', new_column_name='IdAuditoria_Ordenes')
    op.create_index(op.f('ix_auditoria_ordenes_IdAuditoria_Ordenes'), 'auditoria_ordenes', ['IdAuditoria_Ordenes'], unique=False)

    # auditoria_pagos
    op.drop_index(op.f('ix_auditoria_pagos_IdAuditoria_Platillos'), table_name='auditoria_pagos')
    op.alter_column('auditoria_pagos', 'IdAuditoria_Platillos', new_column_name='IdAuditoria_Pagos')
    op.create_index(op.f('ix_auditoria_pagos_IdAuditoria_Pagos'), 'auditoria_pagos', ['IdAuditoria_Pagos'], unique=False)

    # auditoria_pedidos
    op.drop_index(op.f('ix_auditoria_pedidos_IdAuditoria_Facturas'), table_name='auditoria_pedidos')
    op.alter_column('auditoria_pedidos', 'IdAuditoria_Facturas', new_column_name='IdAuditoria_Pedidos')
    op.create_index(op.f('ix_auditoria_pedidos_IdAuditoria_Pedidos'), 'auditoria_pedidos', ['IdAuditoria_Pedidos'], unique=False)


def downgrade() -> None:
    # 1. Revertir los renombramientos de pedidos a cliente
    
    # auditoria_pedidos
    op.drop_index(op.f('ix_auditoria_pedidos_IdAuditoria_Pedidos'), table_name='auditoria_pedidos')
    op.alter_column('auditoria_pedidos', 'IdAuditoria_Pedidos', new_column_name='IdAuditoria_Facturas')
    op.create_index(op.f('ix_auditoria_pedidos_IdAuditoria_Facturas'), 'auditoria_pedidos', ['IdAuditoria_Facturas'], unique=False)

    # auditoria_pagos
    op.drop_index(op.f('ix_auditoria_pagos_IdAuditoria_Pagos'), table_name='auditoria_pagos')
    op.alter_column('auditoria_pagos', 'IdAuditoria_Pagos', new_column_name='IdAuditoria_Platillos')
    op.create_index(op.f('ix_auditoria_pagos_IdAuditoria_Platillos'), 'auditoria_pagos', ['IdAuditoria_Platillos'], unique=False)

    # auditoria_ordenes
    op.drop_index(op.f('ix_auditoria_ordenes_IdAuditoria_Ordenes'), table_name='auditoria_ordenes')
    op.alter_column('auditoria_ordenes', 'IdAuditoria_Ordenes', new_column_name='IdAuditoria_Facturas')
    op.create_index(op.f('ix_auditoria_ordenes_IdAuditoria_Facturas'), 'auditoria_ordenes', ['IdAuditoria_Facturas'], unique=False)

    # auditoria_cliente
    op.drop_index(op.f('ix_auditoria_cliente_IdAuditoria_Clientes'), table_name='auditoria_cliente')
    op.alter_column('auditoria_cliente', 'IdAuditoria_Clientes', new_column_name='IdAuditoria_Platillos')
    op.create_index(op.f('ix_auditoria_cliente_IdAuditoria_Platillos'), 'auditoria_cliente', ['IdAuditoria_Platillos'], unique=False)

    # 2. Eliminar la tabla auditoria_caja
    op.drop_index(op.f('ix_auditoria_caja_IdAuditoria_Caja'), table_name='auditoria_caja')
    op.drop_table('auditoria_caja')