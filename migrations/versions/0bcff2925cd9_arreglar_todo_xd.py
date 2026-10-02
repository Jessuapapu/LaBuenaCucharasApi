"""arreglar todo xd

Revision ID: 0bcff2925cd9
Revises: fdb8da1a0356
Create Date: 2026-09-30 23:55:52.442648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '0bcff2925cd9'
down_revision: Union[str, Sequence[str], None] = 'fdb8da1a0356'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f('ix_auditoria_pedidos_IdAuditoria_Pedidos'), table_name='auditoria_pedidos')
    op.drop_table('auditoria_pedidos')
    op.drop_index(op.f('ix_auditoria_transaciones_IdAuditoria_Transaciones'), table_name='auditoria_transaciones')
    op.drop_table('auditoria_transaciones')
    op.drop_table('clientetelefono')
    op.drop_table('clientecorreo')
    op.drop_index(op.f('ix_auditoria_pagos_IdAuditoria_Pagos'), table_name='auditoria_pagos')
    op.drop_table('auditoria_pagos')
    op.drop_index(op.f('ix_auditoria_facturas_IdAuditoria_Facturas'), table_name='auditoria_facturas')
    op.drop_table('auditoria_facturas')
    op.drop_index(op.f('ix_auditoria_cliente_IdAuditoria_Clientes'), table_name='auditoria_cliente')
    op.drop_table('auditoria_cliente')
    op.drop_table('platilloseingredientes')
    op.drop_table('detallesdepedidos')
    op.drop_index(op.f('ix_auditoria_platillos_IdAuditoria_Platillos'), table_name='auditoria_platillos')
    op.drop_table('auditoria_platillos')
    op.drop_table('auditoriaimagenes')
    op.drop_index(op.f('ix_auditoria_ordenes_IdAuditoria_Ordenes'), table_name='auditoria_ordenes')
    op.drop_table('auditoria_ordenes')
    op.drop_index(op.f('ix_auditoria_imagenes_IdAuditoria_Imagenes'), table_name='auditoria_imagenes')
    op.drop_table('auditoria_imagenes')
    op.drop_index(op.f('ix_auditoria_usuario_IdAuditoria_Usuario'), table_name='auditoria_usuario')
    op.drop_table('auditoria_usuario')
    op.drop_table('facturaspedidos')
    
    op.alter_column('auditoria_caja', 'Username',
               existing_type=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               type_=sqlmodel.sql.sqltypes.AutoString(length=150),
               existing_nullable=False)
    op.alter_column('auditoria_comedor', 'Username',
               existing_type=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               type_=sqlmodel.sql.sqltypes.AutoString(length=150),
               existing_nullable=False)
    op.alter_column('catalogoplatillos', 'NombreCatalogoPlatillo',
               existing_type=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               type_=sqlmodel.sql.sqltypes.AutoString(length=150),
               existing_nullable=False)
    op.alter_column('clientedireccion', 'Dirreccion',
               existing_type=sa.VARCHAR(length=100, collation='SQL_Latin1_General_CP1_CI_AS'),
               type_=sqlmodel.sql.sqltypes.AutoString(length=1000),
               existing_nullable=False)
    op.add_column('clientes', sa.Column('CorreoElectronico', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False))
    op.add_column('clientes', sa.Column('Telefono', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False))
    op.drop_column('clientes', 'DireccionCliente')
    op.alter_column('ingredientes', 'NombreIngrediente',
               existing_type=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               type_=sqlmodel.sql.sqltypes.AutoString(length=150),
               existing_nullable=False)
    op.add_column('insumos', sa.Column('Stock', sa.Integer(), nullable=False))
    
    # 1. Eliminamos la llave foránea ANTES de borrar la tabla hija
    op.drop_constraint(op.f('FK__insumos__IdCateg__62EF9734'), 'insumos', type_='foreignkey')
    op.drop_column('insumos', 'IdCategoriaInsumo')
    # 2. Ahora sí, borramos la tabla categoriasinsumos de forma segura
    op.drop_table('categoriasinsumos')
    
    op.alter_column('menudiario', 'Hora',
               existing_type=mssql.TIME(),
               nullable=False)
    op.alter_column('platillos', 'NombrePlatillo',
               existing_type=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               type_=sqlmodel.sql.sqltypes.AutoString(length=200),
               existing_nullable=False)
    op.alter_column('usuario', 'username',
               existing_type=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               type_=sqlmodel.sql.sqltypes.AutoString(length=150),
               existing_nullable=False)
    op.alter_column('usuario', 'rol',
               existing_type=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               type_=sa.Enum('MESERO', 'CAJERO', 'ADMIN', 'COCINA', name='rol'),
               existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('usuario', 'rol',
               existing_type=sa.Enum('MESERO', 'CAJERO', 'ADMIN', 'COCINA', name='rol'),
               type_=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               existing_nullable=False)
    op.alter_column('usuario', 'username',
               existing_type=sqlmodel.sql.sqltypes.AutoString(length=150),
               type_=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               existing_nullable=False)
    op.alter_column('platillos', 'NombrePlatillo',
               existing_type=sqlmodel.sql.sqltypes.AutoString(length=200),
               type_=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               existing_nullable=False)
    op.alter_column('menudiario', 'Hora',
               existing_type=mssql.TIME(),
               nullable=True)
               
    # 1. Recreamos la tabla categoriasinsumos PRIMERO
    op.create_table('categoriasinsumos',
    sa.Column('IdCategoriaInsumo', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('NombreCategoriaInsumo', sa.VARCHAR(length=150, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('IdCategoriaInsumo', name=op.f('PK__categori__EE8BC207B904058F'))
    )
    # 2. Recreamos la columna y la llave foránea apuntando a la tabla ya existente
    op.add_column('insumos', sa.Column('IdCategoriaInsumo', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key(op.f('FK__insumos__IdCateg__62EF9734'), 'insumos', 'categoriasinsumos', ['IdCategoriaInsumo'], ['IdCategoriaInsumo'])
    op.drop_column('insumos', 'Stock')
    
    op.alter_column('ingredientes', 'NombreIngrediente',
               existing_type=sqlmodel.sql.sqltypes.AutoString(length=150),
               type_=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               existing_nullable=False)
    op.add_column('clientes', sa.Column('DireccionCliente', sa.VARCHAR(length=150, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False))
    op.drop_column('clientes', 'Telefono')
    op.drop_column('clientes', 'CorreoElectronico')
    op.alter_column('clientedireccion', 'Dirreccion',
               existing_type=sqlmodel.sql.sqltypes.AutoString(length=1000),
               type_=sa.VARCHAR(length=100, collation='SQL_Latin1_General_CP1_CI_AS'),
               existing_nullable=False)
    op.alter_column('catalogoplatillos', 'NombreCatalogoPlatillo',
               existing_type=sqlmodel.sql.sqltypes.AutoString(length=150),
               type_=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               existing_nullable=False)
    op.alter_column('auditoria_comedor', 'Username',
               existing_type=sqlmodel.sql.sqltypes.AutoString(length=150),
               type_=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               existing_nullable=False)
    op.alter_column('auditoria_caja', 'Username',
               existing_type=sqlmodel.sql.sqltypes.AutoString(length=150),
               type_=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               existing_nullable=False)
    
    op.create_table('facturaspedidos',
    sa.Column('IdFactura', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('IdPedido', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['IdFactura'], ['facturas.IdFactura'], name=op.f('FK__facturasp__IdFac__7DA38D70')),
    sa.ForeignKeyConstraint(['IdPedido'], ['pedidos.IdPedido'], name=op.f('FK__facturasp__IdPed__7E97B1A9')),
    sa.PrimaryKeyConstraint('IdFactura', name=op.f('PK__facturas__50E7BAF1CA828039'))
    )
    op.create_table('auditoria_usuario',
    sa.Column('IdAuditoria_Usuario', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.Column('IdUsuarioCreado', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
    sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['IdUsuarioCreado'], ['usuario.id'], name=op.f('FK__auditoria__IdUsu__424DBD78')),
    sa.PrimaryKeyConstraint('IdAuditoria_Usuario', name=op.f('PK__auditori__C2815FC2B7DC24F9'))
    )
    op.create_index(op.f('ix_auditoria_usuario_IdAuditoria_Usuario'), 'auditoria_usuario', ['IdAuditoria_Usuario'], unique=False)
    op.create_table('auditoria_imagenes',
    sa.Column('IdAuditoria_Imagenes', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.Column('IdImagen', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
    sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('IdAuditoria_Imagenes', name=op.f('PK__auditori__926F70067A0F9F81'))
    )
    op.create_index(op.f('ix_auditoria_imagenes_IdAuditoria_Imagenes'), 'auditoria_imagenes', ['IdAuditoria_Imagenes'], unique=False)
    op.create_table('auditoria_ordenes',
    sa.Column('IdAuditoria_Ordenes', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.Column('IdOrden', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
    sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['IdOrden'], ['ordenes.IdOrdenes'], name=op.f('FK__auditoria__IdOrd__452A2A23')),
    sa.PrimaryKeyConstraint('IdAuditoria_Ordenes', name=op.f('PK__auditori__AB55208E225C16B8'))
    )
    op.create_index(op.f('ix_auditoria_ordenes_IdAuditoria_Ordenes'), 'auditoria_ordenes', ['IdAuditoria_Ordenes'], unique=False)
    op.create_table('auditoriaimagenes',
    sa.Column('IDAU_imagenes', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('fecha', sa.DATETIME(), autoincrement=False, nullable=False),
    sa.Column('accion', sa.VARCHAR(length=9, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('IDAU_imagenes', name=op.f('PK__auditori__873346CCF42DAFC3'))
    )
    op.create_table('auditoria_platillos',
    sa.Column('IdAuditoria_Platillos', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.Column('IdPlatillo', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
    sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['IdPlatillo'], ['platillos.IdPlatillo'], name=op.f('FK__auditoria__IdPla__3F7150CD')),
    sa.PrimaryKeyConstraint('IdAuditoria_Platillos', name=op.f('PK__auditori__9A3E666225541C3A'))
    )
    op.create_index(op.f('ix_auditoria_platillos_IdAuditoria_Platillos'), 'auditoria_platillos', ['IdAuditoria_Platillos'], unique=False)
    op.create_table('detallesdepedidos',
    sa.Column('IdDetalle', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('IdPedido', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('IdPlatillo', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('Cantidad', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('PrecioUnitario', sa.FLOAT(precision=53), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['IdPedido'], ['pedidos.IdPedido'], name=op.f('FK__detallesd__IdPed__7231DAC4')),
    sa.ForeignKeyConstraint(['IdPlatillo'], ['platillos.IdPlatillo'], name=op.f('FK__detallesd__IdPla__7325FEFD')),
    sa.PrimaryKeyConstraint('IdDetalle', name=op.f('PK__detalles__E43646A5750C893A'))
    )
    op.create_table('platilloseingredientes',
    sa.Column('IdRelacion', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('IdPlatillo', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('IdIngrediente', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['IdIngrediente'], ['ingredientes.IdIngrediente'], name=op.f('FK__platillos__IdIng__5B196B42')),
    sa.ForeignKeyConstraint(['IdPlatillo'], ['platillos.IdPlatillo'], name=op.f('FK__platillos__IdPla__5C0D8F7B')),
    sa.PrimaryKeyConstraint('IdRelacion', name=op.f('PK__platillo__D27D6AE7BF7767BD'))
    )
    op.create_table('auditoria_cliente',
    sa.Column('IdAuditoria_Clientes', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.Column('IdCliente', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
    sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['IdCliente'], ['clientes.IdCliente'], name=op.f('FK__auditoria__IdCli__39B87777')),
    sa.PrimaryKeyConstraint('IdAuditoria_Clientes', name=op.f('PK__auditori__9A3E6662183B2E24'))
    )
    op.create_index(op.f('ix_auditoria_cliente_IdAuditoria_Clientes'), 'auditoria_cliente', ['IdAuditoria_Clientes'], unique=False)
    op.create_table('auditoria_facturas',
    sa.Column('IdAuditoria_Facturas', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.Column('IdFactura', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
    sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['IdFactura'], ['facturas.IdFactura'], name=op.f('FK__auditoria__IdFac__3C94E422')),
    sa.PrimaryKeyConstraint('IdAuditoria_Facturas', name=op.f('PK__auditori__AB55208ED3060163'))
    )
    op.create_index(op.f('ix_auditoria_facturas_IdAuditoria_Facturas'), 'auditoria_facturas', ['IdAuditoria_Facturas'], unique=False)
    op.create_table('auditoria_pagos',
    sa.Column('IdAuditoria_Pagos', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.Column('IdPago', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
    sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['IdPago'], ['pago.IdPago'], name=op.f('FK__auditoria__IdPag__4AE30379')),
    sa.PrimaryKeyConstraint('IdAuditoria_Pagos', name=op.f('PK__auditori__9A3E6662B5043BDF'))
    )
    op.create_index(op.f('ix_auditoria_pagos_IdAuditoria_Pagos'), 'auditoria_pagos', ['IdAuditoria_Pagos'], unique=False)
    op.create_table('clientecorreo',
    sa.Column('id', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('IdCliente', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('CorreoElectronico', sa.VARCHAR(length=100, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['IdCliente'], ['clientes.IdCliente'], name=op.f('FK__clienteco__IdCli__5A5A5133')),
    sa.PrimaryKeyConstraint('id', name=op.f('PK__clientec__3213E83F5A01011C'))
    )
    op.create_table('clientetelefono',
    sa.Column('id', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('IdCliente', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('Telefono', sa.VARCHAR(length=20, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['IdCliente'], ['clientes.IdCliente'], name=op.f('FK__clientete__IdCli__5D36BDDE')),
    sa.PrimaryKeyConstraint('id', name=op.f('PK__clientet__3213E83F55869AA2'))
    )
    op.create_table('auditoria_transaciones',
    sa.Column('IdAuditoria_Transaciones', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.Column('IdPago', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['IdPago'], ['pago.IdPago'], name=op.f('FK__auditoria__IdPag__583CFE97')),
    sa.PrimaryKeyConstraint('IdAuditoria_Transaciones', name=op.f('PK__auditori__1E81A0CE859767FE'))
    )
    op.create_index(op.f('ix_auditoria_transaciones_IdAuditoria_Transaciones'), 'auditoria_transaciones', ['IdAuditoria_Transaciones'], unique=False)
    op.create_table('auditoria_pedidos',
    sa.Column('IdAuditoria_Pedidos', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
    sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.Column('IdPedido', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['IdPedido'], ['pedidos.IdPedido'], name=op.f('fk_auditoria_pedidos_pedidos')),
    sa.PrimaryKeyConstraint('IdAuditoria_Pedidos', name=op.f('PK__auditori__AB55208E70DB388C'))
    )
    op.create_index(op.f('ix_auditoria_pedidos_IdAuditoria_Pedidos'), 'auditoria_pedidos', ['IdAuditoria_Pedidos'], unique=False)