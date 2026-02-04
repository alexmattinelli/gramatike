-- Migration: Add bio, genero, and pronome columns to users table
-- Date: 2026-02-04

-- Add bio column
ALTER TABLE users ADD COLUMN bio TEXT;

-- Add genero column  
ALTER TABLE users ADD COLUMN genero TEXT;

-- Add pronome column
ALTER TABLE users ADD COLUMN pronome TEXT;
