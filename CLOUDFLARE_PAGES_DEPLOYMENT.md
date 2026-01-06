# Guia de Deploy Cloudflare Pages

## 🎯 Resumo

Este projeto usa **Cloudflare Pages** (não Workers) com Functions (TypeScript).

## ✅ Configuração Correta

### 1. wrangler.toml

O arquivo `wrangler.toml` está configurado para Pages:

```toml
name = "gramatike"
compatibility_date = "2026-01-06"
pages_build_output_dir = "public"  # ← Isso indica Pages!

# D1 Database
[[d1_databases]]
binding = "DB"
database_name = "gramatike"
database_id = "c22cbe34-444b-40ec-9987-5e90ecc8cc91"

# R2 Storage
[[r2_buckets]]
binding = "R2_BUCKET"
bucket_name = "gramatike"
```

**Características de Pages:**
- ✅ Tem `pages_build_output_dir`
- ❌ NÃO tem `main` (isso seria Worker)
- ❌ NÃO tem `compatibility_flags` (isso seria Worker)

### 2. Deploy Automático

O deploy deve acontecer **automaticamente via integração nativa do Cloudflare Pages**, NÃO via GitHub Actions.

**Como funciona:**

1. Push para branch `main` → GitHub notifica Cloudflare
2. Cloudflare Pages faz build e deploy automaticamente
3. Deploy aparece em: https://dash.cloudflare.com → Workers & Pages → gramatike

## 🚨 Problema: "Workers Build Failed"

Se você vê o erro:

```
Workers Builds: gramatike failed
Build ID: 0d8777b9-b13f-43c1-b59c-3e2231287165
```

**Causa:** Cloudflare está tentando fazer build como Worker, não Pages.

## 🔧 Solução

### Passo 1: Verificar Configuração do Projeto

1. Acesse [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Vá em **Workers & Pages**
3. Procure por `gramatike`

**Cenário A: Existe APENAS um projeto "gramatike" (Pages)**
- ✅ Configuração correta!
- O erro pode ser temporário ou já resolvido

**Cenário B: Existem DOIS projetos "gramatike"**
- Um como **Pages** ✅
- Um como **Worker** ❌
- **Ação:** Delete o Worker, mantenha apenas o Pages

### Passo 2: Verificar Integração GitHub

No projeto Pages:

1. **Workers & Pages** → **gramatike** (Pages)
2. **Settings** → **Builds & deployments**
3. Verificar:
   - ✅ GitHub repository: `alexmattinelli/gramatike`
   - ✅ Production branch: `main`
   - ✅ Build command: `npm run build` (ou vazio)
   - ✅ Build output directory: `public`

#### 📝 Configuração Detalhada do Dashboard

**Build configuration:**
- **Framework preset**: None (ou deixe em "None")
- **Build command**: `npm run build` (ou deixe vazio - o build já está feito)
- **Build output directory**: `public` ← **IMPORTANTE!**

**Advanced settings** (geralmente não precisa mexer):
- **Root directory**: Deixe **VAZIO** ou `/` (raiz do repositório)
- **Deploy command**: Deixe **VAZIO** (Pages faz deploy automaticamente)
- **Version command**: Deixe **VAZIO** (não necessário)

**⚠️ ATENÇÃO:**
- ❌ **Root directory ≠ Build output directory**
- Root directory = raiz do repo (onde está `package.json`)
- Build output directory = `public` (onde estão os arquivos estáticos)
- O `wrangler.toml` define isso com `pages_build_output_dir = "public"`

### Passo 3: Forçar Novo Deploy

Após verificar a configuração:

```bash
# Opção 1: Push vazio para forçar deploy
git commit --allow-empty -m "Trigger Pages deploy"
git push

# Opção 2: Deploy manual via CLI
npm install
npm run deploy
```

### Passo 4: Monitorar Deploy

1. Vá em **Workers & Pages** → **gramatike** → **Deployments**
2. Veja o status do deploy
3. ✅ Deve mostrar "Success" se tudo estiver configurado corretamente

## 📋 Checklist de Configuração

Use este checklist para validar sua configuração:

- [ ] `wrangler.toml` tem `pages_build_output_dir = "public"`
- [ ] `wrangler.toml` NÃO tem campo `main`
- [ ] NÃO existe arquivo `.github/workflows/deploy.yml`
- [ ] No Cloudflare Dashboard, existe apenas UM projeto `gramatike` (tipo Pages)
- [ ] A integração GitHub está ativa (Settings → Builds & deployments)
- [ ] D1 database `gramatike` existe e tem schema aplicado
- [ ] R2 bucket `gramatike` existe

## 🆘 Troubleshooting

### Erro persiste após correções

Se o erro continuar:

1. **Delete o projeto Pages** no Cloudflare Dashboard
2. **Recrie do zero:**
   - Workers & Pages → Create → Pages
   - Connect to GitHub → Selecione `alexmattinelli/gramatike`
   - Configure:
     - Project name: `gramatike`
     - Build command: `npm run build`
     - Build output: `public`
   - Após criar, configure D1 e R2 bindings em Settings

### Build local funciona, mas deploy falha

```bash
# Teste local
npm run dev

# Verifique tipos TypeScript
npm run typecheck

# Se tudo funcionar localmente, o problema é configuração do Cloudflare
```

### Como saber se é Pages ou Worker?

**Pages:**
- Tem `pages_build_output_dir` no `wrangler.toml`
- Deploy com `wrangler pages deploy`
- Icon no Dashboard: 📄 Pages

**Worker:**
- Tem `main = "src/worker.ts"` no `wrangler.toml`
- Deploy com `wrangler deploy`
- Icon no Dashboard: ⚡ Worker

## 📚 Recursos

- [Documentação Cloudflare Pages](https://developers.cloudflare.com/pages/)
- [Cloudflare Pages Functions](https://developers.cloudflare.com/pages/functions/)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)

## ✅ Resultado Esperado

Após seguir este guia:

- ✅ Deploy automático funciona a cada push
- ✅ Sem erros de "Workers Build failed"
- ✅ Site acessível em `https://gramatike.pages.dev`
- ✅ Functions TypeScript funcionando corretamente
