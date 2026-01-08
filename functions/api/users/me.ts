// GET /api/users/me - Get current user

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../../src/types';
import { jsonResponse, errorResponse } from '../../../src/lib/response';

export const onRequestGet: PagesFunction<Env> = async ({ data }) => {
  try {
    const user = data.user;
    if (!user) {
      return errorResponse('Não autorizado', 401);
    }
    
    // Remove password from response
    const { password, ...userWithoutPassword } = user;
    
    return jsonResponse({ user: userWithoutPassword });
  } catch (error) {
    console.error('[users/me] GET Error:', error);
    return errorResponse('Erro ao buscar usuário', 500);
  }
};
