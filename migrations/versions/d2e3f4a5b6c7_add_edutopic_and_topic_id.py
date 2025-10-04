"""add EduTopic and topic_id to EduContent

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4g5h6
Create Date: 2025-08-12
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd2e3f4a5b6c7'
down_revision = 'c1d2e3f4g5h6'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('edu_topic',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('area', sa.String(length=40), nullable=False),
        sa.Column('nome', sa.String(length=150), nullable=False),
        sa.Column('descricao', sa.Text()),
        sa.Column('created_at', sa.DateTime()),
        sa.UniqueConstraint('area','nome', name='uix_area_nome')
    )
    op.create_index('ix_edu_topic_area', 'edu_topic', ['area'])
    op.create_index('ix_edu_topic_created_at', 'edu_topic', ['created_at'])
    with op.batch_alter_table('edu_content') as batch:
        batch.add_column(sa.Column('topic_id', sa.Integer(), nullable=True))
        batch.create_foreign_key('fk_edu_content_topic','edu_topic','id', ['topic_id'], ['id'])


def downgrade():
    with op.batch_alter_table('edu_content') as batch:
        batch.drop_constraint('fk_edu_content_topic', type_='foreignkey')
        batch.drop_column('topic_id')
    op.drop_table('edu_topic')
