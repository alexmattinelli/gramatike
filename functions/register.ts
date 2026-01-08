// Register page

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../src/types';
import { redirectResponse } from '../src/lib/response';

export const onRequestGet: PagesFunction<Env> = async ({ data, env }) => {
  const user = data.user;
  
  // If already logged in, redirect to feed
  if (user) {
    return redirectResponse('/feed');
  }
  
  // Serve HTML from public directory
  try {
    const html = await env.ASSETS.fetch(new Request('https://placeholder.local/register.html'));
    return html;
  } catch (e) {
    return new Response('<html><body><h1>Register Page</h1></body></html>', {
      headers: { 'Content-Type': 'text/html' }
    });
  }
};
