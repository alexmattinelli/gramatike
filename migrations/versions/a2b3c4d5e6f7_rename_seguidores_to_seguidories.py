"""rename seguidores to seguidories

Revision ID: a2b3c4d5e6f7
Revises: 72c95270b966
Create Date: 2025-12-09 12:21:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a2b3c4d5e6f7'
down_revision = '72c95270b966'
branch_labels = None
depends_on = None

# SQL template for creating seguidories table
CREATE_SEGUIDORIES_SQL = """
    CREATE TABLE seguidories (
        seguidore_id INTEGER NOT NULL,
        seguide_id INTEGER NOT NULL,
        PRIMARY KEY (seguidore_id, seguide_id),
        FOREIGN KEY (seguidore_id) REFERENCES user(id),
        FOREIGN KEY (seguide_id) REFERENCES user(id)
    )
"""

CREATE_SEGUIDORES_SQL = """
    CREATE TABLE seguidores (
        seguidor_id INTEGER NOT NULL,
        seguido_id INTEGER NOT NULL,
        PRIMARY KEY (seguidor_id, seguido_id),
        FOREIGN KEY (seguidor_id) REFERENCES user(id),
        FOREIGN KEY (seguido_id) REFERENCES user(id)
    )
"""

def upgrade():
    """
    Rename seguidores table to seguidories and columns to use neutral gender:
    - seguidor_id -> seguidore_id
    - seguido_id -> seguide_id
    
    Handles three cases:
    1. Old table exists (seguidores) - migrate it
    2. New table already exists (seguidories) - skip
    3. Neither exists - create new table
    """
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'seguidores' in tables and 'seguidories' not in tables:
        # Case 1: Old table exists, migrate it
        if conn.dialect.name == 'sqlite':
            # SQLite doesn't support ALTER TABLE RENAME COLUMN
            # Create new table, copy data, drop old
            op.execute(CREATE_SEGUIDORIES_SQL)
            op.execute("""
                INSERT INTO seguidories (seguidore_id, seguide_id)
                SELECT seguidor_id, seguido_id FROM seguidores
            """)
            op.drop_table('seguidores')
        else:
            # PostgreSQL supports direct renaming
            op.rename_table('seguidores', 'seguidories')
            op.alter_column('seguidories', 'seguidor_id', new_column_name='seguidore_id')
            op.alter_column('seguidories', 'seguido_id', new_column_name='seguide_id')
    
    elif 'seguidories' in tables:
        # Case 2: New table already exists - migration already applied or schema correct
        pass
    
    else:
        # Case 3: Neither table exists - create new table with correct naming
        op.execute(CREATE_SEGUIDORIES_SQL)


def downgrade():
    """
    Revert seguidories table to seguidores and columns to masculine gender:
    - seguidore_id -> seguidor_id
    - seguide_id -> seguido_id
    """
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'seguidories' in tables and 'seguidores' not in tables:
        # Revert the migration
        if conn.dialect.name == 'sqlite':
            op.execute(CREATE_SEGUIDORES_SQL)
            op.execute("""
                INSERT INTO seguidores (seguidor_id, seguido_id)
                SELECT seguidore_id, seguide_id FROM seguidories
            """)
            op.drop_table('seguidories')
        else:
            # PostgreSQL
            op.rename_table('seguidories', 'seguidores')
            op.alter_column('seguidores', 'seguidore_id', new_column_name='seguidor_id')
            op.alter_column('seguidores', 'seguide_id', new_column_name='seguido_id')

