// Admin dashboard page

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env, User } from '../types';
import { isAdmin } from '../src/lib/auth';
import { redirectResponse, errorResponse } from '../src/lib/response';

export const onRequestGet: PagesFunction<Env> = async ({ data, env }) => {
  const user = data.user as User | null;
  
  // Require login
  if (!user) {
    return redirectResponse('/');
  }
  
  // Require admin
  if (!isAdmin(user)) {
    return redirectResponse('/feed');
  }
  
  // Serve HTML from public directory
  try {
    const html = await env.ASSETS.fetch(new Request('https://placeholder.local/admin.html'));
    return html;
  } catch (e) {
    return new Response('<html><body><h1>Admin Dashboard</h1></body></html>', {
      headers: { 'Content-Type': 'text/html' }
    });
  }
};
