// POST /api/auth/logout - User logout

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../../src/types';
import { deleteSession } from '../../../src/lib/db';
import { jsonResponse, errorResponse } from '../../../src/lib/response';
import { deleteSessionCookie } from '../../../src/lib/auth';

export const onRequestPost: PagesFunction<Env> = async ({ request, env, data }) => {
  try {
    const session = data.session;
    
    if (session) {
      await deleteSession(env.DB, session.token);
    }
    
    return new Response(JSON.stringify({
      success: true,
      message: 'Logout realizado com sucesso'
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Set-Cookie': deleteSessionCookie()
      }
    });
  } catch (error) {
    console.error('[logout] Error:', error);
    return errorResponse('Erro ao fazer logout', 500);
  }
};
