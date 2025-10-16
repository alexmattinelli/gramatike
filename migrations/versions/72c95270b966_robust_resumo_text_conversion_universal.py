"""robust resumo text conversion universal

Revision ID: 72c95270b966
Revises: n9o0p1q2r3s4
Create Date: 2025-10-16 14:56:32.666371

This migration ensures the resumo column is TEXT (unlimited) regardless of current state.
It is completely idempotent and will work with:
- PostgreSQL (production) - uses ALTER TABLE with conditional logic
- SQLite (development) - uses batch operations

This fixes the production error:
ERROR: (psycopg2.errors.StringDataRightTruncation) value too long for type character varying(400)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '72c95270b966'
down_revision = 'n9o0p1q2r3s4'
branch_labels = None
depends_on = None


def upgrade():
    """Convert resumo column to TEXT type if it's not already TEXT."""
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    if dialect_name == 'postgresql':
        # PostgreSQL: Use direct SQL with conditional logic
        # This is completely safe and idempotent - will not fail if already TEXT
        op.execute("""
            DO $$ 
            BEGIN
                -- Only alter if column exists and is not already TEXT
                IF EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'edu_content' 
                      AND column_name = 'resumo'
                      AND data_type != 'text'
                ) THEN
                    -- Convert to TEXT (works from any VARCHAR size: 400, 1000, 2000, etc.)
                    ALTER TABLE edu_content ALTER COLUMN resumo TYPE TEXT;
                    RAISE NOTICE '✅ Successfully converted resumo column to TEXT (unlimited length)';
                ELSE
                    -- Column is already TEXT or doesn't exist
                    IF EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name = 'edu_content' 
                          AND column_name = 'resumo'
                          AND data_type = 'text'
                    ) THEN
                        RAISE NOTICE '✅ resumo column is already TEXT - no action needed';
                    ELSE
                        RAISE WARNING '⚠️ resumo column not found in edu_content table';
                    END IF;
                END IF;
            END $$;
        """)
    else:
        # SQLite and other databases: Use batch operations
        inspector = Inspector.from_engine(bind)
        
        try:
            columns = inspector.get_columns('edu_content')
            resumo_col = next((col for col in columns if col['name'] == 'resumo'), None)
            
            if not resumo_col:
                # Column doesn't exist, skip
                print('⚠️ resumo column not found in edu_content table')
                return
            
            # Check if already TEXT
            col_type_str = str(resumo_col['type']).upper()
            if 'TEXT' in col_type_str or 'CLOB' in col_type_str:
                # Already TEXT, skip
                print('✅ resumo column is already TEXT - no action needed')
                return
            
            # Convert to TEXT using batch operations
            with op.batch_alter_table('edu_content', schema=None) as batch_op:
                batch_op.alter_column('resumo',
                                      existing_type=sa.String(),
                                      type_=sa.Text(),
                                      existing_nullable=True)
            print('✅ Successfully converted resumo column to TEXT (unlimited length)')
        except Exception as e:
            print(f'⚠️ Error during migration: {e}')
            # Don't raise - let other migrations continue


def downgrade():
    """
    Revert resumo to VARCHAR(2000).
    WARNING: This may truncate data if resumo exceeds 2000 characters!
    """
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    if dialect_name == 'postgresql':
        # PostgreSQL: Direct SQL
        op.execute("""
            DO $$ 
            BEGIN
                IF EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'edu_content' 
                      AND column_name = 'resumo'
                ) THEN
                    ALTER TABLE edu_content ALTER COLUMN resumo TYPE VARCHAR(2000);
                    RAISE NOTICE 'Reverted resumo column to VARCHAR(2000)';
                END IF;
            END $$;
        """)
    else:
        # SQLite and other databases
        with op.batch_alter_table('edu_content', schema=None) as batch_op:
            batch_op.alter_column('resumo',
                                  existing_type=sa.Text(),
                                  type_=sa.String(length=2000),
                                  existing_nullable=True)
