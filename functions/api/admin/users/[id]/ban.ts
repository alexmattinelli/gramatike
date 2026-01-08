// Admin Ban User API
import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env, User, Session } from '../../../../../src/types';
import { isAdmin } from '../../../../../src/lib/auth';
import { errorResponse, jsonResponse } from '../../../../../src/lib/response';
import { banUser } from '../../../../../src/lib/db';

/**
 * POST /api/admin/users/[id]/ban - Ban a user
 */
export const onRequestPost: PagesFunction<Env> = async ({ env, data, params }) => {
  const user = data.user as User;
  
  if (!user || !isAdmin(user)) {
    return errorResponse('Acesso negado', 403);
  }
  
  const userId = parseInt(params.id as string);
  
  if (isNaN(userId)) {
    return errorResponse('ID do usuário inválido', 400);
  }
  
  try {
    await banUser(env.DB, userId);
    
    return jsonResponse({
      success: true,
      message: 'Usuário banido'
    });
  } catch (error) {
    console.error('[admin/ban] Error:', error);
    return errorResponse('Erro ao banir usuário', 500);
  }
};
