-- Migration: Add missing columns to users and posts tables
-- Date: 2026-02-05

-- Add last_active and updated_at to users table
ALTER TABLE users ADD COLUMN last_active DATETIME DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE users ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Add updated_at to posts table
ALTER TABLE posts ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Add banned column alias (view) - but since SQLite doesn't support computed columns easily,
-- we'll handle this in the application code by using is_banned
