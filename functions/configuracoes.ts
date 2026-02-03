import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env, User } from './types';

export const onRequestGet: PagesFunction<Env> = async ({ data, env, request }) => {
  const user = data.user as User | null;
  
  if (!user) {
    return Response.redirect(new URL('/', request.url));
  }
  
  try {
    const html = await env.ASSETS.fetch(new URL('/configuracoes.html', request.url));
    return html;
  } catch (e) {
    return Response.redirect(new URL('/feed', request.url));
  }
};
