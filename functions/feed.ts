export const onRequestGet: PagesFunction<Env> = async ({ data, env, request }) => {
  const user = data.user;
  
  if (!user) {
    return redirectResponse('/');
  }
  
  try {
    // Método 1: Usando a URL completa da request atual
    const baseUrl = new URL(request.url);
    const feedUrl = `${baseUrl.origin}/feed.html`;
    
    // Método 2: Ou diretamente assim:
    const response = await env.ASSETS.fetch(new URL('/feed.html', request.url));
    
    return response;
  } catch (e) {
    // Fallback mínimo (mantendo seu estilo original)
    return new Response('<html><body><h1>Feed Page</h1></body></html>', {
      headers: { 'Content-Type': 'text/html' }
    });
  }
};
