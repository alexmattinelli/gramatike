# Deployment - Gramátike no Cloudflare Pages

## ✅ Arquitetura

- **Runtime:** Cloudflare Pages Functions (TypeScript/JavaScript)
- **Banco:** Cloudflare D1 (SQLite)
- **Storage:** Cloudflare R2 (opcional)
- **NÃO usa:** Python, Flask, Python Workers

## 📁 Estrutura

```
public/
  ├── index.html → Redireciona para /feed
  ├── templates/ → Templates HTML
  └── static/ → CSS, JS, imagens

functions/
  ├── feed.ts → Serve feed.html
  ├── novo_post.ts → Serve criar_post.html
  ├── perfil/[username].ts → Serve perfil.html
  └── api/ → APIs REST (já implementadas)
```

## 🚀 Como funciona

1. Usuário acessa `/feed`
2. `functions/feed.ts` é executado
3. Busca `/templates/feed.html` do `public/`
4. Retorna HTML com header correto
5. JavaScript no HTML chama as APIs em `/api/*`

## 🔧 Build

```bash
npm run build
```

Apenas valida que está pronto. Os arquivos já estão em `public/`.

## 📦 Deploy

Cloudflare Pages faz deploy automático quando há push na branch `main`.

### Manual:
```bash
wrangler pages deploy public
```

## ✅ Checklist de Deploy

- [ ] D1 database binding configurado (`DB`)
- [ ] Environment variables adicionadas
- [ ] Build command: `npm run build`
- [ ] Build output: `public`
- [ ] Compatibility flags: `nodejs_compat`
- [ ] Banco resetado: `wrangler d1 execute gramatike --file=./schema.d1.sql --remote`

## 🌐 URLs

- `/` → Redireciona para `/feed`
- `/feed` → Feed de posts
- `/novo_post` → Criar novo post
- `/perfil/@username` → Perfil de usuário
- `/meu_perfil` → Seu perfil
- `/artigos` → Artigos
- `/apostilas` → Apostilas
- `/exercicios` → Exercícios
- `/gramatike_edu` → Educação

## 🔥 Performance

- **Cloudflare Pages:** Edge computing global
- **D1:** SQLite distribuído
- **Sem Python:** 10-20x mais rápido
- **TypeScript:** Type-safe, moderno
