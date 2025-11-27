# Configuração do Cloudflare D1 - Gramátike

Este guia explica como configurar o Cloudflare D1 (banco de dados SQLite na edge) para a aplicação Gramátike.

## ⚡ Início Rápido (Quick Start)

Se você está vendo o erro **"Sistema temporariamente indisponível"** ou **"Banco de dados não disponível"**, siga estes passos:

```bash
# 1. Autenticar no Cloudflare (se ainda não fez)
wrangler login

# 2. Criar o banco de dados D1 (se ainda não existe)
wrangler d1 create gramatike

# 3. IMPORTANTE: Atualize o database_id no wrangler.toml com o ID retornado acima

# 4. Criar todas as tabelas no banco de dados
wrangler d1 execute gramatike --file=./schema.d1.sql

# 5. Fazer o deploy
npm run deploy
```

**Ou use o script automatizado:**
```bash
./scripts/setup_d1_database.sh
```

---

## Por que este erro aparece?

Se você está vendo o erro **"Banco de dados não disponível. Verifique a configuração do Cloudflare D1."** na página de login ou cadastro, isso significa que:

1. O banco de dados D1 não está configurado corretamente
2. O binding do D1 não está acessível no worker
3. As tabelas do banco de dados não foram criadas

## Pré-requisitos

1. Conta no Cloudflare com Workers habilitado
2. [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/install-and-update/) instalado
3. Autenticação configurada (`wrangler login`)

## Passo 1: Criar o banco de dados D1

```bash
# Criar o banco de dados D1
wrangler d1 create gramatike
```

Você receberá uma resposta como:

```
✅ Successfully created DB 'gramatike'!

Add the following to your wrangler.toml to connect to it:

[[d1_databases]]
binding = "DB"
database_name = "gramatike"
database_id = "seu-id-aqui-xxx-xxx"
```

## Passo 2: Atualizar o wrangler.toml

O arquivo `wrangler.toml` já está configurado. Se você criou um novo banco de dados, atualize o `database_id`:

```toml
# D1 Database (SQLite na edge)
[[d1_databases]]
binding = "DB"
database_name = "gramatike"
database_id = "SEU_DATABASE_ID_AQUI"
```

## Passo 3: Criar as tabelas no D1

Execute o schema SQL para criar todas as tabelas:

```bash
# Aplicar o schema ao banco de dados D1
wrangler d1 execute gramatike --file=./schema.d1.sql
```

Para ambiente de desenvolvimento local:

```bash
# Aplicar schema ao banco local (para desenvolvimento)
wrangler d1 execute gramatike --file=./schema.d1.sql --local
```

## Passo 4: Verificar a configuração

Verifique se as tabelas foram criadas:

```bash
# Listar tabelas
wrangler d1 execute gramatike --command="SELECT name FROM sqlite_master WHERE type='table';"

# Para desenvolvimento local
wrangler d1 execute gramatike --command="SELECT name FROM sqlite_master WHERE type='table';" --local
```

Você deve ver uma lista de tabelas como:
- user
- user_session
- post
- edu_content
- exercise_topic
- exercise_question
- dynamic
- ... (muitas outras)

## Passo 5: Deploy

Faça o deploy do worker com a configuração D1:

```bash
# Usando npm (recomendado)
npm run deploy

# Ou diretamente com pywrangler
uv run pywrangler deploy
```

## Desenvolvimento Local

Para desenvolvimento local, você precisa executar o worker com D1 local:

```bash
# Criar tabelas no banco local
wrangler d1 execute gramatike --file=./schema.d1.sql --local

# Iniciar o worker em modo de desenvolvimento
wrangler dev --local
```

O modo `--local` cria um banco SQLite local em `.wrangler/state/v3/d1/miniflare-D1DatabaseObject/`.

## Troubleshooting

### Erro: "Banco de dados não disponível. Verifique a configuração do Cloudflare D1."

Este erro aparece quando:

1. **D1 não configurado no wrangler.toml**
   - Verifique se a seção `[[d1_databases]]` existe
   - Confirme que o `database_id` está correto

