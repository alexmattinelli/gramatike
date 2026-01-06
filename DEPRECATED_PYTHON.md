# DEPRECATED - Python Code

⚠️ **This directory contains the legacy Python/Flask implementation.**

The project has been migrated to **TypeScript with Cloudflare Pages Functions**.

## New Structure

The new TypeScript implementation is in:
- `functions/` - API endpoints (TypeScript)
- `src/` - Core libraries and types
- `public/` - Static assets and templates

## Migration Status

✅ All functionality has been reimplemented in TypeScript  
✅ Database schema remains the same (D1)  
✅ Static assets have been copied to `public/`  

## Why Keep This?

This Python code is kept temporarily for:
1. **Reference** - To verify TypeScript implementation matches functionality
2. **Rollback** - In case issues are discovered with the TypeScript version
3. **Documentation** - Understanding business logic

## When Will This Be Removed?

After the TypeScript version has been:
- Thoroughly tested
- Deployed to production
- Running successfully for 1-2 weeks

Then this directory can be safely deleted.

## Don't Use This Code

❌ Do not deploy or run the Python code  
❌ Do not make changes to Python files  
✅ Use the TypeScript implementation instead  

See `README_TYPESCRIPT.md` for the new setup instructions.
