"""add palavra do dia tables

Revision ID: h7i8j9k0l1m2
Revises: g1h2i3j4k5l6
Create Date: 2025-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'h7i8j9k0l1m2'
down_revision = 'g1h2i3j4k5l6'
branch_labels = None
depends_on = None

def upgrade():
    # Create palavra_do_dia table
    op.create_table('palavra_do_dia',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('palavra', sa.String(length=200), nullable=False),
        sa.Column('significado', sa.Text(), nullable=False),
        sa.Column('ordem', sa.Integer(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('palavra_do_dia', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_palavra_do_dia_ativo'), ['ativo'], unique=False)
        batch_op.create_index(batch_op.f('ix_palavra_do_dia_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_palavra_do_dia_created_by'), ['created_by'], unique=False)
        batch_op.create_index(batch_op.f('ix_palavra_do_dia_ordem'), ['ordem'], unique=False)

    # Create palavra_do_dia_interacao table
    op.create_table('palavra_do_dia_interacao',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('palavra_id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('frase', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['palavra_id'], ['palavra_do_dia.id'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('palavra_do_dia_interacao', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_palavra_do_dia_interacao_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_palavra_do_dia_interacao_palavra_id'), ['palavra_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_palavra_do_dia_interacao_usuario_id'), ['usuario_id'], unique=False)


def downgrade():
    with op.batch_alter_table('palavra_do_dia_interacao', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_palavra_do_dia_interacao_usuario_id'))
        batch_op.drop_index(batch_op.f('ix_palavra_do_dia_interacao_palavra_id'))
        batch_op.drop_index(batch_op.f('ix_palavra_do_dia_interacao_created_at'))

    op.drop_table('palavra_do_dia_interacao')

    with op.batch_alter_table('palavra_do_dia', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_palavra_do_dia_ordem'))
        batch_op.drop_index(batch_op.f('ix_palavra_do_dia_created_by'))
        batch_op.drop_index(batch_op.f('ix_palavra_do_dia_created_at'))
        batch_op.drop_index(batch_op.f('ix_palavra_do_dia_ativo'))

    op.drop_table('palavra_do_dia')
