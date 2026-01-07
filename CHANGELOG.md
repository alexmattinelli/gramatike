# Changelog

## [2.0.0-typescript-only] - 2026-01-07

### 🚀 BREAKING CHANGES
- **Migração completa de Python para TypeScript**
- Removidos TODOS os arquivos Python
- Runtime: Cloudflare Pages Functions (Node.js/TypeScript)
- Performance: 10-20x mais rápido que Python/Pyodide

### ✅ Added
- TypeScript 100% code base
- Cloudflare Pages Functions
- D1 Database bindings
- R2 Storage bindings
- `.cfpagesignore` to block Python detection by Cloudflare
- `VERSION` file to mark TypeScript-only version
- GitHub Actions workflow to validate no Python files
- `clean:python` npm script to ensure no Python artifacts
- `prebuild` npm script that runs before build

### ❌ Removed
- Python runtime
- requirements.txt
- Todos os arquivos .py
- Python Workers compatibility

### 🔒 Security
- Bloqueio permanente de arquivos Python via .gitignore
- Bloqueio de deploy Python via .cfpagesignore
- Validação automática via GitHub Actions

### 📝 Documentation
- Updated README.md with TypeScript-only notice
- Updated wrangler.toml with explicit runtime configuration
- Created VERSION file for version tracking
