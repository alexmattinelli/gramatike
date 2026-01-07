# Gramatike

## Cloudflare Pages (TypeScript)

Esta aplicação usa **Cloudflare Pages** com **Functions** (TypeScript) para uma arquitetura serverless moderna.

**Stack:**
- Frontend: HTML estático com templates Jinja2 (pré-renderizados)
- Backend: Cloudflare Functions (TypeScript) no diretório `/functions`
- Banco de dados: Cloudflare D1 (SQLite na edge)
- Storage: Cloudflare R2 (arquivos de usuário)

### 🚀 Deploy no Cloudflare Pages

Este projeto usa **TypeScript** e **Cloudflare Pages Functions** (não Python Workers).

### Configuração Inicial

Veja as instruções completas em [CLOUDFLARE_PAGES_SETUP.md](./CLOUDFLARE_PAGES_SETUP.md).

**Resumo rápido:**

1. Conectar repositório ao Cloudflare Pages
2. Build command: `npm run build`
3. Build output: `public`
4. Adicionar D1 binding: `DB` → seu banco D1 (ex: `gramatike`)
5. Resetar banco: `wrangler d1 execute <seu-banco-d1> --file=./schema.d1.sql --remote`

### Deploy Automático (Recomendado)

**O deploy é automático via integração nativa do Cloudflare Pages com GitHub.**

