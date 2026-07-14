"""agregar_auditoria_clientes

Revision ID: a4b8f230d1af
Revises: 
Create Date: 2026-07-07 09:46:50.374795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a4b8f230d1af'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema (Versión Segura)."""
    # 1. Inyección exclusiva de columnas de negocio (Bajas lógicas y auditoría)
    op.add_column('clientes', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('clientes', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('clientes', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    
    # 2. Creación de índices para optimizar la velocidad de búsqueda
    op.create_index(op.f('ix_clientes_id'), 'clientes', ['id'], unique=False)
    op.create_index(op.f('ix_clientes_rfc'), 'clientes', ['rfc'], unique=True)

def downgrade() -> None:
    """Downgrade schema (Versión Segura)."""
    # Revertir únicamente las columnas e índices añadidos, protegiendo el resto de la estructura
    op.drop_index(op.f('ix_clientes_rfc'), table_name='clientes')
    op.drop_index(op.f('ix_clientes_id'), table_name='clientes')
    op.drop_column('clientes', 'updated_at')
    op.drop_column('clientes', 'created_at')
    op.drop_column('clientes', 'is_active')