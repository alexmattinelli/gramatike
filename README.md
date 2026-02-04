# 🎓 Gramátike - Língua viva e de todes

> **Versão: 2.2.0 - MVP Refatorado**  
> Plataforma moderna para discussão e aprendizado da língua.

[![Version](https://img.shields.io/badge/version-2.2.0-blue.svg)](https://github.com/alexmattinelli/gramatike)
[![Platform](https://img.shields.io/badge/platform-Cloudflare%20Pages-orange.svg)](https://pages.cloudflare.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-100%25-blue.svg)](https://www.typescriptlang.org/)

## ✨ Features

- 📝 **Feed de posts** com curtidas e comentários
- 👤 **Perfis de usuário** personalizáveis
- 🔐 **Autenticação segura** com sessões baseadas em cookies
- 👨‍💼 **Painel administrativo** com dashboard e gerenciamento
- 📱 **Design responsivo** mobile-first
- ⚡ **Performance otimizada** com Tailwind CSS e HTMX

## 🚀 Tech Stack

- **Runtime:** Cloudflare Pages Functions (TypeScript)
- **Database:** Cloudflare D1 (SQLite on the edge)
- **Storage:** Cloudflare R2 (file uploads) ⚠️ [Configuração obrigatória](R2_PUBLIC_ACCESS_SETUP.md)
- **Frontend:** HTML + Tailwind CSS (via CDN) + HTMX
- **Auth:** Cookie-based sessions with bcrypt

> **⚠️ IMPORTANTE:** Se você está vendo erro 404 no mobile ao carregar imagens, veja o [guia rápido de configuração do R2](QUICK_FIX_404.md).

## 📍 Acesso Rápido

- **Site:** https://www.gramatike.com.br
- **Feed:** https://www.gramatike.com.br/feed
- **Admin:** https://www.gramatike.com.br/admin

## 🎨 O Que Mudou na v2.2.0

Esta versão traz uma **refatoração completa** focando apenas nas funcionalidades essenciais (MVP):

### ✅ Mantido (Features Funcionais)
- ✨ **Autenticação:** Login, registro, sessões e logout
- 📝 **Feed:** Posts com paginação, curtidas, comentários
- 👤 **Perfis:** Ver e editar perfil de usuário
- 👨‍💼 **Admin:** Dashboard, gerenciamento de usuários, moderação

### 🗑️ Removido (Features Não Implementadas)
- ❌ Artigos, apostilas, exercícios (apenas HTML estático)
- ❌ Dinâmicas, redação, novidades
- ❌ Reset de senha (sem backend)
- ❌ Documentação obsoleta (14 arquivos .md)

### 🚀 Melhorias
- **70% menos código** - De 28 templates para 11 essenciais
- **Feed otimizado** - De 104KB para ~10KB com Tailwind CSS + HTMX
- **Performance** - Infinite scroll, design responsivo mobile-first
- **Admin melhorado** - Dashboard com Chart.js e gerenciamento completo
- **Código modular** - Partials reutilizáveis (navbar, post-card, footer)
- **Utilitários** - R2 uploads e template rendering simplificados

## 🚀 Cloudflare Pages Setup

Este projeto usa **TypeScript** e **Cloudflare Pages Functions** (edge runtime serverless).

### Configuração Inicial

Ver [SETUP.md](./SETUP.md) para instruções detalhadas.

**Resumo rápido:**

1. Conectar repositório ao Cloudflare Pages
2. Build command: `npm run build`
3. Build output: `public`
4. Adicionar D1 binding: `DB` → seu banco D1 (ex: `gramatike`)
5. **⚠️ IMPORTANTE - Executar schema no banco remoto:**
   ```bash
   npx wrangler d1 execute gramatike --remote --file=./db/schema.sql
   ```
   **Nota:** Isso cria todas as tabelas necessárias, incluindo `post_likes` que é necessária para a funcionalidade de curtidas. Sem esta etapa, você receberá erro 500 ao tentar curtir posts.

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
wrangler d1 execute gramatike --file=./db/schema.sql --remote

# 4. Verificar se as tabelas foram criadas
wrangler d1 execute gramatike --command="SELECT name FROM sqlite_master WHERE type='table';" --remote
```

**Você deve ver as tabelas:** users, posts, sessions, comments, likes

### Troubleshooting - Erro 500 ao cadastrar

Se você receber erro 500 ao tentar criar uma conta, provavelmente o banco de dados não foi inicializado. Execute:

```bash
# Aplicar schema (criar tabelas) no ambiente remoto
wrangler d1 execute gramatike --remote --file=./db/schema.sql

# Verificar se funcionou
wrangler d1 execute gramatike --remote --command="SELECT name FROM sqlite_master WHERE type='table';"
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
# Edite o arquivo db/schema.sql, depois execute:
wrangler d1 execute gramatike --file=./db/schema.sql --remote
```

### 🔄 Resetar Banco de Dados D1

Para resetar completamente o banco de dados (apagar todos os dados e recriar as tabelas):

```bash
# Executar o schema (DROP + CREATE)
wrangler d1 execute gramatike --file=./db/schema.sql --remote

# Verificar tabelas criadas
wrangler d1 execute gramatike --command="SELECT name FROM sqlite_master WHERE type='table';" --remote

# Verificar usuário admin criado (se houver seed data)
wrangler d1 execute gramatike --command="SELECT * FROM users;" --remote
```

**⚠️ IMPORTANTE:** Altere a senha padrão após o primeiro login!

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

For configurar o R2:

1. Criar um bucket R2 chamado `gramatike` no [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. **Configurar acesso público** - IMPORTANTE para o site funcionar! Veja [R2_PUBLIC_ACCESS_SETUP.md](R2_PUBLIC_ACCESS_SETUP.md)
3. O binding `R2_BUCKET` permite que as Functions acessem o bucket automaticamente

**📖 Guia Completo:** Veja [R2_PUBLIC_ACCESS_SETUP.md](R2_PUBLIC_ACCESS_SETUP.md) para instruções detalhadas sobre como habilitar acesso público e evitar erros 404.

**Variáveis RAG/IA (opcional):**

- `RAG_MODEL`: modelo de embeddings (padrão: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)

## 📁 Estrutura do Projeto

```
gramatike/
├── functions/              # Cloudflare Pages Functions (TypeScript)
│   ├── _middleware.ts      # Global middleware (auth)
│   ├── index.ts            # Landing page
│   ├── login.ts            # Login page
│   ├── cadastro.ts         # Register page
│   ├── feed.ts             # Main feed page
│   ├── meu_perfil.ts       # User profile page
│   ├── configuracoes.ts    # Settings page
│   ├── admin.ts            # Admin dashboard
│   ├── perfil/
│   │   └── [username].ts   # Public user profile
│   └── api/                # API endpoints
│       ├── auth/           # Authentication (login, register, logout)
│       ├── posts/          # Posts CRUD and interactions
│       ├── users/          # User management
│       └── admin/          # Admin endpoints
│
├── public/                 # Static files (served directly)
│   ├── templates/          # HTML templates
│   │   ├── feed.html       # Main feed (Tailwind + HTMX)
│   │   ├── login.html      # Login form
│   │   ├── cadastro.html   # Registration form
│   │   ├── meu_perfil.html # Profile page
│   │   ├── perfil.html     # Public profile
│   │   ├── configuracoes.html # Settings
│   │   ├── admin.html      # Admin dashboard
│   │   ├── partials/       # Reusable components
│   │   │   ├── navbar.html # Navigation bar
│   │   │   ├── post-card.html # Post card component
│   │   │   └── footer.html # Footer component
│   │   ├── 404.html        # Error page
│   │   └── acesso_restrito.html # Forbidden page
│   │
│   └── static/             # CSS, JS, images
│       ├── css/
│       │   └── main.css    # Custom styles (minimal)
│       ├── js/
│       │   ├── admin.js    # Admin panel logic
│       │   └── utils.js    # Shared utilities
│       └── img/
│           ├── logo.svg    # Logo
│           └── perfil.png  # Default avatar
│
├── src/                    # TypeScript source code
│   ├── lib/                # Shared utilities
│   │   ├── auth.ts         # Authentication helpers
│   │   ├── db.ts           # Database utilities
│   │   ├── crypto.ts       # Password hashing
│   │   ├── sanitize.ts     # Input sanitization
│   │   ├── utils.ts        # General utilities
│   │   └── upload.ts       # R2 upload handler
│   ├── templates/
│   │   └── renderer.ts     # Template rendering helper
│   └── types/
│       └── index.d.ts      # TypeScript types
│
├── schema.d1.sql           # Database schema (D1/SQLite)
├── wrangler.toml           # Cloudflare configuration
├── package.json            # Node.js dependencies
├── tsconfig.json           # TypeScript config
└── README.md               # This file
```

## 🔧 Troubleshooting

### Erro "Sistema temporariamente indisponível"

As tabelas do banco de dados não foram criadas. Execute:

```bash
wrangler d1 execute gramatike --file=./db/schema.sql --remote
```

### Deploy falha com erro de Worker

Se você ver erros relacionados a "Workers Build failed":

1. ✅ Verifique que `wrangler.toml` tem `pages_build_output_dir = "public"`
2. ✅ Verifique que NÃO há campos `main` ou `compatibility_flags` no `wrangler.toml`
3. ❌ Remova qualquer GitHub Actions workflow de deploy
4. ✅ Use a integração nativa do Cloudflare Pages

### Erro 404 - "Object not found" no mobile

Se você está recebendo erro 404 ao acessar o site pelo celular, especialmente ao carregar imagens:

**Causa:** O bucket R2 não está configurado com acesso público.

**Solução:** Siga o guia completo em [R2_PUBLIC_ACCESS_SETUP.md](R2_PUBLIC_ACCESS_SETUP.md) para:
1. Habilitar Public Access no bucket R2
2. Configurar CORS policy
3. Testar o acesso mobile

### Imagens não aparecem

Configure o R2 bucket com acesso público. Veja [R2_PUBLIC_ACCESS_SETUP.md](R2_PUBLIC_ACCESS_SETUP.md).

## 📚 Documentação Adicional

- [R2_PUBLIC_ACCESS_SETUP.md](R2_PUBLIC_ACCESS_SETUP.md) - **Fix erro 404 mobile** - Configurar acesso público do R2
- [CLOUDFLARE_D1_SETUP.md](CLOUDFLARE_D1_SETUP.md) - Configuração detalhada do D1
- [BREVO_EMAIL_SETUP.md](BREVO_EMAIL_SETUP.md) - Configuração de e-mail
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Guia de solução de problemas

## 📄 Licença

Este projeto está sob licença MIT.

git add README.md
