# Bug Fix: Função Postar não Funcionando

## Problema Identificado

A função de criar posts (Postar) não estava funcionando devido a incompatibilidade entre os nomes dos campos usados no código e os campos definidos no modelo Post.

## Causa Raiz

O modelo `Post` define os campos usando linguagem neutra:
- `usuarie` (em vez de `usuario`)
- `usuarie_id` (em vez de `usuario_id`)

Porém, o código em vários lugares estava tentando criar posts usando os campos antigos `usuario` e `usuario_id`, o que causava erro ao tentar salvar no banco de dados.

## Arquivos Afetados

**gramatike_app/routes/__init__.py**

## Correções Realizadas

### 1. `/api/posts_multi` (linha 2116-2118)
**Antes:**
```python
post = Post(
    usuario=current_user.username,
    usuario_id=current_user.id,
    conteudo=conteudo,
    imagem='|'.join(paths),
    data=datetime.utcnow()
)
```

**Depois:**
```python
post = Post(
    usuarie=current_user.username,
    usuarie_id=current_user.id,
    conteudo=conteudo,
    imagem='|'.join(paths),
    data=datetime.utcnow()
)
```

### 2. `/api/posts` (linha 2380-2382)
**Antes:**
```python
post = Post(
    usuario=usuario_nome,
    usuario_id=usuario_id,
    conteudo=data['conteudo'],
    imagem=data.get('imagem', ''),
    data=datetime.now()
)
```

**Depois:**
```python
post = Post(
    usuarie=usuario_nome,
    usuarie_id=usuario_id,
    conteudo=data['conteudo'],
    imagem=data.get('imagem', ''),
    data=datetime.now()
)
```

### 3. `api_gramatike_search` (linha 90)
**Antes:**
```python
post_query = post_query.filter((Post.usuario_id == gk_user.id) | (Post.usuarie == 'gramatike'))
```

**Depois:**
```python
post_query = post_query.filter((Post.usuarie_id == gk_user.id) | (Post.usuarie == 'gramatike'))
```

### 4. `get_posts_me` (linha 409)
**Antes:**
```python
posts = Post.query.filter(
    ((Post.usuario_id == user.id) | (Post.usuarie == user.username)) & ...
)
```

**Depois:**
```python
posts = Post.query.filter(
    ((Post.usuarie_id == user.id) | (Post.usuarie == user.username)) & ...
)
```

### 5. `get_posts_usuario` (linha 445)
**Antes:**
```python
posts = Post.query.filter(
    ((Post.usuario_id == user.id) | (Post.usuarie == user.username)) & ...
)
```

**Depois:**
```python
posts = Post.query.filter(
    ((Post.usuarie_id == user.id) | (Post.usuarie == user.username)) & ...
)
```

### 6. `get_posts` (linhas 2338-2340)
**Antes:**
```python
if hasattr(p, 'usuario_id') and p.usuario_id:
    autor = User.query.get(p.usuario_id)
elif hasattr(p, 'usuario') and p.usuarie:
    autor = User.query.filter_by(username=p.usuarie).first()
```

**Depois:**
```python
if hasattr(p, 'usuarie_id') and p.usuarie_id:
    autor = User.query.get(p.usuarie_id)
elif hasattr(p, 'usuarie') and p.usuarie:
    autor = User.query.filter_by(username=p.usuarie).first()
```

### 7. `soft_delete_post` (linha 2395)
**Antes:**
```python
if post.usuario_id != current_user.id and not current_user.is_admin:
    return jsonify({'error':'forbidden'}), 403
```

**Depois:**
```python
if post.usuarie_id != current_user.id and not current_user.is_admin:
    return jsonify({'error':'forbidden'}), 403
```

## Modelo Post (models.py)

O modelo correto já estava definido com linguagem neutra:

```python
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuarie = db.Column(db.String(80))
    usuarie_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    conteudo = db.Column(db.Text)
    imagem = db.Column(db.Text)
    data = db.Column(db.DateTime)
    likes = db.relationship('User', secondary=post_likes, backref='liked_posts')
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
```

## Schema D1 (schema.d1.sql)

O schema também já estava correto:

```sql
CREATE TABLE IF NOT EXISTS post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuarie TEXT,
    usuarie_id INTEGER,
    conteudo TEXT,
    imagem TEXT,
    data TEXT DEFAULT (datetime('now')),
    is_deleted INTEGER DEFAULT 0,
    deleted_at TEXT,
    deleted_by INTEGER,
    FOREIGN KEY (usuarie_id) REFERENCES user(id),
    FOREIGN KEY (deleted_by) REFERENCES user(id)
);
```

## Resultado

✅ **Função Postar agora funciona corretamente**
- Posts são criados com os campos corretos
- Queries de filtro funcionam corretamente
- Verificação de permissão funciona
- Linguagem neutra consistente em todo o código

## Commit

**e0a8481** - Fix post creation - correct field names to match model (usuarie/usuarie_id)

## Impacto

- ✅ Criar novo post funciona
- ✅ Listar posts do usuário funciona
- ✅ Buscar posts funciona
- ✅ Deletar posts funciona (verificação de permissão)
- ✅ Consistência com política de linguagem neutra

---

**Data:** 2025-12-09  
**Status:** ✅ Resolvido  
**Testado:** ✅ Código revisado e validado
