# Database Migration Guide - February 2026

## Issue Fixed
This migration adds missing columns to fix the `/api/users/me` 500 error and like button persistence issues.

## Changes
- Adds `last_active` column to `users` table
- Adds `updated_at` column to `users` table
- Adds `updated_at` column to `posts` table

## How to Run the Migration

### For Production (Cloudflare D1)

```bash
# Run the migration on your remote D1 database
npx wrangler d1 execute gramatike --remote --file=./db/migrations/add_missing_columns.sql
```

### For Local Development

```bash
# Run the migration on your local D1 database
npx wrangler d1 execute gramatike --local --file=./db/migrations/add_missing_columns.sql
```

## Verification

After running the migration, verify the changes:

```bash
# Check the users table structure
npx wrangler d1 execute gramatike --remote --command="PRAGMA table_info(users);"

# Check the posts table structure
npx wrangler d1 execute gramatike --remote --command="PRAGMA table_info(posts);"
```

You should see the new columns:
- `users.last_active` (DATETIME)
- `users.updated_at` (DATETIME)  
- `posts.updated_at` (DATETIME)

## For Fresh Installations

If you're setting up a new database from scratch, use the updated schema:

```bash
npx wrangler d1 execute gramatike --remote --file=./db/schema.sql
```

The updated schema already includes all necessary columns.

## Rollback (if needed)

If you need to rollback the migration:

```sql
-- Remove the added columns
ALTER TABLE users DROP COLUMN last_active;
ALTER TABLE users DROP COLUMN updated_at;
ALTER TABLE posts DROP COLUMN updated_at;
```

**Note:** SQLite's `ALTER TABLE DROP COLUMN` requires SQLite 3.35.0+ (available in Cloudflare D1).
