// My profile page

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../src/types';
import { redirectResponse } from '../src/lib/response';

export const onRequestGet: PagesFunction<Env> = async ({ data, env }) => {
  const user = data.user;
  
  // Require login
  if (!user) {
    return redirectResponse('/login');
  }
  
  // Serve HTML from public directory
  try {
    const html = await env.ASSETS.fetch(new Request('https://placeholder.local/profile.html'));
    return html;
  } catch (e) {
    return new Response('<html><body><h1>Profile Page</h1></body></html>', {
      headers: { 'Content-Type': 'text/html' }
    });
  }
};
