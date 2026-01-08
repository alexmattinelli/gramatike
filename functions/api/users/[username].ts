// GET /api/users/:username - Get user by username

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../../src/types';
import { getUserByUsername } from '../../../src/lib/db';
import { jsonResponse, errorResponse } from '../../../src/lib/response';

export const onRequestGet: PagesFunction<Env> = async ({ params, env }) => {
  try {
    const username = params.username as string;
    
    const user = await getUserByUsername(env.DB, username);
    if (!user) {
      return errorResponse('Usuário não encontrado', 404);
    }
    
    // Remove sensitive data
    const { password, email, ...publicUser } = user;
    
    return jsonResponse({ user: publicUser });
  } catch (error) {
    console.error('[users/username] Error:', error);
    return errorResponse('Erro ao buscar usuário', 500);
  }
};
