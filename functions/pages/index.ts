// Feed page handler
import { getPosts, getDivulgacoes } from '../../src/lib/db';
import { getCurrentUser } from '../../src/lib/auth';
import { renderFeed } from '../../src/templates/pages/feed';
import type { Env } from '../../src/types';

/**
 * Render the feed page with posts and announcements
 */
export const onRequestGet: PagesFunction<Env> = async ({ env, request }) => {
  try {
    // Get current user (optional for feed viewing)
    const user = await getCurrentUser(request, env.DB);
    
    // Get posts with pagination
    const posts = await getPosts(env.DB, 1, 20, user?.id);
    
    // Get announcements/news for the feed
    const divulgacoes = await getDivulgacoes(env.DB, 5);
    
    // Render the HTML
    const html = renderFeed({ user, posts, divulgacoes });
    
    return new Response(html, {
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
      },
    });
  } catch (error) {
    console.error('[Feed page] Error:', error);
    return new Response('Erro ao carregar o feed', { status: 500 });
  }
};
