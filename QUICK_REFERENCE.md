# Quick Reference - Cloudflare Workers Deployment

## 🚀 Deploy Rápido

```bash
npm run deploy
```

## 📋 Comandos Essenciais

### Setup Inicial

```bash
# 1. Instalar uv (uma vez)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Instalar dependências
npm install
uv sync

# 3. Autenticar (uma vez)
npx wrangler login
```

### Desenvolvimento Local

```bash
# Modo dev (hot reload)
npm run dev

# Ou
npx wrangler dev
```

### Deploy

```bash
# Deploy padrão
npm run deploy

# Deploy com force (ignora cache)
npx wrangler deploy --force

# Deploy com logs
npx wrangler deploy --verbose
```

### Gerenciar D1 Database

```bash
# Criar banco (uma vez)
npx wrangler d1 create gramatike

# Criar/atualizar schema
npx wrangler d1 execute gramatike --file=./schema.d1.sql

# Query direto
npx wrangler d1 execute gramatike --command="SELECT * FROM users LIMIT 5"

# Backup
npx wrangler d1 export gramatike --output=backup.sql
```

### Gerenciar Secrets

```bash
# Adicionar secret
npx wrangler secret put SECRET_KEY

# Listar secrets
npx wrangler secret list

# Deletar secret
npx wrangler secret delete SECRET_KEY
```

### Logs e Monitoramento

```bash
# Ver logs em tempo real
npx wrangler tail

# Ver logs com filtro
npx wrangler tail --status error

# Ver deployment info
npx wrangler deployments list
```

### Adicionar Dependências

```bash
# Adicionar pacote
uv add nome-do-pacote

# Adicionar pacote de dev
uv add --dev nome-do-pacote

# Remover pacote
uv remove nome-do-pacote

# Atualizar dependências
uv sync
```

## ❌ Erros Comuns

### "You cannot yet deploy Python Workers that depend on packages defined in requirements.txt"

**Problema:** Tentando usar Pages Functions com requirements.txt.

**Solução:** Use Workers deployment via `npm run deploy`.

### "Package not found" ou "Module not importable"

**Problema:** Pacote não compatível com Pyodide.

**Solução:** Verifique se o pacote é pure-Python ou está na [lista do Pyodide](https://pyodide.org/en/stable/usage/packages-in-pyodide.html).

### Changes não aparecem após deploy

**Problema:** Cache.

**Solução:**
```bash
npx wrangler deploy --force
```

### D1 Error: "no such table"

**Problema:** Schema não aplicado.

**Solução:**
```bash
npx wrangler d1 execute gramatike --file=./schema.d1.sql
```

## 📁 Estrutura de Arquivos

```
gramatike/
├── index.py                    # ← Entry point do Worker
├── wrangler.toml               # ← Configuração do Worker
├── pyproject.toml              # ← Dependências (via uv)
├── uv.lock                     # ← Lock file de dependências
├── package.json                # ← Scripts npm
├── schema.d1.sql               # ← Schema do banco D1
├── _pages.toml                 # (não usado - mantido para compatibilidade)
├── requirements.txt            # (não usado - apenas dev local)
├── functions/                  # (não usado - código está no index.py)
└── gramatike_app/
    └── static/                 # ← Assets estáticos
```

## 🔧 Configuração

### Variáveis no Cloudflare Dashboard

**Workers & Pages > gramatike > Settings > Variables**

Obrigatórias:
- `SECRET_KEY` (string segura, 32+ chars)

Opcionais:
- `MAIL_SERVER`
- `MAIL_PORT`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_DEFAULT_SENDER`

### Bindings (wrangler.toml)

```toml
# D1 Database
[[d1_databases]]
binding = "DB"
database_name = "gramatike"
database_id = "c22cbe34-444b-40ec-9987-5e90ecc8cc91"

# R2 Storage
[[r2_buckets]]
binding = "R2_BUCKET"
bucket_name = "gramatike"

# Assets
[assets]
directory = "gramatike_app/static"
binding = "ASSETS"
```

## 🧪 Testing

```bash
# Rodar testes localmente
python -m pytest

# Testar endpoint específico (dev mode)
curl http://localhost:8787/

# Verificar versão deployed
curl -I https://gramatike.workers.dev/
```

## 📖 Documentação Completa

- [CLOUDFLARE_DEPLOYMENT_GUIDE.md](CLOUDFLARE_DEPLOYMENT_GUIDE.md) - Guia completo
- [README.md](README.md) - Instruções gerais
- [Cloudflare Workers Docs](https://developers.cloudflare.com/workers/)
- [Pyodide Package List](https://pyodide.org/en/stable/usage/packages-in-pyodide.html)

## 💡 Dicas

1. **Sempre teste localmente** antes de fazer deploy:
   ```bash
   npm run dev
   ```

2. **Use versões** no código para tracking:
   ```python
   SCRIPT_VERSION = "v2025.12.09.a"
   ```

3. **Monitore logs** após deploy:
   ```bash
   npx wrangler tail
   ```

4. **Faça backup do D1** regularmente:
   ```bash
   npx wrangler d1 export gramatike --output=backup-$(date +%Y%m%d).sql
   ```

5. **Use secrets para dados sensíveis**, não variáveis de ambiente:
   ```bash
   npx wrangler secret put DATABASE_PASSWORD
   ```

## 🆘 Precisa de Ajuda?

1. Verifique logs: `npx wrangler tail`
2. Consulte [CLOUDFLARE_DEPLOYMENT_GUIDE.md](CLOUDFLARE_DEPLOYMENT_GUIDE.md)
3. Veja [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. Documentação oficial: https://developers.cloudflare.com/workers/
