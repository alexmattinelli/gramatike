# Guia de Recuperação do Banco de Dados D1

## Problema: Tabelas Apagadas

Se você apagou algumas tabelas do banco de dados D1, isso pode causar vários problemas no feed e em outras partes da aplicação.

## Tabelas Essenciais para o Feed Funcionar

### 1. Autenticação
```sql
user              -- Usuários da plataforma
user_session      -- Sessões de login
```

### 2. Feed de Posts
```sql
post              -- Posts criados
post_likes        -- Curtidas em posts
post_image        -- Imagens anexadas aos posts
comentario        -- Comentários nos posts
```

### 3. Relacionamentos Sociais
```sql
seguidories       -- Quem segue quem
amizade           -- Amizades (seguimento mútuo)
```

### 4. Outras Tabelas Importantes
```sql
notification      -- Notificações
divulgacao        -- Avisos e divulgações
report            -- Denúncias
blocked_word      -- Palavras bloqueadas (moderação)
```

### 5. Conteúdo Educacional
```sql
edu_topic         -- Tópicos educacionais
edu_content       -- Conteúdo educacional
exercise_topic    -- Tópicos de exercícios
exercise_section  -- Seções de exercícios
exercise_question -- Questões de exercícios
```

### 6. Outras Features
```sql
dynamic           -- Dinâmicas/jogos
dynamic_response  -- Respostas das dinâmicas
palavra_do_dia    -- Palavra do dia
palavra_do_dia_interacao -- Interações com palavra do dia
support_ticket    -- Tickets de suporte
```

## Como Verificar se as Tabelas Existem

### Opção 1: Via Wrangler CLI
```bash
# Listar todas as tabelas
wrangler d1 execute gramatike-db --command="SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
```

### Opção 2: Via Cloudflare Dashboard
1. Acesse Cloudflare Dashboard
2. Vá em Workers & Pages
3. Clique em D1
4. Selecione seu database (gramatike-db)
5. Vá na aba "Tables" ou "Console"
6. Execute: `SELECT name FROM sqlite_master WHERE type='table';`

## Como Recriar as Tabelas

### Método Completo (Recomendado)

Se você tem o arquivo `schema.d1.sql` no repositório:

```bash
# 1. Fazer backup do banco atual (se tiver dados importantes)
wrangler d1 backup create gramatike-db

# 2. Aplicar o schema completo
wrangler d1 execute gramatike-db --file=schema.d1.sql
```

### Método Seletivo

Se só faltam algumas tabelas específicas:

```bash
# Criar tabela user se não existe
wrangler d1 execute gramatike-db --command="
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email_confirmed INTEGER DEFAULT 0,
    email_confirmed_at TEXT,
    foto_perfil TEXT DEFAULT 'img/perfil.png',
    genero TEXT,
    pronome TEXT,
    bio TEXT,
    data_nascimento TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    is_admin INTEGER DEFAULT 0,
    is_superadmin INTEGER DEFAULT 0,
    is_banned INTEGER DEFAULT 0,
    banned_at TEXT,
    ban_reason TEXT,
    suspended_until TEXT
);
"

# Criar tabela user_session se não existe
wrangler d1 execute gramatike-db --command="
CREATE TABLE IF NOT EXISTS user_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    user_agent TEXT,
    ip_address TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);
"

# Continue para outras tabelas essenciais...
```

## Problemas Comuns Causados por Tabelas Faltando

### Sintoma: "Não consigo fazer login"
**Causa:** Tabelas `user` ou `user_session` faltando  
**Solução:** Recriar essas tabelas

### Sintoma: "Feed aparece vazio"
**Causa:** Tabelas `post`, `post_likes`, `comentario` faltando  
**Solução:** Recriar essas tabelas

### Sintoma: "Amigues não aparecem"
**Causa:** Tabelas `seguidories` ou `amizade` faltando  
**Solução:** Recriar essas tabelas

### Sintoma: "Avatar não aparece"
**Causa:** 
- Coluna `foto_perfil` faltando na tabela `user`
- Session query não buscando o campo (CORRIGIDO em abef1bd)

**Solução:** 
- Verificar se coluna existe: `PRAGMA table_info(user);`
- Se não existir, adicionar: `ALTER TABLE user ADD COLUMN foto_perfil TEXT DEFAULT 'img/perfil.png';`

## Correção Recente (Commit abef1bd)

Descobrimos que mesmo com a tabela `user` completa, o campo `foto_perfil` não estava sendo buscado da sessão.

**O que foi corrigido:**
1. `gramatike_d1/db.py` - Adicionado `u.foto_perfil` na query de sessão
2. `gramatike_d1/auth.py` - Adicionado `foto_perfil` no dict retornado por `get_current_user()`

**Antes:**
```python
# foto_perfil sempre None, avatar sempre mostrava inicial
current_user = {
    'id': user_id,
    'username': username,
    'email': email,
    'is_admin': ...,
}
```

**Depois:**
```python
# foto_perfil vem do banco, avatar mostra foto real
current_user = {
    'id': user_id,
    'username': username,
    'email': email,
    'foto_perfil': foto_perfil,  # ← NOVO
    'is_admin': ...,
}
```

## Validação

Para verificar se tudo está funcionando:

### 1. Verificar se user tem foto_perfil
```sql
SELECT id, username, foto_perfil FROM user LIMIT 5;
```

### 2. Verificar se sessões estão ativas
```sql
SELECT 
    s.token, 
    u.username, 
    u.foto_perfil,
    s.expires_at 
FROM user_session s 
JOIN user u ON s.user_id = u.id 
WHERE s.expires_at > datetime('now');
```

### 3. Testar o feed
1. Faça login em `/login`
2. Deve redirecionar para `/feed`
3. Avatar deve aparecer no header (desktop)
4. Posts devem carregar
5. Amigues devem aparecer (se tiver seguimento mútuo)

## Quando Usar Cada Abordagem

### Banco Vazio / Quase Vazio
→ Use `wrangler d1 execute gramatike-db --file=schema.d1.sql`

### Banco Com Dados, Faltando Só Algumas Tabelas
→ Use CREATE TABLE IF NOT EXISTS para cada tabela faltando

### Banco Com Dados, Faltando Colunas
→ Use ALTER TABLE ADD COLUMN para adicionar colunas

## Backup Antes de Qualquer Mudança

**SEMPRE** faça backup antes de modificar o schema:

```bash
# Criar backup
wrangler d1 backup create gramatike-db --output backup-$(date +%Y%m%d-%H%M%S).sql

# Listar backups
wrangler d1 backup list gramatike-db

# Restaurar backup (se necessário)
wrangler d1 backup restore gramatike-db --backup-id=BACKUP_ID
```

## Resumo

1. ✅ **Commit abef1bd** corrigiu o problema de foto_perfil não aparecer
2. ⚠️ **Verifique** se todas as tabelas essenciais existem
3. 🔧 **Recrie** tabelas faltando usando `schema.d1.sql`
4. 💾 **Sempre faça backup** antes de modificar schema
5. ✅ **Teste** o feed após recriar tabelas

---

**Status:** Com o commit abef1bd, o avatar agora funciona corretamente desde que a tabela `user` tenha a coluna `foto_perfil`.
