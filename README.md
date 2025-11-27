# Gramatike

## Cloudflare Workers Python

Esta aplicacao usa Cloudflare Workers Python (Pyodide) com o padrao nativo WorkerEntrypoint. O deploy deve ser feito usando `pywrangler`.

**NOTA:** FastAPI nao pode ser implantado no Cloudflare Workers Python. Veja: https://github.com/cloudflare/workers-sdk/issues/5608

### Deploy via CLI (Recomendado)

1. Instale [uv](https://docs.astral.sh/uv/getting-started/installation/) (gerenciador de pacotes Python)
2. Instale as dependencias: `uv sync`
3. Deploy: `npm run deploy` (ou `uv run pywrangler deploy`)

### Deploy via GitHub Actions

Configure um workflow do GitHub Actions com:
```yaml
- name: Deploy to Cloudflare Workers
  run: |
    npm install
    uv sync
    npm run deploy
  env:
    CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
    CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

### Notas Importantes

- O Cloudflare Workers Python usa o padrao nativo WorkerEntrypoint (sem FastAPI)
- O arquivo `uv.lock` garante que as dependencias sejam resolvidas corretamente
- Variaveis de ambiente (Settings > Environment Variables):
   - `SECRET_KEY`: uma string segura
   - `DATABASE_URL`: Postgres gerenciado (recomendado para producao)
   - Variaveis do Cloudflare R2 (veja abaixo)

## Banco de Dados

### ⚠️ Erro "Sistema temporariamente indisponível"?

Se você está vendo este erro, as tabelas do banco de dados não foram criadas. Execute:

```bash
# 1. Autenticar (se necessário)
wrangler login

# 2. Criar tabelas no banco D1
wrangler d1 execute gramatike --file=./schema.d1.sql

# 3. Re-deploy
npm run deploy
```

Ou use o script automatizado: `./scripts/setup_d1_database.sh`

### Cloudflare D1 (Recomendado para Workers)

O Gramátike usa **Cloudflare D1** (SQLite na edge) para o deploy em Cloudflare Workers. Se você está vendo o erro **"Sistema temporariamente indisponível"**, provavelmente o D1 não está configurado.

**📖 Guia Completo:** Veja [CLOUDFLARE_D1_SETUP.md](CLOUDFLARE_D1_SETUP.md) para instruções detalhadas de como:
- Criar o banco de dados D1
- Aplicar o schema (`schema.d1.sql`)
- Configurar o `wrangler.toml`
- Fazer troubleshooting

**Comandos rápidos:**
```bash
# Criar banco D1
wrangler d1 create gramatike

# Criar tabelas
wrangler d1 execute gramatike --file=./schema.d1.sql

# Deploy
npm run deploy
```

### PostgreSQL (Flask tradicional)

Para deploy Flask tradicional (Heroku, Railway, etc.), use PostgreSQL via `DATABASE_URL`.

## Variáveis de ambiente necessárias

Mínimo para rodar:

- SECRET_KEY: string segura (32+ chars)
- Para Cloudflare Workers: D1 configurado no `wrangler.toml`
- Para Flask tradicional: DATABASE_URL (Postgres recomendado)

### Database Migrations (PostgreSQL)

Para aplicar migrações pendentes ao banco de dados:

```bash
# Aplicar todas as migrações pendentes
flask db upgrade

# Verificar versão atual da migração
flask db current
```

**Nota importante:** Se você encontrar o erro `StringDataRightTruncation` relacionado ao campo `resumo`, consulte [DEPLOY_QUICK_REFERENCE.md](DEPLOY_QUICK_REFERENCE.md) para aplicar a correção que converte o campo de VARCHAR(400) para TEXT (ilimitado).

E-mail (opcional, mas necessário para verificação de e-mail, reset de senha, etc.):

- MAIL_SERVER: host SMTP (ex: smtp.office365.com ou smtp-relay.brevo.com)
- MAIL_PORT: porta (geralmente 587)
- MAIL_USE_TLS: true/false (geralmente true)
- MAIL_USERNAME: usuário SMTP (e/ou API Key)
- MAIL_PASSWORD: senha SMTP (ou API Key)
- MAIL_DEFAULT_SENDER: e-mail remetente padrão (ex: no-reply@gramatike.com.br)
- MAIL_SENDER_NAME: nome amigável do remetente (ex: Gramátike)

**Para Brevo (recomendado)**: Veja o guia completo em [BREVO_EMAIL_SETUP.md](BREVO_EMAIL_SETUP.md) com:
- Instruções passo-a-passo de configuração
- Como obter a SMTP Key
- Configuração de SPF/DKIM
- Scripts de diagnóstico e teste
- Solução de problemas comuns

### Testar Envio de E-mails

Para testar se o envio de e-mails está funcionando corretamente, use o script `send_test_email.py`:

```bash
# E-mail de teste básico (usa configuração do .env ou variáveis de ambiente)
python3 scripts/send_test_email.py seu_email@exemplo.com

# E-mail personalizado com título e conteúdo
python3 scripts/send_test_email.py seu_email@exemplo.com \
  --title "Meu Teste" \
  --html "<p>Conteúdo personalizado do e-mail</p>"

# Especificar servidor SMTP manualmente (útil para testes)
python3 scripts/send_test_email.py seu_email@exemplo.com \
  --server smtp.gmail.com \
  --port 587 \
  --tls \
  --user seu_email@gmail.com \
  --password sua_senha
```

**Nota:** Os e-mails de teste agora incluem o template completo do Gramátike com logo e botões roxos. Veja [EMAIL_TEST_TEMPLATE_FIX.md](EMAIL_TEST_TEMPLATE_FIX.md) para mais detalhes.

Cloudflare R2 Storage (necessário para upload de arquivos em ambientes serverless):

- CLOUDFLARE_ACCOUNT_ID: ID da sua conta Cloudflare (encontrado em Overview > Account ID)
- CLOUDFLARE_R2_ACCESS_KEY_ID: Access Key ID do R2 (criado em R2 > Manage R2 API Tokens)
- CLOUDFLARE_R2_SECRET_ACCESS_KEY: Secret Access Key do R2
- CLOUDFLARE_R2_BUCKET: nome do bucket (padrão: 'gramatike')
- CLOUDFLARE_R2_PUBLIC_URL: URL pública do bucket (domínio personalizado ou r2.dev)

**🚨 IMPORTANTE - Configuração Necessária para Imagens Funcionarem:**

Se as imagens não estiverem aparecendo no site, você precisa:

1. Criar um bucket R2 (ex: 'gramatike') em R2 > Create bucket
2. **Habilitar acesso público** via R2.dev subdomain ou domínio personalizado
3. Criar um API Token com permissões de leitura/escrita para o bucket
4. Configurar as variáveis de ambiente

**📖 Guia Completo:** Veja [CLOUDFLARE_R2_SETUP.md](CLOUDFLARE_R2_SETUP.md) para instruções detalhadas passo-a-passo.

**🔧 Diagnóstico:** Se as imagens não funcionarem, execute o script de diagnóstico:
```bash
python diagnose_images.py
```
Este script verifica automaticamente sua configuração e identifica problemas.

RAG/IA (opcional):

- RAG_MODEL: modelo de embeddings (padrão: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)

Veja `.env.example` para um modelo de configuração local. No Cloudflare Pages, cadastre as mesmas chaves em Settings → Environment Variables.

### Executar local
Ver seção "Development".
