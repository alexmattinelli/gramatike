# Gramátike TypeScript - Quick Start Guide

## 🚀 For New Users

### Prerequisites
- Node.js 18+
- npm or yarn
- Cloudflare account (for deployment)

### Local Development (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/alexmattinelli/gramatike.git
cd gramatike

# 2. Install dependencies
npm install

# 3. Run type check (optional but recommended)
npm run typecheck

# 4. Start development server
npm run dev
```

Your app is now running at `http://localhost:8788`

### Available API Endpoints

Test these in your browser or with curl:

```bash
# Health check
curl http://localhost:8788/api/health

# Register a user
curl -X POST http://localhost:8788/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:8788/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# List posts
curl http://localhost:8788/api/posts
```

## ☁️ Deploy to Cloudflare (10 minutes)

### First Time Setup

```bash
# 1. Login to Cloudflare
npx wrangler login

# 2. Create D1 database
npx wrangler d1 create gramatike
# Copy the database_id and update wrangler.toml

# 3. Initialize database
npx wrangler d1 execute gramatike --file=./schema.d1.sql

# 4. Create R2 bucket
npx wrangler r2 bucket create gramatike
```

### Deploy

```bash
npm run deploy
```

Your app is now live on Cloudflare Pages!

## 📁 Project Structure

```
gramatike/
├── functions/          # API endpoints (TypeScript)
├── src/               # Core libraries
├── public/            # Static assets
├── wrangler.toml      # Cloudflare config
└── package.json       # Dependencies
```

## 🔑 Environment Variables

Set these in Cloudflare Pages dashboard:

- `SECRET_KEY` - Random string for sessions (required)
- `MAIL_SERVER` - Email server (optional)
- `MAIL_PORT` - Email port (optional)
- `MAIL_USERNAME` - Email username (optional)
- `MAIL_PASSWORD` - Email password (optional)

## 📖 Full Documentation

- **README_TYPESCRIPT.md** - Comprehensive setup guide
- **MIGRATION_SUMMARY.md** - Migration details
- **VALIDATION_CHECKLIST.md** - Testing guide

## 🆘 Troubleshooting

### TypeScript errors
```bash
npm run typecheck
```

### Local dev not starting
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Database not working
```bash
# Reinitialize database
npx wrangler d1 execute gramatike --file=./schema.d1.sql
```

## 🎯 What's Working

✅ User authentication (register, login, logout)
✅ Post creation and listing
✅ User profiles
✅ Educational content
✅ Admin dashboard
✅ All API endpoints

## 💡 Tips

1. **Development**: Always run `npm run typecheck` before deploying
2. **Database**: Use D1 Studio to inspect your database
3. **Logs**: Use `wrangler pages deployment tail` to see logs
4. **Testing**: Test locally before deploying to production

## 🚀 Ready to Go!

Your TypeScript version of Gramátike is ready to use. Start with `npm run dev` and explore the API!

---

Questions? Check the full documentation in README_TYPESCRIPT.md
