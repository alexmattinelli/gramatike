// Serve perfil.html template
import { Env } from '../../src/types';

export const onRequest: PagesFunction<Env> = async ({ request, env, params }) => {
  try {
    // Serve o template perfil.html
    const response = await env.ASSETS.fetch(new URL('/templates/perfil.html', request.url));
    
    if (!response.ok) {
      return new Response('Página não encontrada', { status: 404 });
    }
    
    return new Response(response.body, {
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'public, max-age=300'
      }
    });
  } catch (error) {
    console.error('[perfil] Error:', error);
    return new Response('Erro ao carregar página', { status: 500 });
  }
};
