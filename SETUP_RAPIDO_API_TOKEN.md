# 🔐 Setup Rápido com API Token Cloudflare

## ⚡ Solução Rápida - Use Isto!

Você tem uma API Token da Cloudflare e quer configurar o banco D1 rapidamente. Siga estes passos:

---

## 🚀 Método 1: Script Automatizado (RECOMENDADO)

Execute este comando no terminal (na raiz do projeto):

```bash
bash scripts/setup-com-api-token.sh
```

O script vai:
1. ✅ Autenticar usando o token
2. ✅ Listar seus bancos D1
3. ✅ Aplicar o schema no banco "gramatike"
4. ✅ Verificar as tabelas criadas

---

## 🔧 Método 2: Comandos Manuais

Se preferir executar manualmente:

### Passo 1: Exportar o Token

```bash
export CLOUDFLARE_API_TOKEN="CZ_tsTFT-M3-p9aeGyYk136ro4-bu3zMvFw5AiUx"
```

### Passo 2: Verificar Autenticação

```bash
npx wrangler whoami
```

Deve mostrar suas informações de conta.

### Passo 3: Listar Bancos D1

```bash
npx wrangler d1 list
```

Confirme que existe um banco chamado "gramatike".

### Passo 4: Aplicar o Schema

```bash
npx wrangler d1 execute gramatike --remote --file=./db/schema.sql
```

### Passo 5: Verificar Tabelas

```bash
npx wrangler d1 execute gramatike --remote --command "SELECT name FROM sqlite_master WHERE type='table';"
```

Deve listar:
- users
- posts
- sessions
- password_resets
- post_likes
- post_comments

---

## 📦 Método 3: Usando npm Script

O projeto já tem um comando npm configurado:

```bash
export CLOUDFLARE_API_TOKEN="CZ_tsTFT-M3-p9aeGyYk136ro4-bu3zMvFw5AiUx"
npm run db:init
```

---

## ⚠️ IMPORTANTE - Segurança

### ✅ O QUE FAZER:

1. **Use variável de ambiente temporária:**
   ```bash
   export CLOUDFLARE_API_TOKEN="sua-chave-aqui"
   ```
   Ela dura apenas enquanto o terminal estiver aberto.

2. **OU crie um arquivo .env (NÃO commitar!):**
   ```bash
   echo "CLOUDFLARE_API_TOKEN=CZ_tsTFT-M3-p9aeGyYk136ro4-bu3zMvFw5AiUx" > .env
   ```
   O `.gitignore` já está configurado para ignorar arquivos `.env`.

3. **Após usar, limpe o token:**
   ```bash
   unset CLOUDFLARE_API_TOKEN
   ```

### ❌ NUNCA FAÇA:

1. ❌ NÃO commite o token no Git
2. ❌ NÃO compartilhe o token publicamente
3. ❌ NÃO coloque o token em código-fonte
4. ❌ NÃO deixe o token em histórico de comandos públicos

### 🔒 Depois de Usar:

Se você acabou de usar e não precisa mais:

```bash
# Limpar a variável de ambiente
unset CLOUDFLARE_API_TOKEN

# OU deletar o arquivo .env
rm .env
```

### 🔄 Regenerar Token (Recomendado):

Depois de configurar tudo, é recomendado:

1. Acesse: https://dash.cloudflare.com/profile/api-tokens
2. Revogue este token
3. Crie um novo se precisar no futuro

---

## 🎯 Guia Passo a Passo Completo

### Cenário: Primeira Vez Configurando

```bash
# 1. Navegue até o diretório do projeto
cd /caminho/para/gramatike

# 2. Instale as dependências (se ainda não fez)
npm install

# 3. Configure o token temporariamente
export CLOUDFLARE_API_TOKEN="CZ_tsTFT-M3-p9aeGyYk136ro4-bu3zMvFw5AiUx"

# 4. Execute o script de setup
bash scripts/setup-com-api-token.sh

# 5. Limpe o token quando terminar
unset CLOUDFLARE_API_TOKEN
```

### Cenário: Já Configurou Antes, Quer Resetar

```bash
export CLOUDFLARE_API_TOKEN="CZ_tsTFT-M3-p9aeGyYk136ro4-bu3zMvFw5AiUx"
npx wrangler d1 execute gramatike --remote --file=./db/schema.sql
unset CLOUDFLARE_API_TOKEN
```

---

## ✅ Como Saber se Funcionou?

Após executar os comandos, você deve ver:

```
✅ Schema aplicado com sucesso!

🔍 Verificando tabelas criadas...
┌──────────────────┐
│ name             │
├──────────────────┤
│ password_resets  │
│ post_comments    │
│ post_likes       │
│ posts            │
│ sessions         │
│ users            │
└──────────────────┘
```

---

## 🆘 Problemas?

### "Error: Authentication error"

**Solução:**
```bash
# Verifique se o token está correto
echo $CLOUDFLARE_API_TOKEN

# Se estiver vazio, exporte novamente
export CLOUDFLARE_API_TOKEN="CZ_tsTFT-M3-p9aeGyYk136ro4-bu3zMvFw5AiUx"
```

### "Error: Database not found"

**Solução:**
```bash
# Liste os bancos disponíveis
npx wrangler d1 list

# Se não existir, crie
npx wrangler d1 create gramatike

# Atualize o database_id no wrangler.toml
```

### "Command not found: npx"

**Solução:**
```bash
# Instale as dependências
npm install

# Ou use o npm diretamente
npm exec wrangler d1 execute gramatike --remote --file=./db/schema.sql
```

---

## 🎉 Pronto!

Depois de configurar o banco, você pode:

1. **Testar localmente:**
   ```bash
   npm run dev
   ```

2. **Fazer deploy:**
   ```bash
   npm run deploy
   ```

3. **Ver os dados no dashboard:**
   - https://dash.cloudflare.com
   - Workers & Pages → D1 → gramatike

---

## 📚 Documentação Adicional

Para mais detalhes, consulte:
- `GUIA_SETUP_DB.md` - Guia completo passo a passo
- `README.md` - Documentação geral do projeto
- `SETUP.md` - Instruções de deploy

---

**🔒 LEMBRE-SE:** Depois de usar, revogue este token e crie um novo se necessário!
