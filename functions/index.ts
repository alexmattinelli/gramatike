// Serve index.html para a rota raiz
import type { PagesFunction } from '@cloudflare/workers-types';

export const onRequest: PagesFunction = async (context) => {
  try {
    // Simplesmente serve o index.html estático
    return context.env.ASSETS.fetch(context.request);
  } catch (error) {
    console.error('[index] Error serving homepage:', error);
    return new Response('Erro ao carregar página inicial', { 
      status: 500,
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
  }
};
