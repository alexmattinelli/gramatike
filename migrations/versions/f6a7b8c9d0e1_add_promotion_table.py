"""add promotion table

Revision ID: f6a7b8c9d0e1
Revises: e5f6g7h8i9j0
Create Date: 2025-09-10 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f6a7b8c9d0e1'
down_revision = 'e5f6g7h8i9j0'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'promotion',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('titulo', sa.String(length=180), nullable=False),
        sa.Column('descricao', sa.String(length=400)),
        sa.Column('media_type', sa.String(length=20), nullable=False, server_default='image'),
        sa.Column('media_path', sa.String(length=500)),
        sa.Column('link_destino', sa.String(length=600)),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('ordem', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('user.id')),
    )
    op.create_index('ix_promotion_ativo', 'promotion', ['ativo'])
    op.create_index('ix_promotion_ordem', 'promotion', ['ordem'])
    op.create_index('ix_promotion_created_at', 'promotion', ['created_at'])

def downgrade():
    op.drop_index('ix_promotion_created_at', table_name='promotion')
    op.drop_index('ix_promotion_ordem', table_name='promotion')
    op.drop_index('ix_promotion_ativo', table_name='promotion')
    op.drop_table('promotion')
