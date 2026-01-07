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
   - D1 database: Selecione `gramatike` (ID: `d0984113-06be-49f5-939a-9d5c5dcba7b6`)
3. Clique em **Save**

### 4. Configurar R2 Storage Binding (se necessário)

1. Vá em **Settings** → **Functions**
2. Em **R2 bucket bindings**, clique **Add binding**:
   - Variable name: `R2_BUCKET`
   - R2 bucket: Selecione `gramatike`
3. Clique em **Save**

### 5. Configurar Environment Variables

Vá em **Settings** → **Environment variables** e adicione:

**Production & Preview:**

| Variable | Value |
|----------|-------|
| `CLOUDFLARE_ACCOUNT_ID` | `0add1ab8e89c1da5cbeacd743c71b254` |
| `CLOUDFLARE_API_TOKEN` | `5-MjlsFQIDg13qiBxclv2883uLG1eOktw_n5vd_-` |
| `CLOUDFLARE_R2_ACCESS_KEY_ID` | `61ac0fe5f2319f1bc9e337f14ffaa6a9` |
| `CLOUDFLARE_R2_BUCKET` | `gramatike` |
| `CLOUDFLARE_R2_PUBLIC_URL` | `https://pub-66c93dcfe2824d17a97ed607b0a8e3d1.r2.dev` |
| `CLOUDFLARE_R2_S3_ENDPOINT` | `https://0add1ab8e89c1da5cbeacd743c71b254.r2.cloudflarestorage.com` |
| `CLOUDFLARE_R2_SECRET_ACCESS_KEY` | `14404703da060469c45fcca6044e89eef2992729ac169d4c778f9a0ffe45063a` |
| `MAIL_DEFAULT_SENDER` | `no-replay@gramatike.com.br` |
| `MAIL_PASSWORD` | `ZjKEdJzXQ7ngky3f` |
| `MAIL_PORT` | `587` |
| `MAIL_SENDER_NAME` | `Gramátike` |
| `MAIL_SERVER` | `smtp-relay.brevo.com` |
| `MAIL_USERNAME` | `96ece6002@smtp-brevo.com` |
| `MAIL_USE_TLS` | `true` |
| `SECRET_KEY` | *(seu valor secreto)* |

### 6. Resetar Banco D1

Após configurar tudo:

```bash
wrangler d1 execute gramatike --file=./schema.d1.sql --remote
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
