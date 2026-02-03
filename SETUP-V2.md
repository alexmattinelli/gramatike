# 🛠️ Setup Instructions - Gramátike v2

Guia passo-a-passo para configurar o Gramátike v2 do zero.

## 📋 Pré-requisitos

- [Node.js](https://nodejs.org/) >= 20.0.0
- [npm](https://www.npmjs.com/) ou [yarn](https://yarnpkg.com/)
- Conta [Cloudflare](https://dash.cloudflare.com/)
- [Git](https://git-scm.com/)

## 🚀 Instalação Local

### 1. Clonar o Repositório

```bash
git clone https://github.com/alexmattinelli/gramatike.git
cd gramatike
git checkout v2-fresh-start
```

### 2. Instalar Dependências

```bash
npm install
```

### 3. Autenticar na Cloudflare

```bash
npx wrangler login
```

## 🗄️ Configurar Cloudflare D1

### 1. Criar Banco de Dados

```bash
npx wrangler d1 create gramatike-v2
```

Você verá uma saída como:

```
✅ Successfully created DB 'gramatike-v2'

[[d1_databases]]
binding = "DB"
database_name = "gramatike-v2"
database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

### 2. Atualizar wrangler.toml

Copie o `database_id` e atualize em `wrangler.toml`:

```toml
[[d1_databases]]
binding = "DB"
database_name = "gramatike-v2"
database_id = "seu-database-id-aqui"  # ← ATUALIZAR
```

### 3. Aplicar Schema

```bash
npm run db:init
```

Ou manualmente:

```bash
npx wrangler d1 execute gramatike-v2 --file=./db/schema.sql
```

### 4. Popular com Dados Iniciais

```bash
npm run db:seed
```

Ou manualmente:

```bash
npx wrangler d1 execute gramatike-v2 --file=./db/seed.sql
```

### 5. Verificar Tabelas

```bash
npx wrangler d1 execute gramatike-v2 --command="SELECT name FROM sqlite_master WHERE type='table';"
```

Deve retornar:

```
users
posts
likes
comments
sessions
```

### 6. Verificar Usuário Admin

```bash
npx wrangler d1 execute gramatike-v2 --command="SELECT username, email, is_admin FROM users;"
```

## 📦 Configurar Cloudflare R2

### 1. Criar Bucket

```bash
npx wrangler r2 bucket create gramatike-v2
```

### 2. Configurar Acesso Público ⚠️ OBRIGATÓRIO

**IMPORTANTE:** Sem acesso público configurado, o site mostrará erro 404 ao tentar carregar imagens!

Para permitir acesso público aos uploads:

1. Acesse o [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Vá em **R2** → **gramatike-v2**
3. Clique em **Settings**
4. Em **Public Access**, clique em **Allow Access** ou **Connect Domain**
5. Escolha **R2.dev subdomain** (ou configure um domínio personalizado)
6. Salve a configuração

Você receberá um domínio público como: `https://pub-[hash].r2.dev`

**📖 Guia Detalhado:** Veja [R2_PUBLIC_ACCESS_SETUP.md](R2_PUBLIC_ACCESS_SETUP.md) se tiver problemas.

## 💻 Desenvolvimento Local

### 1. Iniciar Servidor de Desenvolvimento

```bash
npm run dev
```

O servidor estará disponível em: `http://localhost:8788`

### 2. Credenciais Padrão

- **Email:** `admin@gramatike.com`
- **Senha:** `admin123`

⚠️ **IMPORTANTE:** Altere a senha após o primeiro login!

### 3. Testar API

```bash
# Health check
curl http://localhost:8788/api/health

# Login
curl -X POST http://localhost:8788/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gramatike.com","password":"admin123"}'
```

## 🌐 Deploy para Produção

### Opção 1: Deploy Manual

```bash
npm run deploy
```

### Opção 2: Deploy Automático via Cloudflare Pages

1. Acesse [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Vá em **Workers & Pages** → **Create Application** → **Pages**
3. Conecte seu repositório GitHub
4. Configure:
   - **Project name:** `gramatike-v2`
   - **Production branch:** `v2-fresh-start`
   - **Build command:** `npm run build`
   - **Build output directory:** `public`

5. Em **Environment Variables**, adicione:
   - `SECRET_KEY`: Uma string segura (32+ caracteres)

6. Deploy!

### Configurar D1 no Cloudflare Pages

1. No projeto Pages, vá em **Settings** → **Functions**
2. Em **D1 database bindings**, adicione:
   - **Variable name:** `DB`
   - **D1 database:** `gramatike-v2`

### Configurar R2 no Cloudflare Pages

1. No projeto Pages, vá em **Settings** → **Functions**
2. Em **R2 bucket bindings**, adicione:
   - **Variable name:** `R2_BUCKET`
   - **R2 bucket:** `gramatike-v2`

## 🔄 Resetar Banco de Dados

Se precisar resetar completamente o banco:

```bash
npm run db:reset
```

Ou manualmente:

```bash
npx wrangler d1 execute gramatike-v2 --file=./db/schema.sql
npx wrangler d1 execute gramatike-v2 --file=./db/seed.sql
```

## 🧪 Desenvolvimento

### TypeScript

Verificar tipos:

```bash
npm run typecheck
```

### Estrutura de Arquivos

```
functions/           # Backend (Cloudflare Pages Functions)
  ├── api/           # API endpoints
  ├── _middleware.ts # Global middleware
  └── *.ts           # Page handlers

src/lib/             # Shared libraries
  ├── auth.ts        # Authentication
  ├── db.ts          # Database queries
  ├── crypto.ts      # Password hashing
  └── ...

public/              # Frontend (static files)
  ├── *.html         # HTML pages
  ├── js/            # JavaScript (Alpine.js)
  └── css/           # Styles (Tailwind CDN + custom)
```

## 🐛 Troubleshooting

### Erro: "DATABASE NOT FOUND"

Certifique-se de que:
1. O database foi criado: `wrangler d1 list`
2. O `database_id` está correto no `wrangler.toml`
3. As tabelas foram criadas: `npm run db:init`

### Erro: "R2 BUCKET NOT FOUND"

Certifique-se de que:
1. O bucket foi criado: `wrangler r2 bucket list`
2. O binding está configurado no `wrangler.toml`

### Página em branco após login

Verifique:
1. Se o JavaScript está carregando (F12 → Console)
2. Se as APIs estão respondendo (F12 → Network)
3. Se o CORS está configurado corretamente

### Erro de autenticação

Limpe os cookies e tente novamente:
- Chrome: F12 → Application → Cookies → Clear All
- Firefox: F12 → Storage → Cookies → Clear All

## 📚 Próximos Passos

1. [ ] Alterar senha do admin
2. [ ] Configurar domínio personalizado
3. [ ] Configurar backup do D1
4. [ ] Monitorar logs no Cloudflare Dashboard
5. [ ] Testar em diferentes dispositivos

## 🆘 Suporte

Se encontrar problemas:

1. Verifique os logs: `wrangler pages deployment tail`
2. Consulte a [documentação oficial](https://developers.cloudflare.com/pages/)
3. Abra uma issue no GitHub

---

**Boa sorte! 🚀**
