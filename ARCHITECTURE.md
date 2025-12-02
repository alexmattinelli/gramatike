# ⚠️ IMPORTANTE: Arquitetura do Projeto

## 🏗️ Duas Versões da Aplicação

Este projeto tem **DUAS implementações diferentes**:

### 1. Flask (Desenvolvimento Local) 📁
```
gramatike_app/
├── templates/*.html    ← Templates Flask (Jinja2)
├── routes/            ← Rotas Flask
└── models.py          ← Models SQLAlchemy
```

**Usar quando:**
- Desenvolvimento local
- Testes com Flask
- Comando: `.venv/bin/flask run`

### 2. Cloudflare Workers (Produção) ☁️
```
index.py               ← TODO o código aqui
gramatike_d1/         ← Funções de banco D1
wrangler.toml         ← Configuração
```

**Usar quando:**
- Deploy em produção
- www.gramatike.com.br
- Comando: `npm run deploy`

---

## ⚠️ NÃO USE: Cloudflare Pages Functions

A pasta `functions/` foi removida porque conflitava com o deploy de Cloudflare Workers.
**NÃO crie arquivos em `/functions/`** - todas as rotas devem estar em `index.py`.

O arquivo `_pages.toml` é apenas para configuração de build, não para roteamento.

---

## ⚡ ATENÇÃO: Templates

### ❌ NÃO Edite Aqui (Produção):
```
gramatike_app/templates/admin/dashboard.html  ← Não usado!
gramatike_app/templates/index.html           ← Não usado!
```

### ✅ Edite Aqui:
```python
# index.py - linha ~3621
async def _admin_page(self, db, current_user):
    return f"""
    <!-- HTML aqui dentro -->
    """
```

---

## 🚀 Deploy

```bash
# 1. Edite index.py
vim index.py

# 2. Commit
git add index.py
git commit -m "Update page"
git push

# 3. Deploy (configure CLOUDFLARE_API_TOKEN primeiro)
export CLOUDFLARE_API_TOKEN="seu-token"
npm run deploy

# 4. Aguarde 30s e teste
https://www.gramatike.com.br
```

---

## 📖 Documentação Completa

Veja `TEMPLATES_SYNC_GUIDE.md` para guia completo de como manter templates sincronizados.

---

## ✅ Status Atual (2025-12-02)

- ✅ Dashboard admin com 5 abas funcionais
- ✅ Todas as páginas principais implementadas
- ✅ Deploy funcionando em www.gramatike.com.br
- ✅ Versão: v2025.12.01.c-sync-ready
- ✅ Removida pasta `functions/` que conflitava com Workers

**Próxima edição:** Lembre-se de editar `index.py`, não os `.html`! 🎯
