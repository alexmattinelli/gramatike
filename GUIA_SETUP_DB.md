# 🗄️ Guia de Setup do Banco de Dados D1

## ⚠️ Problema Comum

Se você está vendo este erro ao tentar executar o comando de migração:
```bash
npx wrangler d1 execute gramatike --remote --file=./db/schema.sql
```

**Não se preocupe!** Este guia vai te ajudar passo a passo.

---

## 📋 Pré-requisitos

Antes de executar qualquer comando, certifique-se de que você tem:

1. **Node.js** instalado (versão 20 ou superior)
2. **npm** funcionando
3. **Uma conta Cloudflare** (gratuita)
4. **Acesso ao projeto Gramátike** no Cloudflare Pages

---

## 🚀 Passo a Passo - Setup Completo

### Passo 1: Instalar Dependências

Primeiro, instale todas as dependências do projeto:

```bash
npm install
```

Isso vai instalar o **Wrangler** (CLI da Cloudflare) e outras dependências necessárias.

### Passo 2: Fazer Login no Wrangler

**Este é o passo mais importante!** Você precisa autenticar com sua conta Cloudflare:

```bash
npx wrangler login
```

O que vai acontecer:
1. Seu navegador vai abrir automaticamente
2. Você vai fazer login na sua conta Cloudflare
3. Vai autorizar o Wrangler a acessar sua conta
4. Depois disso, volte ao terminal

**Se o navegador não abrir automaticamente:**
```bash
npx wrangler login --browser=false
```
Isso vai te dar um link para copiar e colar no navegador.

### Passo 3: Verificar se o Login Funcionou

Teste se você está autenticado:

```bash
npx wrangler whoami
```

Você deve ver suas informações de conta. Se aparecer erro, volte ao Passo 2.

### Passo 4: Listar seus Bancos D1

Veja quais bancos D1 você tem:

```bash
npx wrangler d1 list
```

Você deve ver um banco chamado **"gramatike"** na lista. Anote o **database_id**.

**Se o banco não existir**, crie um novo:

```bash
npx wrangler d1 create gramatike
```

Anote o `database_id` que aparecer e atualize o arquivo `wrangler.toml` com esse ID.

### Passo 5: Executar o Schema no Banco

Agora sim, execute o comando para criar as tabelas:

**Opção A - Usar o script npm (RECOMENDADO):**
```bash
npm run db:init
```

**Opção B - Usar o comando direto:**
```bash
npx wrangler d1 execute gramatike --remote --file=./db/schema.sql
```

**Opção C - Usar o script bash (com confirmação de segurança):**
```bash
bash scripts/migrate-schema.sh
```

### Passo 6: Verificar se Funcionou

Liste as tabelas criadas:

```bash
npx wrangler d1 execute gramatike --remote --command "SELECT name FROM sqlite_master WHERE type='table';"
```

Você deve ver as tabelas:
- users
- posts
- sessions
- password_resets
- post_likes
- post_comments

---

## 🆘 Problemas Comuns e Soluções

### ❌ "Error: Not authenticated"

**Solução:** Execute `npx wrangler login` novamente

### ❌ "Error: No such database"

**Solução:** 
1. Execute `npx wrangler d1 list` para ver seus bancos
2. Se não existir, crie com `npx wrangler d1 create gramatike`
3. Atualize o `database_id` no arquivo `wrangler.toml`

### ❌ "Error: No such file: ./db/schema.sql"

**Solução:** Certifique-se de estar executando o comando da raiz do projeto (onde está o arquivo `package.json`)

```bash
cd /caminho/para/gramatike
npm run db:init
```

### ❌ "Error: You don't have permission"

**Solução:** 
1. Verifique se você é o dono do projeto no Cloudflare
2. Ou peça ao dono para te adicionar como colaborador
3. Faça logout e login novamente: `npx wrangler logout` e depois `npx wrangler login`

### ❌ O comando trava e não faz nada

**Solução:**
1. Pressione `Ctrl+C` para cancelar
2. Verifique sua conexão com internet
3. Tente executar: `npx wrangler d1 list` para testar a conexão
4. Se funcionar, tente o comando de schema novamente

---

## 🧪 Testando em Ambiente Local

Se você quer apenas testar localmente sem afetar a produção:

```bash
# Criar tabelas no banco local
npx wrangler d1 execute gramatike --local --file=./db/schema.sql

# Iniciar servidor de desenvolvimento
npm run dev
```

O banco local fica em `.wrangler/state/v3/d1/miniflare-D1DatabaseObject/...`

---

## 📝 Inserindo Dados de Teste

Depois de criar as tabelas, você pode inserir um usuário de teste:

```bash
npx wrangler d1 execute gramatike --remote --file=./db/insert_test_user.sql
```

Ou manualmente:

```bash
npx wrangler d1 execute gramatike --remote --command "
INSERT INTO users (username, email, password_hash, name, avatar_initials, verified, is_admin) 
VALUES ('admin', 'admin@gramatike.com.br', '\$2a\$10\$hash...', 'Administrador', 'AD', 1, 1);
"
```

---

## 🔄 Resetar o Banco (CUIDADO!)

Se você precisar resetar TUDO (vai apagar todos os dados):

```bash
npx wrangler d1 execute gramatike --remote --file=./db/schema.sql
```

Como o schema tem `DROP TABLE IF EXISTS`, ele vai:
1. Apagar todas as tabelas existentes
2. Criar tudo do zero
3. **PERDER TODOS OS DADOS**

⚠️ **NUNCA faça isso em produção se tiver dados importantes!**

---

## 💡 Dicas Úteis

### Ver todos os comandos disponíveis:
```bash
npm run
```

### Ver ajuda do Wrangler D1:
```bash
npx wrangler d1 --help
```

### Executar query SQL customizada:
```bash
npx wrangler d1 execute gramatike --remote --command "SELECT * FROM users LIMIT 5;"
```

### Exportar dados do banco:
```bash
npx wrangler d1 export gramatike --remote --output=backup.sql
```

---

## 📚 Próximos Passos

Depois de configurar o banco:

1. **Deploy no Cloudflare Pages:**
   ```bash
   npm run deploy
   ```

2. **Testar localmente:**
   ```bash
   npm run dev
   ```

3. **Verificar no dashboard:**
   - Acesse: https://dash.cloudflare.com
   - Vá em **Workers & Pages** → **D1**
   - Clique no banco **gramatike**
   - Veja suas tabelas e dados

---

## 🤝 Precisa de Ajuda?

Se nada disso funcionou:

1. Verifique o arquivo `wrangler.toml` - o `database_id` está correto?
2. Certifique-se de estar logado: `npx wrangler whoami`
3. Verifique se tem permissão no projeto Cloudflare
4. Tente fazer logout e login novamente
5. Atualize o Wrangler: `npm install wrangler@latest`

---

## ✅ Checklist Final

Marque conforme for completando:

- [ ] Node.js instalado
- [ ] `npm install` executado
- [ ] `npx wrangler login` executado com sucesso
- [ ] `npx wrangler whoami` mostra suas informações
- [ ] `npx wrangler d1 list` mostra o banco "gramatike"
- [ ] `npm run db:init` executado sem erros
- [ ] Tabelas verificadas com sucesso
- [ ] Usuário de teste criado (opcional)
- [ ] Servidor local funcionando (`npm run dev`)

**Se todos os itens estão marcados, seu banco está configurado! 🎉**
