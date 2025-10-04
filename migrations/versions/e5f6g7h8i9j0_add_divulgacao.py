"""add divulgacao table

Revision ID: e5f6g7h8i9j0
Revises: d2e3f4a5b6c7
Create Date: 2025-08-23 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e5f6g7h8i9j0'
down_revision = 'd2e3f4a5b6c7'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'divulgacao',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('area', sa.String(length=20), nullable=False, index=True),
        sa.Column('titulo', sa.String(length=180), nullable=False),
        sa.Column('texto', sa.Text()),
        sa.Column('link', sa.String(length=400)),
        sa.Column('imagem', sa.String(length=400)),
        sa.Column('ordem', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('edu_content_id', sa.Integer(), sa.ForeignKey('edu_content.id')),
        sa.Column('post_id', sa.Integer(), sa.ForeignKey('post.id')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index('ix_divulgacao_area', 'divulgacao', ['area'])
    op.create_index('ix_divulgacao_ativo', 'divulgacao', ['ativo'])
    op.create_index('ix_divulgacao_ordem', 'divulgacao', ['ordem'])


def downgrade():
    op.drop_index('ix_divulgacao_ordem', table_name='divulgacao')
    op.drop_index('ix_divulgacao_ativo', table_name='divulgacao')
    op.drop_index('ix_divulgacao_area', table_name='divulgacao')
    op.drop_table('divulgacao')
