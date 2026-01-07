# Changelog

## [2.1.0] - 2026-01-07

### ✅ Fixed
- Criado `public/index.html` principal com página inicial funcional
- Adicionado `functions/index.ts` para servir index.html
- Configurado `_headers` para segurança e cache
- Configurado `_routes.json` para routing correto
- Site agora carrega completamente (não mais "Hello world")

### 🎨 Added
- Página inicial com design moderno
- Navegação para todas as seções (Feed, Posts, Artigos, Apostilas)
- Informações sobre a plataforma
- Versioning visível

### 🚀 Performance
- Headers de cache otimizados
- Static assets com cache de 1 ano
- Templates com cache de 5 minutos

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
