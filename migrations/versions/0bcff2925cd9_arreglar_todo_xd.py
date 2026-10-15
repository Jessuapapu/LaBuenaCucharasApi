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

    # Limpieza de tablas de auditoría (verificando índices para evitar fallos)
    tablas_a_borrar = [
        ('auditoria_pedidos', 'ix_auditoria_pedidos_IdAuditoria_Pedidos'),
        ('auditoria_transaciones', 'ix_auditoria_transaciones_IdAuditoria_Transaciones'),
        ('clientetelefono', None),
        ('clientecorreo', None),
        ('auditoria_pagos', 'ix_auditoria_pagos_IdAuditoria_Pagos'),
        ('auditoria_facturas', 'ix_auditoria_facturas_IdAuditoria_Facturas'),
        ('auditoria_cliente', 'ix_auditoria_cliente_IdAuditoria_Clientes'),
        ('platilloseingredientes', None),
        ('detallesdepedidos', None),
        ('auditoria_platillos', 'ix_auditoria_platillos_IdAuditoria_Platillos'),
        ('auditoriaimagenes', None),
        ('auditoria_ordenes', 'ix_auditoria_ordenes_IdAuditoria_Ordenes'),
        ('auditoria_imagenes', 'ix_auditoria_imagenes_IdAuditoria_Imagenes'),
        ('auditoria_usuario', 'ix_auditoria_usuario_IdAuditoria_Usuario'),
        ('facturaspedidos', None)
    ]

    for tabla, indice in tablas_a_borrar:
        if inspector.has_table(tabla):
            if indice:
                existing_indexes = [idx['name'] for idx in inspector.get_indexes(tabla)]
                if indice in existing_indexes:
                    op.drop_index(op.f(indice), table_name=tabla)
            op.drop_table(tabla)

    # Modificación de columnas
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
    
    existing_clientes_cols = [col['name'] for col in inspector.get_columns('clientes')]
    if 'CorreoElectronico' not in existing_clientes_cols:
        op.add_column('clientes', sa.Column('CorreoElectronico', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False, server_default=''))
    if 'Telefono' not in existing_clientes_cols:
        op.add_column('clientes', sa.Column('Telefono', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False, server_default=''))
    if 'DireccionCliente' in existing_clientes_cols:
        op.drop_column('clientes', 'DireccionCliente')

    op.alter_column('ingredientes', 'NombreIngrediente',
               existing_type=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               type_=sqlmodel.sql.sqltypes.AutoString(length=150),
               existing_nullable=False)
               
    existing_insumos_cols = [col['name'] for col in inspector.get_columns('insumos')]
    if 'Stock' not in existing_insumos_cols:
        op.add_column('insumos', sa.Column('Stock', sa.Integer(), nullable=False, server_default='0'))
    
    # === CORRECCIÓN DE LA FK CONSTANTE AQUÍ ===
    if 'IdCategoriaInsumo' in existing_insumos_cols:
        drop_fk_by_column('insumos', 'IdCategoriaInsumo')
        op.drop_column('insumos', 'IdCategoriaInsumo')
        
    if inspector.has_table('categoriasinsumos'):
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
               
    # 1. Recreamos la tabla categoriasinsumos con nombre de PK limpio
    op.create_table('categoriasinsumos',
        sa.Column('IdCategoriaInsumo', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('NombreCategoriaInsumo', sa.VARCHAR(length=150, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('IdCategoriaInsumo', name='pk_categoriasinsumos')
    )
    
    # 2. Recreamos la columna y la llave foránea con nombre limpio
    op.add_column('insumos', sa.Column('IdCategoriaInsumo', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('fk_insumos_categoriasinsumos', 'insumos', 'categoriasinsumos', ['IdCategoriaInsumo'], ['IdCategoriaInsumo'])
    op.drop_column('insumos', 'Stock')
    
    op.alter_column('ingredientes', 'NombreIngrediente',
               existing_type=sqlmodel.sql.sqltypes.AutoString(length=150),
               type_=sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'),
               existing_nullable=False)
    op.add_column('clientes', sa.Column('DireccionCliente', sa.VARCHAR(length=150, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False, server_default=''))
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
    
    # Limpiamos todas las PKs y FKs de las tablas recreadas en el downgrade
    op.create_table('facturaspedidos',
        sa.Column('IdFactura', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('IdPedido', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['IdFactura'], ['facturas.IdFactura'], name='fk_facturaspedidos_factura'),
        sa.ForeignKeyConstraint(['IdPedido'], ['pedidos.IdPedido'], name='fk_facturaspedidos_pedido'),
        sa.PrimaryKeyConstraint('IdFactura', name='pk_facturaspedidos')
    )
    op.create_table('auditoria_usuario',
        sa.Column('IdAuditoria_Usuario', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.Column('IdUsuarioCreado', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
        sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['IdUsuarioCreado'], ['usuario.id'], name='fk_auditoria_usuario_id'),
        sa.PrimaryKeyConstraint('IdAuditoria_Usuario', name='pk_auditoria_usuario')
    )
    op.create_index(op.f('ix_auditoria_usuario_IdAuditoria_Usuario'), 'auditoria_usuario', ['IdAuditoria_Usuario'], unique=False)
    op.create_table('auditoria_imagenes',
        sa.Column('IdAuditoria_Imagenes', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.Column('IdImagen', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
        sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('IdAuditoria_Imagenes', name='pk_auditoria_imagenes')
    )
    op.create_index(op.f('ix_auditoria_imagenes_IdAuditoria_Imagenes'), 'auditoria_imagenes', ['IdAuditoria_Imagenes'], unique=False)
    op.create_table('auditoria_ordenes',
        sa.Column('IdAuditoria_Ordenes', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.Column('IdOrden', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
        sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['IdOrden'], ['ordenes.IdOrdenes'], name='fk_auditoria_ordenes_id'),
        sa.PrimaryKeyConstraint('IdAuditoria_Ordenes', name='pk_auditoria_ordenes')
    )
    op.create_index(op.f('ix_auditoria_ordenes_IdAuditoria_Ordenes'), 'auditoria_ordenes', ['IdAuditoria_Ordenes'], unique=False)
    op.create_table('auditoriaimagenes',
        sa.Column('IDAU_imagenes', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('fecha', sa.DATETIME(), autoincrement=False, nullable=False),
        sa.Column('accion', sa.VARCHAR(length=9, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('IDAU_imagenes', name='pk_auditoriaimagenes')
    )
    op.create_table('auditoria_platillos',
        sa.Column('IdAuditoria_Platillos', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.Column('IdPlatillo', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
        sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['IdPlatillo'], ['platillos.IdPlatillo'], name='fk_auditoria_platillos_id'),
        sa.PrimaryKeyConstraint('IdAuditoria_Platillos', name='pk_auditoria_platillos')
    )
    op.create_index(op.f('ix_auditoria_platillos_IdAuditoria_Platillos'), 'auditoria_platillos', ['IdAuditoria_Platillos'], unique=False)
    op.create_table('detallesdepedidos',
        sa.Column('IdDetalle', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('IdPedido', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('IdPlatillo', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('Cantidad', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('PrecioUnitario', sa.FLOAT(precision=53), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['IdPedido'], ['pedidos.IdPedido'], name='fk_detalles_pedidos'),
        sa.ForeignKeyConstraint(['IdPlatillo'], ['platillos.IdPlatillo'], name='fk_detalles_platillos'),
        sa.PrimaryKeyConstraint('IdDetalle', name='pk_detallesdepedidos')
    )
    op.create_table('platilloseingredientes',
        sa.Column('IdRelacion', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('IdPlatillo', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('IdIngrediente', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['IdIngrediente'], ['ingredientes.IdIngrediente'], name='fk_relacion_ingrediente'),
        sa.ForeignKeyConstraint(['IdPlatillo'], ['platillos.IdPlatillo'], name='fk_relacion_platillo'),
        sa.PrimaryKeyConstraint('IdRelacion', name='pk_platilloseingredientes')
    )
    op.create_table('auditoria_cliente',
        sa.Column('IdAuditoria_Clientes', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.Column('IdCliente', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
        sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['IdCliente'], ['clientes.IdCliente'], name='fk_auditoria_cliente_id'),
        sa.PrimaryKeyConstraint('IdAuditoria_Clientes', name='pk_auditoria_cliente')
    )
    op.create_index(op.f('ix_auditoria_cliente_IdAuditoria_Clientes'), 'auditoria_cliente', ['IdAuditoria_Clientes'], unique=False)
    op.create_table('auditoria_facturas',
        sa.Column('IdAuditoria_Facturas', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.Column('IdFactura', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
        sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['IdFactura'], ['facturas.IdFactura'], name='fk_auditoria_facturas_id'),
        sa.PrimaryKeyConstraint('IdAuditoria_Facturas', name='pk_auditoria_facturas')
    )
    op.create_index(op.f('ix_auditoria_facturas_IdAuditoria_Facturas'), 'auditoria_facturas', ['IdAuditoria_Facturas'], unique=False)
    op.create_table('auditoria_pagos',
        sa.Column('IdAuditoria_Pagos', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.Column('IdPago', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
        sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['IdPago'], ['pago.IdPago'], name='fk_auditoria_pagos_id'),
        sa.PrimaryKeyConstraint('IdAuditoria_Pagos', name='pk_auditoria_pagos')
    )
    op.create_index(op.f('ix_auditoria_pagos_IdAuditoria_Pagos'), 'auditoria_pagos', ['IdAuditoria_Pagos'], unique=False)
    op.create_table('clientecorreo',
        sa.Column('id', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('IdCliente', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('CorreoElectronico', sa.VARCHAR(length=100, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['IdCliente'], ['clientes.IdCliente'], name='fk_clientecorreo_cliente'),
        sa.PrimaryKeyConstraint('id', name='pk_clientecorreo')
    )
    op.create_table('clientetelefono',
        sa.Column('id', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('IdCliente', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('Telefono', sa.VARCHAR(length=20, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['IdCliente'], ['clientes.IdCliente'], name='fk_clientetelefono_cliente'),
        sa.PrimaryKeyConstraint('id', name='pk_clientetelefono')
    )
    op.create_table('auditoria_transaciones',
        sa.Column('IdAuditoria_Transaciones', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.Column('IdPago', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['IdPago'], ['pago.IdPago'], name='fk_auditoria_transaciones_id'),
        sa.PrimaryKeyConstraint('IdAuditoria_Transaciones', name='pk_auditoria_transaciones')
    )
    op.create_index(op.f('ix_auditoria_transaciones_IdAuditoria_Transaciones'), 'auditoria_transaciones', ['IdAuditoria_Transaciones'], unique=False)
    op.create_table('auditoria_pedidos',
        sa.Column('IdAuditoria_Pedidos', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
        sa.Column('Username', sa.VARCHAR(collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.Column('Fecha', sa.DATETIME(), autoincrement=False, nullable=False),
        sa.Column('TipoAccion', sa.VARCHAR(length=10, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
        sa.Column('IdPedido', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['IdPedido'], ['pedidos.IdPedido'], name='fk_auditoria_pedidos_pedidos'),
        sa.PrimaryKeyConstraint('IdAuditoria_Pedidos', name='pk_auditoria_pedidos')
    )
    op.create_index(op.f('ix_auditoria_pedidos_IdAuditoria_Pedidos'), 'auditoria_pedidos', ['IdAuditoria_Pedidos'], unique=False)