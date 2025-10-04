"""add moderation fields

Revision ID: b7c9d10e11f2
Revises: a1c2d3e4f5b6
Create Date: 2025-08-12 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b7c9d10e11f2'
down_revision = 'a1c2d3e4f5b6'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_banned', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('banned_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('ban_reason', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('suspended_until', sa.DateTime(), nullable=True))
    with op.batch_alter_table('report', schema=None) as batch_op:
        batch_op.add_column(sa.Column('resolved', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('resolved_at', sa.DateTime(), nullable=True))
    op.execute("UPDATE user SET is_banned = 0 WHERE is_banned IS NULL")
    op.execute("UPDATE report SET resolved = 0 WHERE resolved IS NULL")


def downgrade():
    with op.batch_alter_table('report', schema=None) as batch_op:
        batch_op.drop_column('resolved_at')
        batch_op.drop_column('resolved')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('suspended_until')
        batch_op.drop_column('ban_reason')
        batch_op.drop_column('banned_at')
        batch_op.drop_column('is_banned')
