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

def upgrade():
    """
    Rename seguidores table to seguidories and columns to use neutral gender:
    - seguidor_id -> seguidore_id
    - seguido_id -> seguide_id
    """
    conn = op.get_bind()
    
    # Check if table exists with old name
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'seguidores' in tables:
        # SQLite doesn't support ALTER TABLE RENAME COLUMN directly
        # We need to recreate the table with the new name and column names
        if conn.dialect.name == 'sqlite':
            # Create new table with neutral gender terminology
            op.execute("""
                CREATE TABLE seguidories (
                    seguidore_id INTEGER NOT NULL,
                    seguide_id INTEGER NOT NULL,
                    PRIMARY KEY (seguidore_id, seguide_id),
                    FOREIGN KEY (seguidore_id) REFERENCES user(id),
                    FOREIGN KEY (seguide_id) REFERENCES user(id)
                )
            """)
            
            # Copy data from old table to new table
            op.execute("""
                INSERT INTO seguidories (seguidore_id, seguide_id)
                SELECT seguidor_id, seguido_id FROM seguidores
            """)
            
            # Drop old table
            op.drop_table('seguidores')
        else:
            # PostgreSQL supports table and column renaming
            op.rename_table('seguidores', 'seguidories')
            op.alter_column('seguidories', 'seguidor_id', new_column_name='seguidore_id')
            op.alter_column('seguidories', 'seguido_id', new_column_name='seguide_id')
    
    # If the table already exists with the new name, skip
    elif 'seguidories' not in tables:
        # Table doesn't exist at all, create it with neutral gender terminology
        op.execute("""
            CREATE TABLE seguidories (
                seguidore_id INTEGER NOT NULL,
                seguide_id INTEGER NOT NULL,
                PRIMARY KEY (seguidore_id, seguide_id),
                FOREIGN KEY (seguidore_id) REFERENCES user(id),
                FOREIGN KEY (seguide_id) REFERENCES user(id)
            )
        """)


def downgrade():
    """
    Revert seguidories table to seguidores and columns to masculine gender:
    - seguidore_id -> seguidor_id
    - seguide_id -> seguido_id
    """
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'seguidories' in tables:
        if conn.dialect.name == 'sqlite':
            # Create old table with masculine gender terminology
            op.execute("""
                CREATE TABLE seguidores (
                    seguidor_id INTEGER NOT NULL,
                    seguido_id INTEGER NOT NULL,
                    PRIMARY KEY (seguidor_id, seguido_id),
                    FOREIGN KEY (seguidor_id) REFERENCES user(id),
                    FOREIGN KEY (seguido_id) REFERENCES user(id)
                )
            """)
            
            # Copy data from new table to old table
            op.execute("""
                INSERT INTO seguidores (seguidor_id, seguido_id)
                SELECT seguidore_id, seguide_id FROM seguidories
            """)
            
            # Drop new table
            op.drop_table('seguidories')
        else:
            # PostgreSQL
            op.rename_table('seguidories', 'seguidores')
            op.alter_column('seguidores', 'seguidore_id', new_column_name='seguidor_id')
            op.alter_column('seguidores', 'seguide_id', new_column_name='seguido_id')
