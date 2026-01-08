// Admin Users API - List all users
import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../../src/types';
import { isAdmin } from '../../../src/lib/auth';
import { errorResponse, jsonResponse } from '../../../src/lib/response';
import { getAllUsers } from '../../../src/lib/db';

/**
 * GET /api/admin/users - Get all users
 */
export const onRequestGet: PagesFunction<Env> = async ({ env, data }) => {
  const user = data.user;
  
  if (!user || !isAdmin(user)) {
    return errorResponse('Acesso negado', 403);
  }
  
  try {
    const users = await getAllUsers(env.DB);
    
    return jsonResponse({ users });
  } catch (error) {
    console.error('[admin/users] Error:', error);
    return errorResponse('Erro ao buscar usuários', 500);
  }
};
