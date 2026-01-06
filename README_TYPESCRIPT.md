# Gramátike - TypeScript Migration

## Overview

This is the TypeScript version of Gramátike, migrated from Python/Flask to TypeScript with Cloudflare Pages Functions.

## Tech Stack

- **Runtime**: Cloudflare Pages Functions (TypeScript)
- **Database**: Cloudflare D1 (SQLite on the edge)
- **Storage**: Cloudflare R2 (file uploads)
- **Authentication**: Session-based with D1
- **Type Safety**: TypeScript with strict mode

## Project Structure

```
gramatike/
├── functions/              # Cloudflare Pages Functions
│   ├── _middleware.ts     # Auth middleware
│   └── api/               # API endpoints
│       ├── auth/          # Login, register, logout
│       ├── posts/         # Posts CRUD and likes
│       ├── users/         # User profiles and settings
│       ├── education/     # Educational content
│       └── admin/         # Admin dashboard
├── src/                   # Source code
│   ├── lib/              # Core libraries
│   │   ├── db.ts         # Database helpers
│   │   ├── auth.ts       # Authentication
│   │   ├── crypto.ts     # Password hashing
│   │   └── utils.ts      # Utilities
│   └── types/            # TypeScript types
│       └── index.ts      # Type definitions
├── public/               # Static assets
│   ├── static/           # CSS, JS, images
│   └── templates/        # HTML templates
├── wrangler.toml         # Cloudflare configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies
```

## Setup

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Wrangler CLI (`npm install -g wrangler`)

### Installation

```bash
# Install dependencies
npm install

# Login to Cloudflare (first time only)
wrangler login

# Create D1 database (first time only)
wrangler d1 create gramatike

# Initialize database with schema
wrangler d1 execute gramatike --file=./schema.d1.sql

# Create R2 bucket (first time only)
wrangler r2 bucket create gramatike
```

### Development

```bash
# Start development server
npm run dev

# Type check
npm run typecheck

# Build
npm run build
```

### Deployment

```bash
# Deploy to Cloudflare Pages
npm run deploy

# Or use Wrangler directly
wrangler pages deploy public
```

## Environment Variables

Set these in Cloudflare Pages dashboard or `.dev.vars` for local development:

- `SECRET_KEY` - Secret key for sessions
- `MAIL_SERVER` - Email server (optional)
- `MAIL_PORT` - Email port (optional)
- `MAIL_USERNAME` - Email username (optional)
- `MAIL_PASSWORD` - Email password (optional)

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout

### Posts
- `GET /api/posts` - List posts
- `POST /api/posts` - Create post (auth required)
- `GET /api/posts/[id]` - Get post by ID
- `DELETE /api/posts/[id]` - Delete post (auth required)
- `POST /api/posts/like` - Like/unlike post (auth required)

### Users
- `GET /api/users/[id]` - Get user profile
- `GET /api/users/settings` - Get current user settings (auth required)
- `PATCH /api/users/settings` - Update settings (auth required)

### Education
- `GET /api/education` - List educational content
- `GET /api/education/[id]` - Get specific content
- `POST /api/education/create` - Create content (admin only)

### Admin
- `GET /api/admin/stats` - Dashboard statistics (admin only)

## Features

✅ User authentication (register, login, logout)  
✅ Session management with D1  
✅ Password hashing with Web Crypto API  
✅ Posts (create, list, like, comment)  
✅ User profiles  
✅ Educational content  
✅ Admin dashboard  
✅ Type-safe with TypeScript  
✅ Fast (native JavaScript, no Pyodide)  

## Performance

TypeScript on Cloudflare Workers is significantly faster than Python/Pyodide:
- ~10-20x faster execution
- Lower memory usage
- Better cold start times
- Native edge performance

## Migration from Python

The Python version is still in the repository for reference. Key differences:

- **Language**: TypeScript instead of Python
- **Framework**: Cloudflare Pages Functions instead of Flask
- **Database**: Same D1 schema, different query syntax
- **Auth**: Custom session management instead of Flask-Login
- **Templates**: Static HTML (to be served via functions or static hosting)

## Database Schema

The database schema (`schema.d1.sql`) remains the same as the Python version. No migration needed!

## Contributing

1. Make changes
2. Run type check: `npm run typecheck`
3. Test locally: `npm run dev`
4. Deploy: `npm run deploy`

## License

Same as the original Gramátike project.
