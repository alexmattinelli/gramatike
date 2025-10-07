"""increase resumo length to 1000

Revision ID: g1h2i3j4k5l6
Revises: f6a7b8c9d0e1
Create Date: 2025-01-09 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'g1h2i3j4k5l6'
down_revision = 'f6a7b8c9d0e1'
branch_labels = None
depends_on = None

def upgrade():
    # Increase resumo field from VARCHAR(400) to VARCHAR(1000)
    op.alter_column('edu_content', 'resumo',
                    existing_type=sa.String(length=400),
                    type_=sa.String(length=1000),
                    existing_nullable=True)

def downgrade():
    # Revert resumo field back to VARCHAR(400)
    op.alter_column('edu_content', 'resumo',
                    existing_type=sa.String(length=1000),
                    type_=sa.String(length=400),
                    existing_nullable=True)