2. **Tabelas não criadas**
   - Execute: `wrangler d1 execute gramatike --file=./schema.d1.sql`

3. **Binding incorreto**
   - O binding deve ser `"DB"` (como configurado no `wrangler.toml`)
   - No código, acessamos via `self.env.DB`

### Erro: "Database D1 não disponível" (API)

Se a API retorna este erro, significa que:

1. O worker não consegue acessar o D1
2. Verifique os logs: `wrangler tail`

### Verificar logs do worker

```bash
# Ver logs em tempo real
wrangler tail

# Ver logs com filtro
wrangler tail --format pretty
```

### Erro: Login não funciona após criar tabelas

Se o login não funciona mesmo após criar as tabelas, provavelmente não existem usuários no banco. O sistema cria um superadmin automaticamente na primeira requisição, mas isso pode não acontecer se as tabelas foram criadas manualmente.

**Solução 1: Criar conta via cadastro**
Acesse `/cadastro` e crie uma nova conta.

**Solução 2: Inserir admin manualmente**
```bash
# No Codespace ou terminal local
npx wrangler d1 execute gramatike --remote --command="INSERT INTO user (username, email, password, nome, is_admin, is_superadmin, created_at) VALUES ('admin', 'admin@exemplo.com', 'HASH_AQUI', 'Admin', 1, 1, datetime('now'));"
```

Nota: O hash de senha deve ser gerado com o formato `salt:hash` usando PBKDF2-SHA256.

### Limpar e recriar banco de dados

Se precisar resetar o banco:

```bash
# Deletar o banco de dados
wrangler d1 delete gramatike

# Criar novamente
wrangler d1 create gramatike

# Aplicar schema
wrangler d1 execute gramatike --file=./schema.d1.sql
```

## Estrutura do Projeto

```
gramatike/
├── index.py              # Entry point do Cloudflare Worker
├── wrangler.toml         # Configuração do Worker (inclui D1)
├── schema.d1.sql         # Schema do banco de dados D1
├── gramatike_d1/         # Módulos D1 (renomeado de 'workers/' para evitar conflito)
│   ├── __init__.py      # Exports dos módulos
│   ├── db.py            # Funções de banco de dados D1
│   ├── auth.py          # Autenticação com D1
│   └── routes.py        # Handlers de rotas
```

**NOTA**: O diretório foi renomeado de `workers/` para `gramatike_d1/` para evitar
conflito com o módulo `workers` built-in do Cloudflare Workers Python, que fornece
`WorkerEntrypoint` e `Response`.

## Variáveis de Ambiente

Configure via `wrangler secret` ou no dashboard do Cloudflare:

```bash
# Configurar SECRET_KEY
wrangler secret put SECRET_KEY

# Outras variáveis (opcionais)
wrangler secret put MAIL_PASSWORD
wrangler secret put CLOUDFLARE_R2_SECRET_ACCESS_KEY
```

## Referências

- [Cloudflare D1 Documentation](https://developers.cloudflare.com/d1/)
- [Wrangler D1 Commands](https://developers.cloudflare.com/d1/platform/wrangler-commands/)
- [D1 Client API](https://developers.cloudflare.com/d1/platform/client-api/)

## FAQ

### O D1 é gratuito?

Sim, o D1 tem um tier gratuito generoso:
- 5 GB de armazenamento total
- 5 milhões de leituras/dia
- 100.000 escritas/dia

### Posso usar PostgreSQL em vez de D1?

A aplicação Gramátike suporta dois modos:

1. **D1 (SQLite)** - Para Cloudflare Workers (recomendado)
2. **PostgreSQL** - Para deploy Flask tradicional (Heroku, Railway, etc.)

O arquivo `schema.d1.sql` é para D1 (SQLite), e as migrações Alembic são para PostgreSQL.

### Como fazer backup do D1?

```bash
# Exportar dados
wrangler d1 execute gramatike --command=".dump" > backup.sql
```

### Como importar dados para D1?

```bash
# Importar de um arquivo SQL
wrangler d1 execute gramatike --file=./backup.sql
```
