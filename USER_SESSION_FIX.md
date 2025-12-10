# Fix: user_session Column Name Mismatch

## Problema

O sistema estava apresentando erro de login com a seguinte mensagem:

```
D1_ERROR: table user_session has no column named user_id: SQLITE_ERROR
```

## Causa Raiz

A tabela `user_session` foi criada com o nome de coluna `usuarie_id`, mas o código tentava referenciar `user_id`:

### Antes (Errado)
```python
# Criação da tabela (linha 544)
CREATE TABLE IF NOT EXISTS user_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuarie_id INTEGER NOT NULL,  # ❌ Nome errado
    ...
)

# Inserção de dados (linha 1012)
INSERT INTO user_session (user_id, token, ...)  # ❌ Referência ao nome correto
VALUES (?, ?, ...)
```

Esta inconsistência causava falha em todas as tentativas de login.

## Solução Implementada

### 1. Correção do Schema (Linhas 540-552)

Atualizado a criação da tabela para usar `user_id`:

```python
CREATE TABLE IF NOT EXISTS user_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,  # ✅ Nome correto
    token TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT NOT NULL,
    user_agent TEXT,
    ip_address TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
)
```

### 2. Migração Automática (Linhas 554-600)

Adicionada lógica de migração automática para bancos de dados existentes:

```python
# 1. Detecta se a tabela tem a coluna antiga
pragma_result = await db.prepare("PRAGMA table_info(user_session)").all()

if 'usuarie_id' in columns and 'user_id' not in columns:
    # 2. Cria nova tabela com schema correto
    CREATE TABLE user_session_new (...)
    
    # 3. Copia dados preservando sessões
    INSERT INTO user_session_new (id, user_id, ...)
    SELECT id, usuarie_id, ...  # Mapeia coluna antiga para nova
    FROM user_session
    
    # 4. Substitui tabela antiga
    DROP TABLE user_session
    ALTER TABLE user_session_new RENAME TO user_session
    
    # 5. Recria índices
    CREATE INDEX idx_session_token ON user_session(token)
    CREATE INDEX idx_session_user ON user_session(user_id)
    CREATE INDEX idx_session_expires ON user_session(expires_at)
```

### 3. Correção de Queries (Linha 2615)

Atualizada a query de estatísticas:

```python
# Antes
SELECT COUNT(DISTINCT usuarie_id) as count FROM user_session  # ❌

# Depois
SELECT COUNT(DISTINCT user_id) as count FROM user_session  # ✅
```

## Comportamento da Migração

### Quando Ocorre
- Automaticamente na primeira requisição após o deploy
- Executada pela função `ensure_database_initialized()`
- Executada apenas uma vez (detecta se já foi migrada)

### Segurança
- Verifica existência de `pragma_result.results` antes de iterar
- Tratamento de erros com try/except
- Logs detalhados para monitoramento
- Preserva todas as sessões de usuário existentes

### Logs Gerados

**Sucesso:**
```
[D1 Migration] Detectada coluna usuarie_id em user_session, migrando para user_id...
[D1 Migration] Migração de user_session concluída com sucesso!
```

**Falha (não bloqueia o sistema):**
```
[D1 Migration Warning] Erro ao verificar/migrar user_session: {erro}
```

## Impacto

### Deployments Novos
- ✅ Tabelas criadas com schema correto desde o início
- ✅ Login funciona imediatamente

### Deployments Existentes
- ✅ Migração automática na primeira requisição
- ✅ Sessões de usuário preservadas
- ✅ Login funciona após migração
- ✅ Zero downtime (migração é rápida)

## Arquivos Modificados

```
gramatike_d1/db.py
- 51 linhas adicionadas
- 3 linhas modificadas
```

### Mudanças Específicas:
1. **Linha 544**: `usuarie_id` → `user_id` (criação da tabela)
2. **Linha 550**: Foreign key atualizada para `user_id`
3. **Linhas 554-600**: Adicionada lógica de migração automática
4. **Linha 2615**: Query de estatísticas atualizada

## Validação

### Verificações Realizadas
- ✅ Sintaxe Python válida (`py_compile`)
- ✅ Code Review aprovada (2 comentários endereçados)
- ✅ CodeQL Security Scan: 0 vulnerabilidades
- ✅ Schema consistente com `schema.d1.sql`

### Alinhamento com Schema Oficial

O arquivo `schema.d1.sql` (schema autoritativo) já usa `user_id`:

```sql
CREATE TABLE IF NOT EXISTS user_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,  -- ✅ Correto desde sempre
    token TEXT UNIQUE NOT NULL,
    ...
);
```

## Deployment

### Para Produção (Cloudflare D1)

1. **Merge do PR**
2. **Deploy Automático**: `npm run deploy`
3. **Migração Automática**: Ocorre na primeira requisição
4. **Monitoramento**: Verificar logs do Cloudflare Workers

### Rollback (se necessário)

Como a migração preserva dados e é não-destrutiva:
- Não é necessário rollback manual
- Em caso de problemas, re-deploy da versão anterior funciona
- Sessões antigas permanecem válidas

## Testes Sugeridos Pós-Deploy

1. ✅ Tentar fazer login com usuário existente
2. ✅ Verificar criação de nova sessão
3. ✅ Confirmar persistência de sessão após reload
4. ✅ Verificar logout funcionando
5. ✅ Checar logs do Cloudflare Workers para mensagens de migração

## Referências

- **Issue Original**: Login error "table user_session has no column named user_id"
- **PR**: #[número]
- **Arquivos**: `gramatike_d1/db.py`, `schema.d1.sql`
- **Commits**:
  - Fix user_session table column name mismatch (usuarie_id -> user_id)
  - Add migration to fix existing user_session tables with usuarie_id column
  - Improve migration safety by checking pragma_result.results properly

## Contato

Para dúvidas ou problemas relacionados a esta correção, verificar:
- Logs do Cloudflare Workers Dashboard
- Tabela `user_session` via `wrangler d1 execute gramatike --command="PRAGMA table_info(user_session)"`
