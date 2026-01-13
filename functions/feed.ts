export const onRequestGet: PagesFunction<Env> = async ({ data, env, request }) => {
  const user = data.user;
  
  if (!user) {
    return redirectResponse('/');
  }
  
  try {
    // 1. BUSCAR DADOS DO BANCO
    const postsPromise = env.DB.prepare(
      `SELECT posts.*, users.username, users.avatar_initials, users.verified
       FROM posts
       INNER JOIN users ON posts.user_id = users.id
       ORDER BY posts.created_at DESC
       LIMIT 20`
    ).all();
    
    const amigosPromise = env.DB.prepare(
      `SELECT id, username, avatar_initials, online_status
       FROM users 
       WHERE id != ?
       ORDER BY online_status DESC, username ASC
       LIMIT 10`
    ).bind(user.id).all();
    
    // Executar as queries em paralelo
    const [postsResult, amigosResult] = await Promise.all([postsPromise, amigosPromise]);
    
    // 2. BUSCAR O HTML
    const response = await env.ASSETS.fetch(new URL('/feed.html', request.url));
    let html = await response.text();
    
    // 3. INJETAR OS DADOS NO HTML (método seguro)
    // Encontrar um marcador no seu HTML ou criar um script com os dados
    const scriptComDados = `
      <script>
        window.__INITIAL_DATA__ = {
          user: ${JSON.stringify(user)},
          posts: ${JSON.stringify(postsResult.results || [])},
          amigos: ${JSON.stringify(amigosResult.results || [])}
        };
      </script>
    `;
    
    // Inserir logo após a tag <head>
    html = html.replace('</head>', scriptComDados + '</head>');
    
    return new Response(html, {
      headers: {
        'Content-Type': 'text/html',
        'Cache-Control': 'no-cache'
      }
    });
    
  } catch (e) {
    console.error('Erro no feed:', e);
    
    // Fallback: retornar HTML sem dados do banco
    const response = await env.ASSETS.fetch(new URL('/feed.html', request.url));
    return response;
  }
};
