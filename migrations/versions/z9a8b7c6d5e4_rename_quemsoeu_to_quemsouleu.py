"""rename quemsoeu to quemsouleu

Revision ID: z9a8b7c6d5e4
Revises: x56rn24y9zwi
Create Date: 2025-10-14 13:33:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'z9a8b7c6d5e4'
down_revision = 'x56rn24y9zwi'
branch_labels = None
depends_on = None

def upgrade():
    # Update all dynamic records with tipo='quemsoeu' to tipo='quemsouleu'
    op.execute("UPDATE dynamic SET tipo = 'quemsouleu' WHERE tipo = 'quemsoeu'")


def downgrade():
    # Revert quemsouleu back to quemsoeu
    op.execute("UPDATE dynamic SET tipo = 'quemsoeu' WHERE tipo = 'quemsouleu'")
