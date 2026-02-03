import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env, User } from './types';

export const onRequestGet: PagesFunction<Env> = async ({ data, env, request }) => {
  // Verificar se usuário está autenticado
  if (!data.user) {
    // Redirecionar para login se não estiver autenticado
    return Response.redirect(new URL('/', request.url));
  }
  
  const user = data.user;
  
  try {
    // 1. BUSCAR POSTS DO BANCO
    const postsResult = await env.DB.prepare(`
      SELECT 
        posts.id,
        posts.content,
        posts.likes,
        posts.comments,
        posts.created_at,
        users.username,
        users.avatar_initials,
        users.verified,
        users.name as user_name
      FROM posts
      INNER JOIN users ON posts.user_id = users.id
      ORDER BY posts.created_at DESC
      LIMIT 20
    `).all();
    
    const posts = postsResult.results || [];
    
    // 2. BUSCAR AMIGOS/SUGESTÕES
    const amigosResult = await env.DB.prepare(`
      SELECT 
        id,
        username,
        avatar_initials,
        online_status,
        verified
      FROM users 
      WHERE id != ?
      ORDER BY online_status DESC, username ASC
      LIMIT 10
    `).bind(user.id).all();
    
    const amigos = amigosResult.results || [];
    
    // 3. CARREGAR HTML
    const response = await env.ASSETS.fetch(new URL('/feed.html', request.url));
    let html = await response.text();
    
    // 4. INJETAR DADOS NO HTML
    const dadosScript = `
      <script>
        // Dados do servidor
        window.APP_DATA = ${JSON.stringify({
          user: {
            id: user.id,
            username: user.username,
            name: user.name || user.username,
            initials: user.avatar_initials || user.username?.charAt(0).toUpperCase() || 'U',
            verified: user.verified || false,
            online: user.online_status || true
          },
          posts: posts,
          amigos: amigos,
          timestamp: new Date().toISOString()
        })};
        
        // API Helper
        window.GramatikeAPI = {
          async post(content) {
            const res = await fetch('/api/posts', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ content })
            });
            return res.json();
          },
          
          async like(postId) {
            const res = await fetch(\`/api/posts/\${postId}/like\`, {
              method: 'PATCH'
            });
            return res.json();
          },
          
          async deletePost(postId) {
            const res = await fetch(\`/api/posts/\${postId}\`, {
              method: 'DELETE'
            });
            return res.json();
          }
        };
      </script>
    `;
    
    // Inserir antes do </body> ou </head>
    if (html.includes('</head>')) {
      html = html.replace('</head>', dadosScript + '</head>');
    } else {
      html = html.replace('</body>', dadosScript + '</body>');
    }
    
    return new Response(html, {
      headers: {
        'Content-Type': 'text/html',
        'Cache-Control': 'no-cache, no-store, must-revalidate'
      }
    });
    
  } catch (error) {
    console.error('Erro no feed.ts:', error);
    
    // Fallback: HTML básico com mensagem de erro
    return new Response(`
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>Gramátike - Erro</title>
        <style>
          body {
            font-family: 'Inter', sans-serif;
            background: #f6f5fa;
            color: #32264c;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
          }
          .error-container {
            background: white;
            padding: 40px;
            border-radius: 18px;
            box-shadow: 0 4px 20px rgba(155, 93, 229, 0.15);
            max-width: 500px;
            text-align: center;
          }
          h1 {
            color: #9B5DE5;
            margin-bottom: 20px;
          }
          .btn {
            background: #9B5DE5;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 14px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 20px;
            text-decoration: none;
            display: inline-block;
          }
        </style>
      </head>
      <body>
        <div class="error-container">
          <h1>😕 Oops!</h1>
          <p>Ocorreu um erro ao carregar o feed.</p>
          <p>Tente recarregar a página ou volte mais tarde.</p>
          <a href="/" class="btn">Voltar para início</a>
        </div>
      </body>
      </html>
    `, {
      headers: { 'Content-Type': 'text/html' }
    });
  }
};
