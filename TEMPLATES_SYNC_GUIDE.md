# 🔄 Guia: Como Manter Templates Sincronizados

## Situação Atual

Você está usando **Cloudflare Workers** com código Python nativo em `index.py`.

**❌ Problema:** Os arquivos `.html` em `gramatike_app/templates/` **NÃO são usados** em produção.

**✅ Solução:** Todo HTML precisa estar **hardcoded no `index.py`**.

---

## Como Funciona

### Deploy Flask Local (Desenvolvimento)
```
gramatike_app/templates/*.html → Flask lê os arquivos
```

### Deploy Cloudflare Workers (Produção)  
```
index.py → HTML está dentro das funções _*_page()
```

---

## Workflow Correto

### 1️⃣ Editando Templates

Quando você quer mudar uma página:

**❌ NÃO faça:**
```bash
# Editar gramatike_app/templates/admin/dashboard.html
# git push
# wrangler deploy
```

**✅ FAÇA:**
```bash
# 1. Edite o HTML diretamente no index.py
vim index.py  # Procure por "async def _admin_page"

# 2. Commit e deploy
git add index.py
git commit -m "Update admin dashboard"
git push origin main
npm run deploy
```

---

## Páginas Implementadas no Workers

Todas essas páginas já existem no `index.py`:

- ✅ `_index_page` - Feed principal (/)
- ✅ `_educacao_page` - Educação (/educacao)
- ✅ `_login_page` - Login (/login)
- ✅ `_cadastro_page` - Cadastro (/cadastro)
- ✅ `_dinamicas_page` - Dinâmicas
- ✅ `_exercicios_page` - Exercícios
- ✅ `_artigos_page` - Artigos
- ✅ `_apostilas_page` - Apostilas
- ✅ `_podcasts_page` - Podcasts
- ✅ `_profile_page` - Perfil de usuário
- ✅ `_novo_post_page` - Criar post
- ✅ `_meu_perfil_page` - Meu perfil
- ✅ `_configuracoes_page` - Configurações
- ✅ `_admin_page` - Dashboard admin (✨ ATUALIZADO)
- ✅ `_esqueci_senha_page` - Recuperar senha
- ✅ `_reset_senha_page` - Resetar senha

---

## Como Atualizar uma Página

### Exemplo: Atualizar Dashboard Admin

1. **Abra o index.py:**
```python
async def _admin_page(self, db, current_user):
    # HTML está aqui dentro
    return f"""
    <html>
    ...
    </html>
    """
```

2. **Edite o HTML diretamente:**
```python
async def _admin_page(self, db, current_user):
    return f"""
    <html>
    <h1>Novo Título do Dashboard</h1>
    <!-- Seu HTML aqui -->
    </html>
    """
```

3. **Salve e faça deploy:**
```bash
git add index.py
git commit -m "Update dashboard title"
git push origin main
npm run deploy
```

4. **Aguarde ~30 segundos** e acesse:
```
https://www.gramatike.com.br/admin/
```

---

## Dicas Importantes

### 1. Versão do Script

Sempre atualize a versão quando fizer mudanças:

```python
SCRIPT_VERSION = "v2025.12.01.c-sua-mudanca"
```

Isso ajuda a confirmar que o deploy foi feito.

### 2. Escapando Código Python

Use `{{` e `}}` para chaves duplas literais:

```python
# ❌ Errado
<style>
  .class { color: red; }
</style>

# ✅ Correto  
<style>
  .class {{ color: red; }}
</style>
```

### 3. Variáveis Python

Use f-strings normalmente:

```python
return f"""
<h1>Olá, {escape_html(current_user.get('username'))}!</h1>
<p>Total de posts: {total_posts}</p>
"""
```

---

## Arquivos que Você Pode Ignorar

Estes arquivos **NÃO são usados** em produção (Workers):

```
gramatike_app/
├── templates/          ← ❌ Ignorar em produção
│   ├── *.html         
│   └── admin/*.html   
├── routes/            ← ❌ Ignorar (Flask)
├── forms.py           ← ❌ Ignorar (Flask)
└── __init__.py        ← ❌ Ignorar (Flask)
```

Estes arquivos são usados **apenas para desenvolvimento local** com Flask.

---

## O Que Usar

### Para Produção (Workers):
```
index.py          ← ✅ TODO o código aqui
gramatike_d1/     ← ✅ Funções de banco de dados
wrangler.toml     ← ✅ Configuração Workers
```

### Para Desenvolvimento Local:
```
gramatike_app/    ← ✅ App Flask completo
run.py            ← ✅ Servidor local
```

---

## Checklist de Deploy

Antes de fazer deploy:

- [ ] Editou HTML no `index.py` (não nos arquivos `.html`)
- [ ] Atualizou `SCRIPT_VERSION` 
- [ ] Testou localmente se possível
- [ ] Commit com mensagem descritiva
- [ ] `npm run deploy`
- [ ] Aguardou 30 segundos
- [ ] Limpou cache do navegador (Ctrl+Shift+R)
- [ ] Verificou no domínio www.gramatike.com.br

---

## Comandos Úteis

```bash
# Ver versão deployada
curl https://www.gramatike.com.br/ | grep SCRIPT_VERSION

# Deploy
npm run deploy

# Ver logs
wrangler tail

# Testar localmente (Workers)
npm run dev

# Testar localmente (Flask)
.venv/bin/flask run
```

---

## ⚡ Status Atual

✅ **Dashboard Admin** - Atualizado com 5 abas completas
✅ **Todas as páginas** - Implementadas no index.py
✅ **Deploy** - Funcionando em www.gramatike.com.br

**Próxima vez que editar:** Lembre-se de editar diretamente no `index.py`! 🚀
