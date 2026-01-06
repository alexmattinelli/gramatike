# Como Resetar o Banco de Dados D1

Este guia mostra como aplicar o schema limpo ao banco de dados D1 do Gramátike.

## ⚠️ IMPORTANTE - Backup Primeiro!

Antes de resetar, faça backup dos dados importantes:

```bash
# Backup de usuários
wrangler d1 execute gramatike --command "SELECT * FROM user" > backup_users.sql

# Backup de posts
wrangler d1 execute gramatike --command "SELECT * FROM post WHERE is_deleted = 0" > backup_posts.sql

# Backup de conteúdo educacional
wrangler d1 execute gramatike --command "SELECT * FROM edu_content WHERE is_deleted = 0" > backup_edu_content.sql
```

## Aplicar Schema Limpo

### Opção 1: Resetar completamente (apaga todos os dados)

```bash
# Aplicar schema do zero
wrangler d1 execute gramatike --file=./schema.d1.sql
```

### Opção 2: Apenas criar tabelas faltantes (preserva dados existentes)

O schema usa `CREATE TABLE IF NOT EXISTS`, então você pode executá-lo de forma segura:

```bash
wrangler d1 execute gramatike --file=./schema.d1.sql
```

Isso criará apenas as tabelas que não existem, preservando as tabelas existentes.

## Verificar Estrutura do Banco

Após aplicar o schema, verifique se as tabelas foram criadas:

```bash
# Listar todas as tabelas
wrangler d1 execute gramatike --command ".tables"

# Ver estrutura de uma tabela específica
wrangler d1 execute gramatike --command ".schema user"
wrangler d1 execute gramatike --command ".schema post"
```

## Verificar Dados

```bash
# Ver usuários
wrangler d1 execute gramatike --command "SELECT id, username, email, is_admin, is_superadmin FROM user"

# Ver posts recentes
wrangler d1 execute gramatike --command "SELECT id, usuarie, conteudo, data FROM post WHERE is_deleted = 0 ORDER BY data DESC LIMIT 10"

# Contar registros
wrangler d1 execute gramatike --command "SELECT COUNT(*) as total_users FROM user"
wrangler d1 execute gramatike --command "SELECT COUNT(*) as total_posts FROM post WHERE is_deleted = 0"
```

## Criar Usuário Admin de Teste (Opcional)

Se precisar criar um usuário admin para testes:

```bash
# Nota: A senha abaixo é "admin123" - TROQUE EM PRODUÇÃO!
wrangler d1 execute gramatike --command "
INSERT INTO user (username, email, password, nome, is_superadmin, is_admin, email_confirmed)
VALUES (
    'admin',
    'admin@gramatike.com',
    '\$2a\$10\$rR5Z3qKX5jX5Z5Z5Z5Z5ZeO5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z',
    'Administrador',
    1,
    1,
    1
)
"
```

**⚠️ IMPORTANTE:** Troque a senha após primeiro login em produção!

## Solução de Problemas

### Erro: "table already exists"

Se você receber esse erro, use `DROP TABLE` antes de recriar:

```bash
# CUIDADO: Isso apaga todos os dados!
wrangler d1 execute gramatike --command "DROP TABLE IF EXISTS post"
wrangler d1 execute gramatike --command "DROP TABLE IF EXISTS user"
# ... repita para outras tabelas conforme necessário
```

### Erro: "D1_TYPE_ERROR: Type 'undefined' not supported"

Este erro ocorre quando valores `undefined` do JavaScript são passados para o D1. 
**Este PR corrige esse problema** através das funções de sanitização em `src/lib/sanitize.ts`.

Se você ainda vir este erro após o deploy:
1. Certifique-se de que o código foi deployado corretamente
2. Verifique os logs com: `wrangler pages deployment tail`
3. Procure por mensagens de log que começam com `[createPost]` ou `[createComment]`

### Verificar Logs do D1

Para ver logs de queries e erros:

```bash
# Ver logs em tempo real
wrangler pages deployment tail

# Ver logs de um deployment específico
wrangler pages deployment list
wrangler pages deployment tail <deployment-id>
```

## Ambiente Local vs Produção

### Para desenvolvimento local:

```bash
# Usar banco local
wrangler d1 execute gramatike --local --file=./schema.d1.sql

# Verificar dados locais
wrangler d1 execute gramatike --local --command "SELECT * FROM user"
```

### Para produção:

```bash
# Aplicar schema em produção (sem --local)
wrangler d1 execute gramatike --file=./schema.d1.sql

# Verificar dados em produção
wrangler d1 execute gramatike --command "SELECT * FROM user"
```

## Após Aplicar o Schema

1. **Teste a criação de posts** - Acesse a aplicação e tente criar um post
2. **Verifique os logs** - Use `wrangler pages deployment tail` para monitorar
3. **Confirme que não há erros D1_TYPE_ERROR** - Os logs devem mostrar mensagens de sucesso

## Referências

- [Documentação Wrangler D1](https://developers.cloudflare.com/workers/wrangler/commands/#d1)
- [Documentação D1 Database](https://developers.cloudflare.com/d1/)
- [Schema do Gramátike](./schema.d1.sql)
