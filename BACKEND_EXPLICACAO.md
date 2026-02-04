# 📚 O QUE É BACKEND? - Guia Completo para Gramátike

## 🎯 Resumo Executivo

**Resposta Curta:** Backend é a parte "invisível" de um site que processa dados, conecta ao banco de dados e executa a lógica do sistema. O projeto Gramátike **JÁ TEM BACKEND** funcionando!

---

## 🤔 Frontend vs Backend - A Diferença

### 🎨 Frontend (O que você VÊ)
- **Localização:** Pasta `/public`
- **O que faz:** Interface visual que você interage
- **Tecnologias:** HTML, CSS, JavaScript
- **Exemplos:**
  - Botões que você clica
  - Formulários que você preenche
  - Animações e cores
  - Layout da página

### ⚙️ Backend (O que você NÃO VÊ)
- **Localização:** Pasta `/functions`
- **O que faz:** Processa dados, salva informações, autentica usuários
- **Tecnologias:** TypeScript, SQL, APIs
- **Exemplos:**
  - Validar login/senha
  - Salvar post no banco de dados
  - Processar curtidas
  - Enviar emails

---

## 🏗️ Backend do Gramátike - JÁ IMPLEMENTADO!

### 📁 Estrutura da Pasta `/functions`

```
functions/
├── _middleware.ts                    ← Autenticação global
│
├── api/
│   ├── auth/                        ← AUTENTICAÇÃO
│   │   ├── login.ts                 ← Fazer login
│   │   ├── register.ts              ← Criar conta
│   │   ├── logout.ts                ← Sair da conta
│   │   ├── forgot-password.ts       ← Recuperar senha
│   │   └── reset-password.ts        ← Redefinir senha
│   │
│   ├── posts/                       ← POSTS E INTERAÇÕES
│   │   ├── index.ts                 ← Listar/criar posts
│   │   ├── [id].ts                  ← Curtir/deletar post específico
│   │   ├── [id]/comments.ts         ← Comentários
│   │   └── [id]/likes.ts            ← Lista quem curtiu
│   │
│   ├── users/                       ← USUÁRIOS E PERFIS
│   │   └── [id]/...                 ← Perfil do usuário
│   │
│   └── admin/                       ← ADMINISTRAÇÃO
│       ├── stats.ts                 ← Estatísticas
│       └── users.ts                 ← Gerenciar usuários
```

---

## 🔄 Como Frontend e Backend se Comunicam?

### Exemplo Prático: Curtir um Post

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. USUÁRIO CLICA NO BOTÃO                    │
│                            ❤️ Curtir                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              2. FRONTEND (JavaScript em feed.html)              │
│   async function likePost(postId) {                             │
│     await fetch('/api/posts/123', { method: 'PATCH' });        │
│   }                                                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          3. BACKEND (functions/api/posts/[id].ts)              │
│   - Verifica se usuário está logado                            │
│   - Conecta ao banco de dados                                  │
│   - Adiciona/remove curtida                                    │
│   - Retorna sucesso ou erro                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  4. BANCO DE DADOS (PostgreSQL)                 │
│   UPDATE posts SET likes = likes + 1 WHERE id = 123            │
│   INSERT INTO post_likes (user_id, post_id) VALUES (...)       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              5. FRONTEND RECEBE RESPOSTA                        │
│   - Mostra coração vermelho ❤️                                 │
│   - Atualiza contador de curtidas                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 Tecnologias Backend do Gramátike

### 🔧 Cloudflare Pages Functions

**O que é?**
- Sistema serverless (sem servidor dedicado)
- Executa código TypeScript na nuvem
- Gratuito até certo limite
- Deploy automático

**Como funciona?**
```typescript
// functions/api/posts/[id].ts
export async function onRequestPATCH(context) {
  // Este código roda no servidor Cloudflare!
  const postId = context.params.id;
  const user = await authenticateUser(context);
  
  // Atualizar banco de dados
  await db.execute(
    'UPDATE posts SET likes = likes + 1 WHERE id = ?',
    [postId]
  );
  
  return new Response(JSON.stringify({ success: true }));
}
```

### 🗄️ Banco de Dados

**Opções no Projeto:**
1. **PostgreSQL** (Produção - Neon)
   - Banco de dados SQL robusto
   - Usado no deploy real

2. **SQLite** (Desenvolvimento)
   - Banco de dados local
   - Para testes

