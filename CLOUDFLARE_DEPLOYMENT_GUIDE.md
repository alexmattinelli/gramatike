# Guia de Deployment Cloudflare - Gramátike

## 🎯 Resumo Executivo

Este projeto usa **Cloudflare Workers Python** para deployment, NÃO Cloudflare Pages Functions.

**Comando de Deploy Correto:**
```bash
npm run deploy
```

## 📋 Visão Geral das Opções de Deployment

### Cloudflare Workers Python ✅ (RECOMENDADO - USADO NESTE PROJETO)

**Características:**
- ✅ Suporta dependências Python via `pyproject.toml` e `uv`
- ✅ Usa o arquivo `index.py` como entry point
- ✅ Configurado via `wrangler.toml`
- ✅ Deploy via `wrangler deploy`
- ✅ Suporta pacotes Pyodide compatíveis

**Arquivos de Configuração:**
- `wrangler.toml` - Configuração do Worker
- `pyproject.toml` - Dependências Python (via uv)
- `index.py` - Entry point do Worker
- `package.json` - Scripts npm para deploy

### Cloudflare Pages Functions ❌ (NÃO SUPORTADO AINDA)

**Características:**
- ❌ **NÃO suporta `requirements.txt` ainda**
- ❌ Limitado a código Python sem dependências externas
- ⚠️ Mensagem de erro: "You cannot yet deploy Python Workers that depend on packages defined in requirements.txt"

**Arquivos (mantidos por compatibilidade, mas NÃO usados para deploy):**
- `_pages.toml` - Configuração do Pages (sem build command)
- `functions/` - Handlers Python (não usados no deployment atual)

## 🚀 Como Fazer Deploy

### Pré-requisitos

1. **Instalar uv** (gerenciador de pacotes Python):
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Instalar wrangler** (já incluído no `package.json`):
   ```bash
   npm install
   ```

3. **Autenticar com Cloudflare**:
   ```bash
   npx wrangler login
   ```

### Deploy via CLI

```bash
# 1. Instalar dependências Python (via uv)
uv sync

# 2. Deploy para Cloudflare Workers
npm run deploy
```

### Deploy via GitHub Actions

Configure um workflow `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloudflare Workers

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install dependencies
        run: |
          npm install
          uv sync
      
      - name: Deploy to Cloudflare Workers
        run: npm run deploy
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

## 🔧 Configuração

### Variáveis de Ambiente (Cloudflare Dashboard)

Configure em **Workers & Pages > Gramátike > Settings > Variables**:

**Obrigatórias:**
- `SECRET_KEY` - String segura (32+ caracteres)

**D1 Database (SQLite na edge):**
- Configurado via `wrangler.toml` - binding `DB`
- Criar tabelas: `wrangler d1 execute gramatike --file=./schema.d1.sql`

**R2 Storage (para uploads):**
- Configurado via `wrangler.toml` - binding `R2_BUCKET`
- Bucket name: `gramatike`

**Email (opcional):**
- `MAIL_SERVER`
- `MAIL_PORT`
- `MAIL_USERNAME`
- `MAIL_PASSWORD`
- `MAIL_DEFAULT_SENDER`

### Secrets (via CLI)

Para valores sensíveis, use secrets:

```bash
# Configurar secret
npx wrangler secret put SECRET_KEY

# Listar secrets
npx wrangler secret list

# Deletar secret
npx wrangler secret delete SECRET_KEY
```

## 📦 Gerenciamento de Dependências

### Adicionar Nova Dependência

```bash
# Adicionar ao pyproject.toml
uv add nome-do-pacote

# Sincronizar dependências
uv sync

# Fazer deploy
npm run deploy
```

### Dependências Suportadas

Apenas pacotes compatíveis com **Pyodide/WebAssembly** são suportados.

**✅ Suportados:**
- `webtypy` - Web framework para Workers Python
- Pacotes pure-Python sem dependências C

**❌ NÃO Suportados (requerem compilação C/nativa):**
- `psycopg2-binary` - Use D1/SQLite em vez de PostgreSQL
- `Pillow` - Processamento de imagens nativo
- `flask` e extensões Flask - Use WorkerEntrypoint nativo
- `fastapi` - [Não suportado no Workers Python](https://github.com/cloudflare/workers-sdk/issues/5608)

**Alternativa:** Para estes pacotes, use serviços externos ou D1 Database (SQLite).

## 🐛 Troubleshooting

### Erro: "You cannot yet deploy Python Workers that depend on packages defined in requirements.txt"

**Causa:** Você está tentando usar Cloudflare Pages Functions com `requirements.txt`.

**Solução:** Use Cloudflare Workers deployment:
1. Remova ou desative `_pages.toml`
2. Use `npm run deploy` (via `wrangler.toml`)
3. Dependências vão via `pyproject.toml`, não `requirements.txt`

### Deploy Falha com "Package not found"

**Causa:** Pacote não disponível no Pyodide.

**Solução:**
1. Verifique se o pacote é compatível com Pyodide
2. Use alternativa pure-Python
3. Ou implemente funcionalidade usando Workers APIs

### Changes Not Reflected After Deploy

**Causa:** Cache ou versão antiga.

**Solução:**
```bash
# Force deploy
npx wrangler deploy --force

# Verificar versão deployed
curl -I https://seu-worker.workers.dev

# Limpar cache do Cloudflare (via Dashboard)
```

## 📚 Recursos Adicionais

- [Cloudflare Workers Python Documentation](https://developers.cloudflare.com/workers/languages/python/)
- [Pyodide Package List](https://pyodide.org/en/stable/usage/packages-in-pyodide.html)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Wrangler CLI Documentation](https://developers.cloudflare.com/workers/wrangler/)

## 🔄 Migração de Pages Functions para Workers

Se você estava usando Pages Functions anteriormente:

1. **Código:**
   - Mova lógica de `functions/` para `index.py`
   - Use `WorkerEntrypoint` pattern em vez de `async def on_request`

2. **Dependências:**
   - Migre de `requirements.txt` para `pyproject.toml`
   - Remova pacotes não suportados no Pyodide

3. **Configuração:**
   - Use `wrangler.toml` em vez de `_pages.toml`
   - Configure bindings (D1, R2) no `wrangler.toml`

4. **Deploy:**
   - Use `npm run deploy` em vez de git push para Pages

## ✅ Checklist de Deployment

- [ ] `uv` instalado
- [ ] `npm install` executado
- [ ] `uv sync` executado
- [ ] Autenticado com `wrangler login`
- [ ] D1 database criado e schema aplicado
- [ ] R2 bucket criado
- [ ] Variáveis de ambiente configuradas
- [ ] Secrets configurados (se necessário)
- [ ] Deploy via `npm run deploy`
- [ ] Teste em produção

## 📝 Notas Importantes

1. **Não use `requirements.txt` para deployment** - Use `pyproject.toml`
2. **Não use Pages Functions** - Use Workers Python (`index.py`)
3. **Teste localmente** com `npm run dev` antes de fazer deploy
4. **Monitore logs** via `wrangler tail`
5. **Versione seus deploys** - Atualize `SCRIPT_VERSION` no `index.py`
