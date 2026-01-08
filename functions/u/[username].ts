// User profile page (/u/:username)

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../src/types';
import { getUserByUsername } from '../../src/lib/db';
import { errorResponse } from '../../src/lib/response';

export const onRequestGet: PagesFunction<Env> = async ({ params, env }) => {
  const username = params.username as string;
  
  // Check if user exists
  const profileUser = await getUserByUsername(env.DB, username);
  if (!profileUser) {
    return errorResponse('Usuário não encontrado', 404);
  }
  
  // Serve HTML (could be same as profile.html but for public view)
  try {
    const html = await env.ASSETS.fetch(new Request('https://placeholder.local/profile.html'));
    return html;
  } catch (e) {
    return new Response('<html><body><h1>User Profile</h1></body></html>', {
      headers: { 'Content-Type': 'text/html' }
    });
  }
};
