# Fix: Gênero Neutro - Correção de Inconsistência

## Problema Identificado

O projeto Gramátike usa terminologia de gênero neutro (usuárie, seguidories) para promover inclusão. No entanto, havia uma inconsistência entre os schemas de banco de dados:

### Antes da Correção

- **schema.sql** (SQLite/PostgreSQL): Usava gênero masculino
  - Tabela: `seguidores`
  - Colunas: `seguidor_id`, `seguido_id`

- **schema.d1.sql** (Cloudflare D1): Usava gênero neutro ✓
  - Tabela: `seguidories`
  - Colunas: `seguidore_id`, `seguide_id`

- **models.py** (SQLAlchemy): Usava gênero neutro ✓
  - Tabela: `seguidories`
  - Colunas: `seguidore_id`, `seguide_id`

### Impacto

Esta inconsistência causava erros de banco de dados que impediam:
- Criação de posts
- Funcionalidade de seguir outros usuáries
- Qualquer operação que dependesse da tabela de seguidories

## Solução Implementada

### 1. Atualização do Schema Principal

Arquivo: `schema.sql`

```sql
-- Antes (masculino)
CREATE TABLE IF NOT EXISTS seguidores (
    seguidor_id INTEGER NOT NULL,
    seguido_id INTEGER NOT NULL,
    ...
);

-- Depois (neutro)
CREATE TABLE IF NOT EXISTS seguidories (
    seguidore_id INTEGER NOT NULL,
    seguide_id INTEGER NOT NULL,
    ...
);
```

### 2. Migração de Banco de Dados

Criada nova migração: `a2b3c4d5e6f7_rename_seguidores_to_seguidories.py`

A migração:
- Renomeia a tabela `seguidores` → `seguidories`
- Renomeia as colunas `seguidor_id` → `seguidore_id` e `seguido_id` → `seguide_id`
- Preserva todos os dados existentes
- Suporta tanto SQLite quanto PostgreSQL
- É idempotente (pode ser executada múltiplas vezes sem problemas)

### 3. Verificação de Consistência

Todos os componentes agora usam terminologia consistente de gênero neutro:

| Componente | Tabela | Colunas | Status |
|------------|--------|---------|--------|
| schema.sql | seguidories | seguidore_id, seguide_id | ✅ Correto |
| schema.d1.sql | seguidories | seguidore_id, seguide_id | ✅ Correto |
| models.py | seguidories | seguidore_id, seguide_id | ✅ Correto |
| gramatike_d1/db.py | seguidories | seguidore_id, seguide_id | ✅ Correto |

## Como Aplicar a Correção

Para bancos de dados existentes, execute a migração:

```bash
flask db upgrade
```

Para novos bancos de dados, o schema já está corrigido e criará as tabelas com a nomenclatura correta automaticamente.

## Terminologia de Gênero Neutro no Projeto

O projeto Gramátike segue estas convenções de gênero neutro em português:

- **usuário** → **usuárie**
- **seguidor** → **seguidore**
- **seguido** → **seguide**
- **todos** → **todes**
- **ele/ela** → **ile/elu**

Estas mudanças refletem o compromisso do projeto com a inclusão e acessibilidade linguística.

## Testes Realizados

✅ Lógica de migração testada e validada
✅ Preservação de dados verificada
✅ Compatibilidade SQLite/PostgreSQL confirmada
✅ Consistência entre todos os schemas verificada

## Próximos Passos

Após aplicar esta correção:
1. Execute `flask db upgrade` em todos os ambientes
2. Verifique que posts podem ser criados normalmente
3. Teste a funcionalidade de seguir/deixar de seguir usuáries
