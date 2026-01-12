// Feed page

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../src/types';
import { redirectResponse } from '../src/lib/response';

export const onRequestGet: PagesFunction<Env> = async ({ data, env }) => {
  const user = data.user;
  
  // Require login
  if (!user) {
    return redirectResponse('/');
  }
  
  // Serve HTML from public directory via the Pages assets binding
  try {
    // Request the local asset path so Pages dev serves the current public/feed.html
    const assetReq = new Request('/feed.html');
    const html = await env.ASSETS.fetch(assetReq);
    return html;
  } catch (e) {
    return new Response('<html><body><h1>Feed Page</h1></body></html>', {
      headers: { 'Content-Type': 'text/html' }
    });
  }
};