**Tabelas Principais:**
- `users` - Usuários do sistema
- `posts` - Posts/publicações
- `post_likes` - Curtidas
- `comments` - Comentários
- `user_follows` - Seguidores

### 📦 Armazenamento de Arquivos

**Cloudflare R2:**
- Armazena avatares de usuários
- Armazena imagens de posts
- Armazena PDFs e documentos

---

## 🚀 Fluxos Backend Implementados

### 1️⃣ Autenticação (Login/Registro)

**Arquivo:** `functions/api/auth/login.ts`

```typescript
// Simplificado
export async function onRequestPost(context) {
  const { email, password } = await context.request.json();
  
  // 1. Buscar usuário no banco
  const user = await db.query(
    'SELECT * FROM users WHERE email = ?',
    [email]
  );
  
  // 2. Verificar senha
  const valid = await bcrypt.compare(password, user.password_hash);
  
  // 3. Criar sessão
  if (valid) {
    const session = await createSession(user.id);
    return Response.json({ success: true, session });
  }
  
  return Response.json({ error: 'Login inválido' }, { status: 401 });
}
```

### 2️⃣ Criar Post

**Arquivo:** `functions/api/posts/index.ts`

```typescript
export async function onRequestPOST(context) {
  // 1. Verificar autenticação
  const user = await getAuthenticatedUser(context);
  
  // 2. Validar conteúdo
  const { content } = await context.request.json();
  if (!content || content.length > 500) {
    return Response.json({ error: 'Conteúdo inválido' }, { status: 400 });
  }
  
  // 3. Salvar no banco
  const post = await db.execute(
    'INSERT INTO posts (user_id, content) VALUES (?, ?)',
    [user.id, content]
  );
  
  return Response.json({ success: true, post });
}
```

### 3️⃣ Curtir Post

**Arquivo:** `functions/api/posts/[id].ts`

```typescript
export async function onRequestPATCH(context) {
  const user = await getAuthenticatedUser(context);
  const postId = context.params.id;
  
  // Verificar se já curtiu
  const existingLike = await db.query(
    'SELECT * FROM post_likes WHERE user_id = ? AND post_id = ?',
    [user.id, postId]
  );
  
  if (existingLike) {
    // Descurtir
    await db.execute(
      'DELETE FROM post_likes WHERE user_id = ? AND post_id = ?',
      [user.id, postId]
    );
    return Response.json({ liked: false });
  } else {
    // Curtir
    await db.execute(
      'INSERT INTO post_likes (user_id, post_id) VALUES (?, ?)',
      [user.id, postId]
    );
    return Response.json({ liked: true });
  }
}
```

---

## 🔐 Segurança no Backend

### 1. Autenticação de Sessão

```typescript
// _middleware.ts
export async function onRequest(context) {
  const sessionCookie = context.request.headers.get('Cookie');
  
  if (!sessionCookie) {
    return Response.json({ error: 'Não autenticado' }, { status: 401 });
  }
  
  const user = await validateSession(sessionCookie);
  context.data.user = user;
  
  return context.next();
}
```

### 2. Validação de Dados

```typescript
// Validar antes de salvar
function validatePostContent(content: string): boolean {
  if (!content || typeof content !== 'string') return false;
  if (content.length < 1 || content.length > 500) return false;
  if (content.includes('<script>')) return false; // Prevenir XSS
  return true;
}
```

### 3. Rate Limiting

```typescript
// Limitar requisições por usuário
const rateLimiter = new Map();

function checkRateLimit(userId: string): boolean {
  const now = Date.now();
  const userRequests = rateLimiter.get(userId) || [];
  
  // Permitir 10 requisições por minuto
  const recentRequests = userRequests.filter(
    time => now - time < 60000
  );
  
  if (recentRequests.length >= 10) {
    return false; // Bloqueado
  }
  
  recentRequests.push(now);
  rateLimiter.set(userId, recentRequests);
  return true;
}
```

---

## 📊 Banco de Dados - Schema

### Tabela `users`
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(100),
  avatar_url VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabela `posts`
```sql
CREATE TABLE posts (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  content TEXT NOT NULL,
  likes_count INTEGER DEFAULT 0,
  comments_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Tabela `post_likes`
```sql
CREATE TABLE post_likes (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  post_id INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (post_id) REFERENCES posts(id),
  UNIQUE(user_id, post_id)
);
```

---

## 🌐 API Endpoints - Resumo

### Autenticação
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/login` | Fazer login |
| POST | `/api/auth/register` | Criar conta |
| POST | `/api/auth/logout` | Sair |
| POST | `/api/auth/forgot-password` | Recuperar senha |
| POST | `/api/auth/reset-password` | Redefinir senha |

