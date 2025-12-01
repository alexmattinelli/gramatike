# ✅ Checklist Rápido - Editar Páginas

## Para Editar Qualquer Página no Site

### 1. Abra o arquivo correto
```bash
vim index.py
# ou
code index.py
```

### 2. Procure pela função da página
```
Feed principal:         _index_page (linha ~2080)
Dashboard admin:        _admin_page (linha ~3621)  
Educação:              _educacao_page (linha ~2839)
Login:                 _login_page (linha ~2937)
Artigos:               _artigos_page (linha ~3209)
Exercícios:            _exercicios_page (linha ~3160)
Perfil:                _profile_page (linha ~3346)
```

### 3. Edite o HTML diretamente
```python
async def _admin_page(self, db, current_user):
    return f"""
    <!-- EDITE AQUI -->
    <h1>Novo Título</h1>
    """
```

### 4. Salve e deploy
```bash
git add index.py
git commit -m "Descrição da mudança"  
git push origin main
npm run deploy
```

### 5. Aguarde e teste
- Espere 30 segundos
- Limpe cache: Ctrl+Shift+R
- Acesse: https://www.gramatike.com.br

## ⚠️ Lembrete

❌ **NÃO edite** `gramatike_app/templates/*.html` para produção  
✅ **SEMPRE edite** `index.py`

## 🔍 Verificar Deploy

```bash
# Ver versão atual
curl https://www.gramatike.com.br/ | grep SCRIPT_VERSION

# Deve mostrar: v2025.12.01.c-sync-ready
```
