"""mapeo_completo

Revision ID: 82f7b19964b1
Revises: a4b8f230d1af
Create Date: 2026-07-14 12:18:41.605717

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '82f7b19964b1'
down_revision: Union[str, Sequence[str], None] = 'a4b8f230d1af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema (Cirugía Segura - Sin pérdida de datos históricos)."""
    # 1. Añadir control de bajas lógicas a usuarios
    op.add_column('usuarios', sa.Column('is_active', sa.Boolean(), nullable=True))
    
    # 2. Añadir índices de optimización de búsqueda (Performance)
    op.create_index(op.f('ix_creditos_id'), 'creditos', ['id'], unique=False)
    op.create_index(op.f('ix_pagos_id'), 'pagos', ['id'], unique=False)
    op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False)

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_usuarios_id'), table_name='usuarios')
    op.drop_index(op.f('ix_pagos_id'), table_name='pagos')
    op.drop_index(op.f('ix_creditos_id'), table_name='creditos')
    op.drop_column('usuarios', 'is_active')
    # ### end Alembic commands ###
