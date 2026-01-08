// Login page

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../src/types';
import { htmlResponse, redirectResponse } from '../src/lib/response';

export const onRequestGet: PagesFunction<Env> = async ({ data, env }) => {
  const user = data.user;
  
  // If already logged in, redirect to feed
  if (user) {
    return redirectResponse('/feed');
  }
  
  // Read HTML file from public directory
  try {
    const html = await env.ASSETS.fetch(new Request('https://placeholder.local/login.html'));
    return html;
  } catch (e) {
    // Fallback if ASSETS is not available
    return htmlResponse('<html><body><h1>Login Page</h1><p>ASSETS binding not configured</p></body></html>', 500);
  }
};
