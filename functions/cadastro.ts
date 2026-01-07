// Serve cadastro.html template (registration)
import { Env } from '../src/types';

export const onRequest: PagesFunction<Env> = async ({ request, env }) => {
  try {
    const response = await env.ASSETS.fetch(new URL('/templates/cadastro.html', request.url));
    
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
    console.error('[cadastro] Error:', error);
    return new Response('Erro ao carregar página', { status: 500 });
  }
};
