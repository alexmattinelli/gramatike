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
    # Using direct SQL for PostgreSQL compatibility
    op.execute("ALTER TABLE edu_content ALTER COLUMN resumo TYPE VARCHAR(1000)")

def downgrade():
    # Revert resumo field back to VARCHAR(400)
    op.execute("ALTER TABLE edu_content ALTER COLUMN resumo TYPE VARCHAR(400)")
