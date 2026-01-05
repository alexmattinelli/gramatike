# Guia de Troubleshooting: D1_TYPE_ERROR

## Se o Problema AINDA Persistir

Se após aplicar o fix do commit 3d3fd93 você ainda ver:
```
Error: D1_TYPE_ERROR: Type 'undefined' not supported for value 'undefined'
```

Siga estes passos:

---

## Passo 1: Verificar se o Deploy Foi Feito

### No Cloudflare Dashboard:

1. Acesse: https://dash.cloudflare.com
2. Vá em "Workers & Pages"
3. Clique no seu worker/page "gramatike"
4. Verifique a data/hora do último deploy
5. **Se não for recente**: Force um novo deploy

### Como Forçar Deploy:

```bash
# No terminal local:
git push origin copilot/fix-postar-layout-error --force-with-lease

# Ou via Cloudflare Dashboard:
# Deployments → Retry deployment
```

---

## Passo 2: Limpar Caches

### A. Cache do Cloudflare Workers

No Cloudflare Dashboard:
1. Workers & Pages → seu worker
2. Settings → Rollback
3. Faça rollback e depois volte para a versão atual
4. Isso força recarga do código

### B. Cache do Navegador

1. Abra DevTools (F12)
2. Vá em Network
3. Marque "Disable cache"
4. Faça Hard Refresh (Ctrl+Shift+R)

---

## Passo 3: Verificar Logs no Console

Abra o console do navegador (F12) e procure por:

### ✅ Log ESPERADO (sucesso):
```
[posts_multi] Creating post: usuarie_id=123 (type=int), conteudo_length=20, imagem=None
[create_post] FINAL VALUES: usuarie_id=123 -> 123, conteudo=... -> ..., imagem=None -> None
```

### ❌ Log de ERRO (problema):
```
[posts_multi Error] D1_TYPE_ERROR: Type 'undefined' not supported for value 'undefined'
```

**SE VER O ERRO**: Copie o traceback COMPLETO e cole aqui.

---

## Passo 4: Verificar Qual Linha Causa o Erro

O traceback mostrará a linha exata. Procure por:

### Cenário A: Erro em `create_post()` linha 1607-1616
```
File "gramatike_d1/db.py", line 1612, in create_post
```

**Significado**: `usuarie_id`, `usuarie`, `conteudo` ou `imagem` está undefined

**Fix**: Adicione sanitização de `conteudo` também:
```python
# ADICIONE antes de create_post:
conteudo = sanitize_for_d1(conteudo)
usuarie_id = sanitize_for_d1(usuarie_id)
```

### Cenário B: Erro em `process_mentions()` linha 4364
```
File "gramatike_d1/db.py", line 4364, in process_mentions
```

**Significado**: `autor_id` ou `item_id` está undefined

**Fix**: Sanitize antes de chamar process_mentions:
```python
autor_id_safe = sanitize_for_d1(usuarie_id)
item_id_safe = sanitize_for_d1(post_id)
await process_mentions(db, conteudo, autor_id_safe, 'post', item_id_safe)
```

### Cenário C: Erro em `process_hashtags()` linha 4463
```
File "gramatike_d1/db.py", line 4463, in process_hashtags
```

**Significado**: Similar ao B, `item_id` está undefined

**Fix**: Mesmo do cenário B

---

## Passo 5: Verificar Autenticação

Se o erro menciona `usuarie_id`, pode ser que o usuário não esteja autenticado corretamente.

### Teste:

1. Faça logout completo
2. Limpe cookies do site
3. Faça login novamente
4. Tente criar um post

### Verificar no Console:

Procure por:
```
[Auth] User authenticated: username (ID: 123)
```

**Se NÃO aparecer**: Problema de autenticação, não de D1_TYPE_ERROR.

---

## Passo 6: Testar com Diferentes Conteúdos

Teste criar posts com diferentes tipos de conteúdo:

### Teste 1: Texto Simples
```
"Olá mundo"
```

### Teste 2: Com Menção
```
"Oi @admin"
```

### Teste 3: Com Hashtag
```
"Teste #gramática"
```

### Teste 4: Com Emoji
```
"Teste 😀"
```

**Anote qual tipo falha** - isso ajuda identificar o problema.

---

## Passo 7: Verificar Código Sendo Executado

### No Console do Navegador:

Digite e execute:
```javascript
fetch('/api/posts_multi', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({conteudo: 'teste direto'})
}).then(r => r.json()).then(console.log)
```

**Se funcionar**: Problema está no frontend (criar_post.html)
**Se falhar**: Problema está no backend (index.py)

---

## Passo 8: Último Recurso - Debug Mode

### Adicione Logs Extras Temporariamente:

No arquivo `index.py`, linha ~1430, adicione:

```python
console.log(f"[DEBUG] usuarie_id type: {type(usuarie_id)}")
console.log(f"[DEBUG] usuarie_id value: {usuarie_id}")
console.log(f"[DEBUG] usuarie_id repr: {repr(usuarie_id)}")
console.log(f"[DEBUG] usuarie_id str: {str(usuarie_id)}")

# Tenta converter para ver se é JsProxy
try:
    if hasattr(usuarie_id, 'to_py'):
        console.log(f"[DEBUG] usuarie_id.to_py(): {usuarie_id.to_py()}")
except Exception as e:
    console.log(f"[DEBUG] to_py failed: {e}")
```

Isso mostrará EXATAMENTE o que `usuarie_id` é no momento.

---

## Informações a Fornecer se Ainda Não Funcionar

Se após TUDO isso o problema persistir, forneça:

1. **Traceback completo** do erro (do console F12)
2. **Logs do console** mostrando [posts_multi] e [create_post]
3. **Qual teste falhou** (Passo 6)
4. **Resultado do fetch direto** (Passo 7)
5. **Logs de debug** (Passo 8)
6. **Data/hora do último deploy** no Cloudflare

---

## Fixes Adicionais Possíveis

### Se usuarie_id é o problema:

```python
# Adicione ANTES de create_post():
usuarie_id = sanitize_for_d1(usuarie_id)
if usuarie_id is None:
    console.error("[posts_multi] usuarie_id is None after sanitize")
    return json_response({"error": "Auth error"}, 400)

# Força conversão para int
try:
    usuarie_id = int(usuarie_id)
except (ValueError, TypeError):
    console.error(f"[posts_multi] Cannot convert usuarie_id to int: {usuarie_id}")
    return json_response({"error": "Invalid user ID"}, 400)
```

### Se conteudo é o problema:

```python
# Adicione ANTES de create_post():
conteudo = sanitize_for_d1(conteudo)
if not conteudo or conteudo == 'undefined':
    console.error("[posts_multi] conteudo invalid after sanitize")
    return json_response({"error": "Conteúdo inválido"}, 400)

# Força conversão para string
conteudo = str(conteudo) if conteudo else ''
```

### Se imagem é o problema:

```python
# Já está None, mas force sanitização:
imagem = sanitize_for_d1(None)  # Garante JS null
```

---

## Referência Rápida

| Sintoma | Causa Provável | Fix |
|---------|---------------|-----|
| Erro logo após submit | `usuarie_id` undefined | Sanitize usuarie_id |
| Erro após "Creating post" log | Dentro de create_post() | Sanitize todos params |
| Erro após post criado | process_mentions/hashtags | Sanitize post_id |
| Sem erro mas post não aparece | Post criado mas não retornado | Check get_posts() |
| Erro "Não autenticado" | Sessão expirada | Login novamente |

---

**Última Atualização**: 2026-01-05 após commit 3d3fd93  
**Próximos Passos**: Deploy, testar, reportar resultado
