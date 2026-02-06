# Cloudflare Pages Deployment Fix

## Problem

The Cloudflare Pages deployment was failing with the following error:

```
Error: Failed to publish your Function. Got error: Uncaught ReferenceError: process is not defined
  at functionsWorker-0.8868856398262266.js:2408:5 in ../src/lib/airtable.ts
```

## Root Cause

The error occurred because Node.js-specific development server files and dependencies were being bundled into the Cloudflare Workers deployment:

1. **Development Server Files**: 
   - `dev-server.js` uses `process.env.PORT` and Express framework
   - `simple-server.cjs` uses Node.js built-in modules (`http`, `fs`, `path`)
   - Both files are intended ONLY for local development

2. **Express Dependency**: 
   - Listed as a production dependency in `package.json`
   - Express and its dependencies include Node.js-specific code
   - Cloudflare Workers runtime doesn't support Node.js globals like `process`, `fs`, etc.

3. **Missing Ignore Rules**:
   - Development server files were not excluded in `.cfignore` and `.cfpagesignore`
   - This caused them to be included in the Cloudflare Pages build

## Solution

### 1. Moved Express to devDependencies

**File**: `package.json`

```diff
- "dependencies": {
-   "express": "^5.2.1"
- }
  "devDependencies": {
    "@cloudflare/workers-types": "^4.20260108.0",
+   "express": "^5.2.1",
    "typescript": "^5.3.0",
    "wrangler": "^4.58.0"
  }
```

**Why**: Express is only needed for local development with `dev-server.js` and `simple-server.cjs`. It should not be deployed to Cloudflare Pages.

### 2. Updated .cfignore

**File**: `.cfignore`

Added the following lines:

```
# Development server files (Node.js only - not for Cloudflare Workers)
dev-server.js
simple-server.cjs
```

**Why**: Ensures Cloudflare deployment tools ignore these Node.js-specific files.

### 3. Updated .cfpagesignore

**File**: `.cfpagesignore`

Added comprehensive ignore rules:

```
# Development server files (Node.js only - not for Cloudflare Workers)
dev-server.js
simple-server.cjs

# Node modules and build artifacts
node_modules/
.wrangler/
.mf/

# Environment and config files
.env
.env.*
.git/

# IDE and temporary files
.vscode/
.idea/
.DS_Store
*.tmp
tmp/
temp/
*.log
*.backup
*.bak
```

**Why**: Ensures Cloudflare Pages ignores all development-only files during deployment.

## How Local Development Works

The project uses different server files for different purposes:

| File | Purpose | Runtime | Command |
|------|---------|---------|---------|
| `dev-server.js` | Simple Express server for local testing | Node.js | `node dev-server.js` |
| `simple-server.cjs` | Alternative simple HTTP server | Node.js | `node simple-server.cjs` |
| `functions/**/*.ts` | Cloudflare Pages Functions (production) | Cloudflare Workers | `wrangler pages dev` |

## How Production Deployment Works

When deploying to Cloudflare Pages:

1. **Build Phase**: 
   - Runs `npm run build` (currently just echoes success)
   - No bundling of Node.js code needed

2. **Deployment Phase**:
   - Uploads `public/` directory with static HTML files
   - Uploads `functions/` directory with TypeScript serverless functions
   - Ignores files listed in `.cfignore` and `.cfpagesignore`
   - Wrangler transpiles TypeScript functions to JavaScript compatible with Cloudflare Workers

3. **Runtime**:
   - Static files served from CDN
   - Functions run in Cloudflare Workers runtime (NOT Node.js)
   - Uses Web APIs and Cloudflare-specific APIs (D1, R2, etc.)
   - Does NOT support Node.js globals like `process`, `fs`, `http`, etc.

## Configuration Files

### wrangler.toml

The configuration is correct:

```toml
name = "gramatike"
compatibility_date = "2026-01-08"
compatibility_flags = ["nodejs_compat"]
pages_build_output_dir = "public"
```

**Note**: `nodejs_compat` provides some Node.js compatibility (like `Buffer`, `process.env` access in Worker context) but does NOT enable full Node.js runtime. It's for compatibility with npm packages, not for running Node.js code.

## Verification

After these changes, the deployment should succeed because:

1. ✅ No Node.js-specific code is bundled
2. ✅ All functions use Cloudflare Workers APIs only
3. ✅ Development dependencies are not included in production
4. ✅ Development server files are excluded from deployment

## Local Development Commands

```bash
# For local development with mock data (Node.js)
node dev-server.js
# or
node simple-server.cjs

# For local development with Cloudflare Pages (Wrangler)
npm run dev

# Deploy to Cloudflare Pages
npm run deploy
```

## Related Files

- `functions/**/*.ts` - Serverless functions that run on Cloudflare Workers
- `src/lib/*.ts` - Utility functions compatible with Cloudflare Workers
- `public/*.html` - Static HTML files
- `wrangler.toml` - Cloudflare configuration
- `tsconfig.json` - TypeScript configuration

## Key Takeaways

1. **Separation of Concerns**: Development server files (Node.js) are separate from production functions (Cloudflare Workers)
2. **Dependencies**: Only devDependencies for local development, no production dependencies needed
3. **Ignore Files**: Always update `.cfignore` and `.cfpagesignore` when adding development-only files
4. **Runtime Awareness**: Cloudflare Workers is not Node.js - use Web APIs and Cloudflare-specific APIs only
