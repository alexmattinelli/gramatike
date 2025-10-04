"""add is_superadmin to user

Revision ID: a1c2d3e4f5b6
Revises: 8cb28843b536
Create Date: 2025-08-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1c2d3e4f5b6'
down_revision = '8cb28843b536'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_superadmin', sa.Boolean(), nullable=True))
    # Preenche False default (SQLite não aplica server_default retroativo automaticamente)
    op.execute("UPDATE user SET is_superadmin = 0 WHERE is_superadmin IS NULL")


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_superadmin')