1. No [Cloudflare Dashboard](https://dash.cloudflare.com/):
   - Vá em **Workers & Pages** → **Create Application** → **Pages**
   - Conecte seu repositório GitHub `alexmattinelli/gramatike`
   - Configure o projeto:
     - **Project name**: `gramatike`
     - **Production branch**: `main`
     - **Build command**: `npm run build` (ou deixe vazio)
     - **Build output directory**: `public` ← **IMPORTANTE!**
     - **Root directory**: Deixe vazio (raiz do repo)

2. O Cloudflare Pages irá automaticamente fazer deploy a cada push na branch `main`

**⚠️ IMPORTANTE:**
- ❌ **NÃO use GitHub Actions** para deploy (pode causar conflitos com Workers)
- ✅ Use a integração nativa do Cloudflare Pages
- ✅ **Build output directory** = `public` (onde estão os arquivos)
- ✅ **Root directory** = vazio ou `/` (raiz do repositório)
- O build acontece no Cloudflare, não no GitHub Actions

### Troubleshooting

Se aparecer erro sobre "Python Workers":
- O projeto Pages precisa ser recriado do zero
- Siga as instruções em [CLOUDFLARE_PAGES_SETUP.md](./CLOUDFLARE_PAGES_SETUP.md)

### 🛠️ Deploy Manual via CLI (Opcional)

Se precisar fazer deploy manual:

```bash
# Instalar dependências
npm install

# Deploy para produção
npm run deploy

# Ou usando wrangler diretamente
wrangler pages deploy public
```

### 💻 Desenvolvimento Local

```bash
# Instalar dependências
npm install

# Rodar servidor de desenvolvimento
npm run dev

# Verificar tipos TypeScript
npm run typecheck
```

O servidor local estará disponível em `http://localhost:8788`

## 🗄️ Banco de Dados (Cloudflare D1)

O Gramátike usa **Cloudflare D1** (SQLite na edge) para armazenamento de dados.

### Configuração Inicial do D1

```bash
# 1. Autenticar (se necessário)
wrangler login

# 2. Criar o banco de dados D1 (se ainda não existe)
wrangler d1 create gramatike

# 3. Aplicar o schema (criar tabelas)
wrangler d1 execute gramatike --file=./schema.d1.sql

# 4. Verificar
wrangler d1 execute gramatike --command="SELECT name FROM sqlite_master WHERE type='table'"
```

### Configuração no wrangler.toml

O `wrangler.toml` já está configurado com o D1 binding:

```toml
[[d1_databases]]
binding = "DB"
database_name = "gramatike"
database_id = "d0984113-06be-49f5-939a-9d5c5dcba7b6"
```

**Nota:** O `database_id` deve corresponder ao ID do seu banco D1. Para verificar: `wrangler d1 list`

### 🔄 Migração de Schema

Se você precisar atualizar o schema do banco de dados:

```bash
# Edite o arquivo schema.d1.sql, depois execute:
wrangler d1 execute gramatike --file=./schema.d1.sql
```

### 🔄 Resetar Banco de Dados D1

Para resetar completamente o banco de dados (apagar todos os dados e recriar as tabelas):

```bash
# Executar o schema (DROP + CREATE)
wrangler d1 execute gramatike --file=./schema.d1.sql --remote

# Verificar tabelas criadas
wrangler d1 execute gramatike --command="SELECT name FROM sqlite_master WHERE type='table';" --remote

# Verificar usuário admin criado
wrangler d1 execute gramatike --command="SELECT * FROM user;" --remote
```

**Credenciais padrão após reset:**
- **Email**: `contato@gramatike.com`
- **Senha**: `admin123`

⚠️ **IMPORTANTE:** Altere a senha após o primeiro login!

## ⚙️ Variáveis de Ambiente

### Configuração no Cloudflare Pages

Configure as variáveis de ambiente em: **Workers & Pages** → **gramatike** → **Settings** → **Environment Variables**

**Mínimo necessário:**
- `SECRET_KEY`: string segura (32+ chars) para sessões
- D1 Database: já configurado via `wrangler.toml`
- R2 Bucket: já configurado via `wrangler.toml`

**Variáveis de E-mail (opcional, mas recomendado):**

Configure estas variáveis para habilitar funcionalidades de e-mail (verificação, reset de senha, etc.):

- `MAIL_SERVER`: host SMTP (ex: smtp.office365.com ou smtp-relay.brevo.com)
- `MAIL_PORT`: porta (geralmente 587)
- `MAIL_USE_TLS`: true/false (geralmente true)
- `MAIL_USERNAME`: usuário SMTP (e/ou API Key)
- `MAIL_PASSWORD`: senha SMTP (ou API Key)
- `MAIL_DEFAULT_SENDER`: e-mail remetente padrão (ex: no-reply@gramatike.com.br)
- `MAIL_SENDER_NAME`: nome amigável do remetente (ex: Gramátike)

**Para Brevo (recomendado)**: Veja o guia completo em [BREVO_EMAIL_SETUP.md](BREVO_EMAIL_SETUP.md)

**Cloudflare R2 Storage:**

O R2 já está configurado no `wrangler.toml`:

```toml
[[r2_buckets]]
binding = "R2_BUCKET"
bucket_name = "gramatike"
```

Para configurar o R2:

1. Criar um bucket R2 chamado `gramatike` no [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Configurar domínio público do R2 (Settings → Public Access)
3. O binding `R2_BUCKET` permite que as Functions acessem o bucket automaticamente

**📖 Guia Completo:** Veja [CLOUDFLARE_R2_SETUP.md](CLOUDFLARE_R2_SETUP.md) para instruções detalhadas.

**Variáveis RAG/IA (opcional):**

- `RAG_MODEL`: modelo de embeddings (padrão: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)

## 📁 Estrutura do Projeto

```
gramatike/
├── functions/           # Cloudflare Functions (TypeScript)
│   ├── _middleware.ts   # Middleware global
│   ├── api/            # API endpoints
│   └── pages/          # Server-side rendered pages
├── public/             # Arquivos estáticos (HTML, CSS, JS)
│   ├── static/         # CSS, JS, imagens
│   └── templates/      # Templates HTML
├── src/                # Código TypeScript compartilhado
├── schema.d1.sql       # Schema do banco D1
├── wrangler.toml       # Configuração Cloudflare
├── package.json        # Dependências Node.js
└── tsconfig.json       # Configuração TypeScript
```

## 🔧 Troubleshooting

### Erro "Sistema temporariamente indisponível"

As tabelas do banco de dados não foram criadas. Execute:

```bash
wrangler d1 execute gramatike --file=./schema.d1.sql
```

### Deploy falha com erro de Worker

Se você ver erros relacionados a "Workers Build failed":

1. ✅ Verifique que `wrangler.toml` tem `pages_build_output_dir = "public"`
2. ✅ Verifique que NÃO há campos `main` ou `compatibility_flags` no `wrangler.toml`
3. ❌ Remova qualquer GitHub Actions workflow de deploy
4. ✅ Use a integração nativa do Cloudflare Pages

### Imagens não aparecem

Configure o R2 bucket com acesso público. Veja [CLOUDFLARE_R2_SETUP.md](CLOUDFLARE_R2_SETUP.md).

## 📚 Documentação Adicional

- [CLOUDFLARE_D1_SETUP.md](CLOUDFLARE_D1_SETUP.md) - Configuração detalhada do D1
- [CLOUDFLARE_R2_SETUP.md](CLOUDFLARE_R2_SETUP.md) - Configuração detalhada do R2
- [BREVO_EMAIL_SETUP.md](BREVO_EMAIL_SETUP.md) - Configuração de e-mail
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Guia de solução de problemas

## 📄 Licença

Este projeto está sob licença MIT.
