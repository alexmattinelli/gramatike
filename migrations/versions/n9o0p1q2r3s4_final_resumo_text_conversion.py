"""Final resumo TEXT conversion - database agnostic

Revision ID: n9o0p1q2r3s4
Revises: m8n9o0p1q2r3
Create Date: 2025-10-16 13:42:00.000000

This migration ensures the resumo column is TEXT type using database-agnostic
SQLAlchemy operations. It works for both PostgreSQL and SQLite.

This is a failsafe migration that handles any VARCHAR size (400, 1000, 2000).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'n9o0p1q2r3s4'
down_revision = 'm8n9o0p1q2r3'
branch_labels = None
depends_on = None

def upgrade():
    # Check database dialect and apply appropriate migration
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)
    
    # Get current column type
    columns = inspector.get_columns('edu_content')
    resumo_col = next((col for col in columns if col['name'] == 'resumo'), None)
    
    if not resumo_col:
        # Column doesn't exist, skip
        return
    
    # Check if already TEXT
    col_type = str(resumo_col['type']).upper()
    if 'TEXT' in col_type or 'CLOB' in col_type:
        # Already TEXT, skip
        return
    
    # Convert to TEXT using batch operations (works for all databases)
    with op.batch_alter_table('edu_content', schema=None) as batch_op:
        batch_op.alter_column('resumo',
                              existing_type=sa.String(),
                              type_=sa.Text(),
                              existing_nullable=True)

def downgrade():
    # Revert to VARCHAR(2000) for compatibility
    # Warning: This may truncate data if resumo exceeds 2000 characters
    with op.batch_alter_table('edu_content', schema=None) as batch_op:
        batch_op.alter_column('resumo',
                              existing_type=sa.Text(),
                              type_=sa.String(length=2000),
                              existing_nullable=True)
