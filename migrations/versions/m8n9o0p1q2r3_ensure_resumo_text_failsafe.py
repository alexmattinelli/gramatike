"""Ensure resumo field is TEXT (failsafe migration)

Revision ID: m8n9o0p1q2r3
Revises: j9k0l1m2n3o4
Create Date: 2025-10-16 12:30:00.000000

This is a failsafe migration to ensure resumo is TEXT type.
It's completely idempotent and will work regardless of current state.
This fixes the VARCHAR(400) truncation error in production.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'm8n9o0p1q2r3'
down_revision = 'j9k0l1m2n3o4'
branch_labels = None
depends_on = None

def upgrade():
    # Failsafe: Ensure resumo is TEXT
    # This is idempotent and safe to run even if resumo is already TEXT
    # Uses PostgreSQL conditional logic to avoid errors
    op.execute("""
        DO $$ 
        BEGIN
            -- Check if resumo column exists and is not TEXT
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'edu_content' 
                  AND column_name = 'resumo'
                  AND data_type <> 'text'
            ) THEN
                -- Convert to TEXT (works from any VARCHAR size)
                ALTER TABLE edu_content ALTER COLUMN resumo TYPE TEXT;
                RAISE NOTICE 'Successfully converted resumo column to TEXT';
            ELSE
                -- Column is already TEXT or doesn't exist
                IF EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_name = 'edu_content' 
                      AND column_name = 'resumo'
                      AND data_type = 'text'
                ) THEN
                    RAISE NOTICE 'resumo column is already TEXT - no action needed';
                ELSE
                    RAISE WARNING 'resumo column not found in edu_content table';
                END IF;
            END IF;
        END $$;
    """)

def downgrade():
    # Revert to VARCHAR(2000) for compatibility
    # Warning: This may truncate data if resumo exceeds 2000 characters
    op.execute("ALTER TABLE edu_content ALTER COLUMN resumo TYPE VARCHAR(2000)")