### Posts
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/posts` | Listar posts |
| POST | `/api/posts` | Criar post |
| PATCH | `/api/posts/[id]` | Curtir/descurtir |
| DELETE | `/api/posts/[id]` | Deletar post |
| GET | `/api/posts/[id]/likes` | Ver quem curtiu |
| POST | `/api/posts/[id]/comments` | Comentar |

### Admin
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/admin/stats` | Estatísticas |
| GET | `/api/admin/users` | Listar usuários |
| POST | `/api/admin/users/[id]/ban` | Banir usuário |

---

## 🚀 Como Adicionar Novo Backend?

### Exemplo: Sistema de Seguir

**1. Criar tabela no banco de dados:**
```sql
-- db/schema.sql
CREATE TABLE user_follows (
  id INTEGER PRIMARY KEY,
  follower_id INTEGER NOT NULL,
  following_id INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (follower_id) REFERENCES users(id),
  FOREIGN KEY (following_id) REFERENCES users(id),
  UNIQUE(follower_id, following_id)
);
```

**2. Criar endpoint backend:**
```typescript
// functions/api/users/[id]/follow.ts
export async function onRequestPOST(context) {
  const currentUser = await getAuthenticatedUser(context);
  const userToFollow = context.params.id;
  
  await db.execute(
    'INSERT INTO user_follows (follower_id, following_id) VALUES (?, ?)',
    [currentUser.id, userToFollow]
  );
  
  return Response.json({ success: true });
}

export async function onRequestDELETE(context) {
  const currentUser = await getAuthenticatedUser(context);
  const userToUnfollow = context.params.id;
  
  await db.execute(
    'DELETE FROM user_follows WHERE follower_id = ? AND following_id = ?',
    [currentUser.id, userToUnfollow]
  );
  
  return Response.json({ success: true });
}
```

**3. Usar no frontend:**
```javascript
// public/perfil.html
async function followUser(userId) {
  const response = await fetch(`/api/users/${userId}/follow`, {
    method: 'POST'
  });
  
  if (response.ok) {
    showToast('Seguindo!');
  }
}

async function unfollowUser(userId) {
  const response = await fetch(`/api/users/${userId}/follow`, {
    method: 'DELETE'
  });
  
  if (response.ok) {
    showToast('Deixou de seguir');
  }
}
```

---

## 📖 Recursos para Aprender Mais

### Backend em Geral
- [MDN - O que é um servidor web?](https://developer.mozilla.org/pt-BR/docs/Learn/Common_questions/What_is_a_web_server)
- [Curso de Backend - Rocketseat](https://www.rocketseat.com.br/)
- [FreeCodeCamp - Backend](https://www.freecodecamp.org/learn/back-end-development-and-apis/)

### Cloudflare Pages Functions
- [Documentação Oficial](https://developers.cloudflare.com/pages/functions/)
- [Guia de Início Rápido](https://developers.cloudflare.com/pages/functions/get-started/)
- [Exemplos de Código](https://developers.cloudflare.com/pages/functions/examples/)

### TypeScript
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [TypeScript para Iniciantes](https://www.typescriptlang.org/docs/handbook/typescript-from-scratch.html)

### SQL e Banco de Dados
- [SQL Tutorial - W3Schools](https://www.w3schools.com/sql/)
- [PostgreSQL Tutorial](https://www.postgresql.org/docs/current/tutorial.html)

---

## ✅ Conclusão

### Resumo:

1. ✅ **Backend JÁ EXISTE** no projeto Gramátike
2. ✅ **Localização:** Pasta `/functions`
3. ✅ **Tecnologia:** Cloudflare Pages Functions + TypeScript
4. ✅ **Funcionalidades:** Login, posts, curtidas, comentários, admin
5. ✅ **Banco de Dados:** PostgreSQL/SQLite
6. ✅ **Pronto para usar:** Só fazer deploy!

### O Gramátike é uma aplicação **FULL-STACK** completa!

**Frontend:** HTML + CSS + JavaScript (pasta `/public`)  
**Backend:** TypeScript + API (pasta `/functions`)  
**Banco de Dados:** PostgreSQL/SQLite (pasta `/db`)

---

**Dúvidas? O backend já está funcionando! 🚀**
