"""add edu content tables and soft delete

Revision ID: c1d2e3f4g5h6
Revises: b7c9d10e11f2
Create Date: 2025-08-12 12:10:00.000000
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'c1d2e3f4g5h6'
down_revision = 'b7c9d10e11f2'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('user', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('post', sa.Column('is_deleted', sa.Boolean(), nullable=True))
    op.add_column('post', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('post', sa.Column('deleted_by', sa.Integer(), nullable=True))
    op.create_index('ix_post_is_deleted', 'post', ['is_deleted'])
    op.create_index('ix_user_created_at', 'user', ['created_at'])
    op.create_table('edu_content',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tipo', sa.String(length=40), nullable=False, index=True),
        sa.Column('titulo', sa.String(length=220), nullable=False),
        sa.Column('resumo', sa.String(length=400)),
        sa.Column('corpo', sa.Text()),
        sa.Column('url', sa.String(length=500)),
        sa.Column('file_path', sa.String(length=500)),
        sa.Column('extra', sa.Text()),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, index=True),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('user.id'))
    )
    op.create_table('exercise_topic',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nome', sa.String(length=150), nullable=False),
        sa.Column('descricao', sa.Text()),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow)
    )
    op.create_table('exercise_question',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('topic_id', sa.Integer(), sa.ForeignKey('exercise_topic.id'), nullable=False, index=True),
        sa.Column('enunciado', sa.Text(), nullable=False),
        sa.Column('resposta', sa.Text()),
        sa.Column('dificuldade', sa.String(length=30)),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow)
    )


def downgrade():
    op.drop_table('exercise_question')
    op.drop_table('exercise_topic')
    op.drop_table('edu_content')
    op.drop_index('ix_post_is_deleted', table_name='post')
    op.drop_index('ix_user_created_at', table_name='user')
    op.drop_column('post', 'deleted_by')
    op.drop_column('post', 'deleted_at')
    op.drop_column('post', 'is_deleted')
    op.drop_column('user', 'created_at')
