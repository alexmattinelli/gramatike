# Deploy Gramátike no Cloudflare

## ⚠️ IMPORTANTE: Este projeto usa Cloudflare Workers, NÃO Pages Functions

**Cloudflare Pages Functions não suporta `requirements.txt` ainda.**

Se você está vendo o erro:
> "You cannot yet deploy Python Workers that depend on packages defined in requirements.txt"

É porque está tentando usar Pages Functions. **Use Cloudflare Workers em vez disso.**

## ✅ Deploy Correto (Cloudflare Workers)

```bash
# 1. Instalar uv (gerenciador de pacotes Python)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Instalar dependências
npm install
uv sync

# 3. Autenticar (se necessário)
npx wrangler login

# 4. Deploy
npm run deploy
```

## 📖 Guia Completo

Veja o guia completo de deployment em: **[CLOUDFLARE_DEPLOYMENT_GUIDE.md](CLOUDFLARE_DEPLOYMENT_GUIDE.md)**

O guia inclui:
- Diferenças entre Workers e Pages Functions
- Configuração completa de variáveis de ambiente
- Gerenciamento de dependências via `pyproject.toml`
- Troubleshooting de erros comuns
- Deploy via GitHub Actions

## 🔧 Configuração Rápida

1. **D1 Database:**
   ```bash
   wrangler d1 create gramatike
   wrangler d1 execute gramatike --file=./schema.d1.sql
   ```

2. **Variáveis de Ambiente:**
   - Configure no dashboard: Workers & Pages > Gramátike > Settings > Variables
   - Mínimo: `SECRET_KEY`

3. **Deploy:**
   ```bash
   npm run deploy
   ```

## ❌ NÃO Use Pages Functions

O diretório `functions/` e o arquivo `_pages.toml` são mantidos por compatibilidade, mas **não são usados para deployment**.

**Deployment correto:**
- ✅ Via `wrangler.toml` (Workers)
- ✅ Entry point: `index.py`
- ✅ Dependências: `pyproject.toml`
- ✅ Comando: `npm run deploy`

**NÃO use:**
- ❌ Git push para Pages
- ❌ Build command com `requirements.txt`
- ❌ Pages Functions com dependências Python
