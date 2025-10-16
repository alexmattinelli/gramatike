"""change resumo to unlimited text

Revision ID: j9k0l1m2n3o4
Revises: i8j9k0l1m2n3, z9a8b7c6d5e4
Create Date: 2025-10-15 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'j9k0l1m2n3o4'
down_revision = ('i8j9k0l1m2n3', 'z9a8b7c6d5e4')
branch_labels = None
depends_on = None

def upgrade():
    # Change resumo field to TEXT (unlimited)
    # Using direct SQL for PostgreSQL compatibility
    # Works regardless of current VARCHAR length (400, 1000, or 2000)
    op.execute("ALTER TABLE edu_content ALTER COLUMN resumo TYPE TEXT")

def downgrade():
    # Revert resumo field back to VARCHAR(2000)
    # Note: This may truncate data if resumo exceeds 2000 characters
    op.execute("ALTER TABLE edu_content ALTER COLUMN resumo TYPE VARCHAR(2000)")
