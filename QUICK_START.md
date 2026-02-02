# 🚀 Gramátike - Guia de Início Rápido

Este guia mostra como configurar e executar o projeto Gramátike do zero.

## ✅ Problemas Corrigidos

O projeto tinha os seguintes problemas que foram corrigidos:

1. **Erros de sintaxe TypeScript** - Declarações de export duplicadas/incompletas em `feed.ts` e `register.ts`
2. **Schema do banco de dados incompleto** - Faltavam colunas necessárias
3. **Problemas de autenticação** - Erros nos campos do banco e criação de sessão
4. **Banco de dados não inicializado** - Tabelas não criadas

## 📋 Pré-requisitos

- Node.js 20+ instalado
- npm (vem com Node.js)

## 🏃 Início Rápido (Desenvolvimento Local)

### 1. Instalar Dependências

```bash
npm install
```

### 2. Inicializar Banco de Dados Local

```bash
npx wrangler d1 execute gramatike --local --file=./db/schema.sql
```

Você deve ver: `🚣 10 commands executed successfully.`

### 3. Iniciar Servidor de Desenvolvimento

```bash
npm run dev
```

O servidor estará disponível em: **http://localhost:8788**

### 4. Testar a Aplicação

1. Abra http://localhost:8788 no navegador
2. Você verá a página de Login/Cadastro
3. Crie uma conta usando o formulário de cadastro
4. Faça login com suas credenciais
5. Você será redirecionado para o feed

## 🧪 Testar via API (curl)

### Criar Usuário

```bash
curl -X POST http://localhost:8788/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"teste","email":"teste@example.com","password":"123456","name":"Usuário Teste"}'
```

### Fazer Login

```bash
curl -X POST http://localhost:8788/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@example.com","password":"123456"}'
```

## 🗄️ Estrutura do Banco de Dados

O schema inclui as seguintes tabelas:

### `users`
- `id` - ID único do usuário
- `username` - Nome de usuário (único)
- `email` - Email (único)
- `password_hash` - Senha (em produção deve ser hash)
- `name` - Nome completo
- `avatar_initials` - Iniciais para avatar
- `verified` - Status de verificação
- `online_status` - Status online
- `role` - Papel (user/admin/moderator)
- `is_admin` - Flag admin
- `is_banned` - Flag banido
- `created_at` - Data de criação

### `posts`
- `id` - ID único do post
- `user_id` - ID do usuário autor
- `content` - Conteúdo do post
- `likes` - Número de curtidas
- `comments` - Número de comentários
- `created_at` - Data de criação

### `sessions`
- `id` - ID único da sessão
- `user_id` - ID do usuário
- `token` - Token de sessão (UUID)
- `expires_at` - Data de expiração
- `created_at` - Data de criação

## 🔧 Comandos Úteis

### Resetar Banco de Dados Local

```bash
npx wrangler d1 execute gramatike --local --file=./db/schema.sql
```

### Ver Tabelas Criadas

```bash
npx wrangler d1 execute gramatike --local --command="SELECT name FROM sqlite_master WHERE type='table';"
```

### Ver Usuários Cadastrados

```bash
npx wrangler d1 execute gramatike --local --command="SELECT id, username, email, name FROM users;"
```

### Verificar Tipos TypeScript

```bash
npm run typecheck
```

## 🚀 Deploy para Produção (Cloudflare Pages)

Para fazer deploy em produção, siga o guia completo em [SETUP.md](./SETUP.md).

**Resumo:**

1. Configure o D1 remoto:
   ```bash
   npx wrangler d1 execute gramatike --remote --file=./db/schema.sql
   ```

2. O deploy é automático via integração do Cloudflare Pages com GitHub
   - Push para branch `main`
   - Cloudflare Pages detecta automaticamente e faz o deploy

## ⚠️ Notas Importantes

### Segurança

⚠️ **AVISO CRÍTICO DE SEGURANÇA**: O código atual **NÃO faz hash de senhas**. As senhas são armazenadas em texto puro no banco de dados. Isso é **APENAS para desenvolvimento/demonstração**.

**ANTES de usar em produção, você DEVE**:

1. ❌ **NUNCA** use este código em produção sem implementar hash de senhas
2. ✅ Implemente hash de senhas com bcrypt ou Argon2
3. ✅ Configure variáveis de ambiente (`SECRET_KEY`)
4. ✅ Use HTTPS em produção
5. ✅ Configure CORS adequadamente
6. ✅ Adicione validação de email
7. ✅ Implemente rate limiting para login

**Exemplo de implementação segura**:
```typescript
import bcrypt from 'bcrypt';

// No registro
const hashedPassword = await bcrypt.hash(password, 10);

// No login
const isValid = await bcrypt.compare(password, user.password_hash);
```

### Banco de Dados

- **Local**: Usa `.wrangler/state/v3/d1/` (SQLite)
- **Remoto**: Usa Cloudflare D1 (configurar via Cloudflare Dashboard)

### Arquivos Importantes

- `functions/` - TypeScript Pages Functions (rotas e APIs)
- `public/` - Arquivos estáticos (HTML, CSS, imagens)
- `db/schema.sql` - Schema do banco de dados
- `wrangler.toml` - Configuração do Cloudflare
- `package.json` - Dependências e scripts

## 🐛 Troubleshooting

### Erro: "Tabelas não encontradas"

Execute o comando de inicialização do banco:
```bash
npx wrangler d1 execute gramatike --local --file=./db/schema.sql
```

### Erro: "Worker compilation failed"

Verifique se há erros de sintaxe TypeScript. Execute:
```bash
npm run typecheck
```

### Erro ao fazer login/cadastro

1. Verifique se o banco foi inicializado
2. Verifique os logs do servidor (terminal onde rodou `npm run dev`)
3. Tente resetar o banco e criar novo usuário

### Porta 8788 já em uso

Mate processos do wrangler:
```bash
ps aux | grep wrangler
kill <PID>
```

## 📚 Documentação Adicional

- [README.md](./README.md) - Visão geral do projeto
- [SETUP.md](./SETUP.md) - Guia de configuração completo
- [Cloudflare D1 Docs](https://developers.cloudflare.com/d1/)
- [Cloudflare Pages Functions](https://developers.cloudflare.com/pages/platform/functions/)

## ✅ Checklist de Verificação

Depois de seguir este guia, você deve ter:

- [x] Dependências instaladas (`npm install`)
- [x] Banco de dados inicializado (10 comandos executados)
- [x] Servidor de desenvolvimento rodando (http://localhost:8788)
- [x] Consegue criar usuário via API ou interface
- [x] Consegue fazer login
- [x] Feed carrega corretamente após login

## 💡 Próximos Passos

1. ✅ Explore a interface do usuário
2. ✅ Crie posts no feed
3. ✅ Teste as funcionalidades de admin (se tiver conta admin)
4. 🔒 Implemente hash de senhas (bcrypt)
5. 🚀 Configure para deploy em produção
6. 📧 Configure email (Brevo) para verificação

---

**Projeto corrigido e funcional!** 🎉
