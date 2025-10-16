"""increase resumo length to 2000

Revision ID: i8j9k0l1m2n3
Revises: h7i8j9k0l1m2
Create Date: 2025-01-16 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'i8j9k0l1m2n3'
down_revision = 'h7i8j9k0l1m2'
branch_labels = None
depends_on = None

def upgrade():
    # Increase resumo field from VARCHAR(1000) to VARCHAR(2000)
    # Using direct SQL for PostgreSQL compatibility
    op.execute("ALTER TABLE edu_content ALTER COLUMN resumo TYPE VARCHAR(2000)")

def downgrade():
    # Revert resumo field back to VARCHAR(1000)
    op.execute("ALTER TABLE edu_content ALTER COLUMN resumo TYPE VARCHAR(1000)")
