# Configuração do Cloudflare Pages - Gramátike

## ⚠️ Recriar Projeto Pages (se necessário)

Se o Cloudflare Pages continuar tentando usar Python Workers, siga estes passos:

### 1. Deletar Projeto Antigo

1. Acesse: https://dash.cloudflare.com
2. Vá em **Workers & Pages**
3. Selecione o projeto **gramatike**
4. Vá em **Settings** → **Danger Zone**
5. Clique em **Delete Project**
6. Confirme digitando o nome do projeto

### 2. Criar Novo Projeto Pages

1. No Cloudflare Dashboard, clique em **Create application**
2. Selecione **Pages** → **Connect to Git**
3. Escolha o repositório: **alexmattinelli/gramatike**
4. Configure:

   **Project name:** `gramatike`
   
   **Production branch:** `main`
   
   **Build settings:**
   - Framework preset: **None** (ou **Custom**)
   - Build command: `npm run build`
   - Build output directory: `public`
   - Root directory: `/`
   
   **Environment variables (Production):**
   ```
   NODE_VERSION=20
   ```

5. Clique em **Save and Deploy**

### 3. Configurar D1 Database Binding

Após criar o projeto:

1. Vá em **Settings** → **Functions**
2. Em **D1 database bindings**, clique **Add binding**:
   - Variable name: `DB`
   - D1 database: Selecione seu banco D1 (ex: `gramatike`)
3. Clique em **Save**

### 4. Configurar R2 Storage Binding (se necessário)

1. Vá em **Settings** → **Functions**
2. Em **R2 bucket bindings**, clique **Add binding**:
   - Variable name: `R2_BUCKET`
   - R2 bucket: Selecione seu bucket R2
3. Clique em **Save**

### 5. Configurar Environment Variables

Vá em **Settings** → **Environment variables** e adicione:

**Production & Preview:**

| Variable | Value |
|----------|-------|
| `CLOUDFLARE_ACCOUNT_ID` | `<seu-account-id>` |
| `CLOUDFLARE_API_TOKEN` | `<seu-api-token>` |
| `CLOUDFLARE_R2_ACCESS_KEY_ID` | `<seu-r2-access-key-id>` |
| `CLOUDFLARE_R2_BUCKET` | `<nome-do-seu-bucket>` |
| `CLOUDFLARE_R2_PUBLIC_URL` | `<sua-url-publica-r2>` |
| `CLOUDFLARE_R2_S3_ENDPOINT` | `<seu-s3-endpoint-r2>` |
| `CLOUDFLARE_R2_SECRET_ACCESS_KEY` | `<seu-r2-secret-access-key>` |
| `MAIL_DEFAULT_SENDER` | `<seu-email-remetente>` |
| `MAIL_PASSWORD` | `<sua-senha-smtp>` |
| `MAIL_PORT` | `587` |
| `MAIL_SENDER_NAME` | `<nome-do-remetente>` |
| `MAIL_SERVER` | `<seu-servidor-smtp>` |
| `MAIL_USERNAME` | `<seu-usuario-smtp>` |
| `MAIL_USE_TLS` | `true` |
| `SECRET_KEY` | `<sua-chave-secreta-32-chars>` |

### 6. Resetar Banco D1

Após configurar tudo:

```bash
wrangler d1 execute <nome-do-seu-banco-d1> --file=./schema.d1.sql --remote
```

### 7. Verificar Deploy

1. Vá em **Deployments**
2. Verifique que o build:
   - ✅ Usa `npm run build`
   - ✅ **NÃO** menciona Python
   - ✅ Completa com sucesso
3. Acesse o site e teste criar um post

## ✅ Checklist Final

- [ ] Projeto antigo deletado
- [ ] Novo projeto criado e conectado ao Git
- [ ] D1 database binding configurado
- [ ] R2 bucket binding configurado (se necessário)
- [ ] Environment variables adicionadas
- [ ] Banco D1 resetado com schema.d1.sql
- [ ] Deploy completou com sucesso
- [ ] Site carrega corretamente
- [ ] Criar post funciona sem erro `D1_TYPE_ERROR`

## 🎯 Resultado Esperado

- Deploy 100% TypeScript/Node.js
- Nenhuma menção a Python Workers
- Posts criados com sucesso
- Performance melhorada (10-20x mais rápido)
