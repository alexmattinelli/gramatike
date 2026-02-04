# 🚀 Gramátike - Setup Guide

Guia completo de configuração e deploy do Gramátike no Cloudflare Pages.

## 📋 Pré-requisitos

- Node.js 20+ instalado
- Conta Cloudflare (gratuita) - [Criar conta](https://dash.cloudflare.com/sign-up)
- Git instalado
- Wrangler CLI instalado: `npm install -g wrangler`

## 1️⃣ Configurar Cloudflare D1 (Banco de Dados)

O D1 é um banco de dados SQLite serverless na edge da Cloudflare.

### 1.1 Fazer login no Wrangler

```bash
wrangler login
```

### 1.2 Criar banco D1

```bash
wrangler d1 create gramatike
```

Anote o `database_id` que será retornado. Você precisará dele no `wrangler.toml`.

### 1.3 Aplicar Schema

Execute o script de migração para criar as tabelas:

```bash
./scripts/migrate-schema.sh
```

Ou manualmente:

```bash
# Ambiente local (desenvolvimento)
wrangler d1 execute gramatike --local --file=./db/schema.sql

# Ambiente remoto (produção) ⚠️ IMPORTANTE
wrangler d1 execute gramatike --remote --file=./db/schema.sql
```

**⚠️ NOTA IMPORTANTE:** Certifique-se de executar o comando `--remote` para criar todas as tabelas necessárias no banco de produção, incluindo a tabela `post_likes` que é essencial para a funcionalidade de curtidas. Sem esta etapa, você receberá erro 500 ao tentar curtir posts.

### 1.4 Atualizar wrangler.toml

Edite o arquivo `wrangler.toml` e atualize o `database_id` com o ID do seu banco:

```toml
[[d1_databases]]
binding = "DB"
database_name = "gramatike"
database_id = "seu-database-id-aqui"
```

## 2️⃣ Configurar Cloudflare R2 (Storage)

O R2 é um serviço de armazenamento de objetos compatível com S3.

### 2.1 Criar bucket R2

```bash
wrangler r2 bucket create gramatike
```

### 2.2 Configurar acesso público ⚠️ OBRIGATÓRIO

**IMPORTANTE:** Sem acesso público configurado, o site mostrará erro 404 ao tentar carregar imagens no mobile!

No dashboard do Cloudflare:
1. Acesse **R2** → **gramatike**
2. Vá em **Settings**
3. Em **Public Access**, clique em **Allow Access** ou **Connect Domain**
4. Escolha **R2.dev subdomain** para obter um domínio público automático
5. Copie o URL público (formato: `https://pub-xxxxx.r2.dev`)

**Alternativa:** Configure um domínio personalizado (ex: `files.gramatike.com.br`)

**📖 Guia Completo:** Veja [R2_PUBLIC_ACCESS_SETUP.md](R2_PUBLIC_ACCESS_SETUP.md) para instruções detalhadas e troubleshooting.

### 2.3 Criar Access Key

1. No dashboard R2, vá em **Manage R2 API Tokens**
2. Clique em **Create API Token**
3. Defina permissões: **Object Read & Write**
4. Anote: `Access Key ID` e `Secret Access Key`

### 2.4 Atualizar wrangler.toml

Verifique se o binding R2 está configurado:

```toml
[[r2_buckets]]
binding = "R2_BUCKET"
bucket_name = "gramatike"
```

## 3️⃣ Variáveis de Ambiente

### 3.1 Desenvolvimento Local

Crie um arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

Edite o `.env` e preencha com valores de desenvolvimento:

```env
SECRET_KEY=dev-secret-key-change-me
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=dev@gramatike.com
MAIL_SENDER_NAME=Gramátike Dev
```

### 3.2 Produção (Cloudflare Pages)

Configure as variáveis de ambiente no dashboard do Cloudflare Pages:

1. Acesse **Workers & Pages** → **gramatike** → **Settings** → **Environment Variables**
2. Adicione as seguintes variáveis para **Production**:

```env
SECRET_KEY=<gerar-com-openssl-rand-hex-32>
CLOUDFLARE_ACCOUNT_ID=<seu-account-id>
CLOUDFLARE_R2_ACCESS_KEY_ID=<seu-access-key-id>
CLOUDFLARE_R2_SECRET_ACCESS_KEY=<seu-secret-access-key>
CLOUDFLARE_R2_BUCKET=gramatike
CLOUDFLARE_R2_S3_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com
CLOUDFLARE_R2_PUBLIC_URL=https://pub-xxxxx.r2.dev
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=xsmtpsib-<sua-chave-smtp>
MAIL_PASSWORD=xsmtpsib-<sua-chave-smtp>
MAIL_DEFAULT_SENDER=no-reply@gramatike.com.br
MAIL_SENDER_NAME=Gramátike
```

**Dicas:**
- Gere `SECRET_KEY` com: `openssl rand -hex 32`
- Para email, recomendamos [Brevo](https://www.brevo.com/) (gratuito até 300 emails/dia)
- `CLOUDFLARE_ACCOUNT_ID` está no dashboard: Account → Account ID

## 4️⃣ Deploy

### 4.1 Deploy Local (Desenvolvimento)

Teste localmente com Wrangler:

```bash
# Instalar dependências
npm install

# Rodar em modo desenvolvimento
npm run dev
# ou
wrangler pages dev public
```

Acesse: `http://localhost:8788`

### 4.2 Deploy no Cloudflare Pages

#### Opção A: Deploy Automático (Recomendado)

1. Faça push do código para GitHub
2. No dashboard do Cloudflare:
   - Acesse **Workers & Pages** → **Create Application** → **Pages**
   - Conecte seu repositório GitHub
   - Configure:
     - **Build command:** `npm run build`
     - **Build output directory:** `public`
     - **Environment variables:** Configure conforme seção 3.2
3. Clique em **Save and Deploy**

A partir de agora, cada push para a branch principal fará deploy automático!

#### Opção B: Deploy Manual

```bash
# Build
npm run build

# Deploy
wrangler pages deploy public
```

### 4.3 Configurar Domínio Personalizado (Opcional)

1. No dashboard: **Workers & Pages** → **gramatike** → **Custom Domains**
2. Clique em **Set up a custom domain**
3. Digite seu domínio (ex: `www.gramatike.com.br`)
4. Siga as instruções para configurar DNS

## 5️⃣ Pós-Deploy

### 5.1 Verificar Deploy

Acesse sua aplicação e teste:
- ✅ Página inicial carrega
- ✅ Cadastro de novo usuário funciona
- ✅ Login funciona
- ✅ Feed de posts carrega
- ✅ Upload de imagem funciona
- ✅ Criação de post funciona

### 5.2 Criar Usuário Admin

Se precisar criar um admin manualmente:

```bash
# Conectar ao D1 remoto
wrangler d1 execute gramatike --remote

# Executar SQL
UPDATE user SET is_admin = 1, is_superadmin = 1 WHERE username = 'seu-usuario';
```

### 5.3 Monitoramento

Acompanhe logs e métricas:
- **Logs em tempo real:** `wrangler pages deployment tail`
- **Dashboard:** Workers & Pages → gramatike → Analytics

## 6️⃣ Troubleshooting

### Erro: "wrangler: command not found"

```bash
npm install -g wrangler
```

### Erro: "Database not found"

Verifique se o `database_id` no `wrangler.toml` está correto e se o binding `DB` está configurado.

### Erro: "R2 bucket not found"

Verifique se o bucket existe:

```bash
wrangler r2 bucket list
```

Se não existir, crie novamente:

```bash
wrangler r2 bucket create gramatike
```

### Erro: "Failed to upload image"

Verifique:
1. Variáveis R2 estão configuradas corretamente
2. Access Key tem permissões de escrita
3. Bucket permite acesso público (se necessário)

### Erro: "Email not sent"

Verifique:
1. Credenciais SMTP estão corretas
2. Email remetente está verificado no provedor (Brevo, etc.)
3. Porta e configurações TLS estão corretas

### Schema desatualizado

Se o schema foi atualizado, reaplique:

```bash
./scripts/migrate-schema.sh
```

**⚠️ ATENÇÃO:** Isso irá recriar todas as tabelas e apagar dados existentes!

### Limpar cache do Cloudflare

Se mudanças não aparecem:
1. Dashboard → Caching → Configuration
2. Clique em **Purge Everything**

## 7️⃣ Desenvolvimento

### Estrutura do Projeto

```
gramatike/
├── functions/          # Cloudflare Pages Functions (TypeScript)
│   ├── api/           # API endpoints
│   ├── *.ts           # Route handlers
│   └── _middleware.ts # Auth middleware
├── src/
│   ├── lib/           # Bibliotecas (db, auth, crypto, etc.)
│   ├── templates/     # Templates em TypeScript
│   └── types/         # TypeScript types
├── public/            # Arquivos estáticos (HTML, CSS, JS)
├── static/            # Assets (imagens, etc.)
├── scripts/           # Scripts de migração e utilitários
├── schema.d1.sql      # Schema do banco de dados
├── wrangler.toml      # Configuração Cloudflare
└── package.json       # Dependências Node.js
```

### Comandos Úteis

```bash
# Desenvolvimento local
npm run dev

# Build para produção
npm run build

# Executar SQL no D1 local
wrangler d1 execute gramatike --local --command="SELECT * FROM user;"

# Executar SQL no D1 remoto
wrangler d1 execute gramatike --remote --command="SELECT * FROM user;"

# Listar buckets R2
wrangler r2 bucket list

# Ver logs em tempo real
wrangler pages deployment tail

# Deploy manual
wrangler pages deploy public
```

### Fazer Backup do Banco

```bash
# Exportar dados (produção)
wrangler d1 export gramatike --remote --output=backup.sql

# Importar dados
wrangler d1 execute gramatike --remote --file=backup.sql
```

## 8️⃣ Recursos Adicionais

- [Documentação Cloudflare Pages](https://developers.cloudflare.com/pages/)
- [Documentação Cloudflare D1](https://developers.cloudflare.com/d1/)
- [Documentação Cloudflare R2](https://developers.cloudflare.com/r2/)
- [Wrangler CLI Docs](https://developers.cloudflare.com/workers/wrangler/)
- [Brevo (Email)](https://www.brevo.com/)

## 🎉 Pronto!

Seu Gramátike está configurado e rodando! 

Para suporte ou dúvidas, abra uma issue no GitHub.
