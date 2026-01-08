// Admin Ban User API
import type { Env, User } from '../../../../../src/types';
import { isAdmin } from '../../../../../src/lib/auth';
import { errorResponse, successResponse } from '../../../../../src/lib/utils';

/**
 * POST /api/admin/users/[id]/ban - Ban or unban a user
 */
export const onRequestPost: PagesFunction<Env> = async ({ request, env, data, params }) => {
  const user = data.user as User;
  
  if (!user || !isAdmin(user)) {
    return errorResponse('Acesso negado', 403);
  }
  
  const userId = params.id as string;
  
  if (!userId) {
    return errorResponse('ID do usuário não fornecido', 400);
  }
  
  try {
    const body = await request.json() as { is_banned: boolean };
    const isBanned = body.is_banned ?? true;
    
    // Update user ban status
    await env.DB.prepare(`
      UPDATE user 
      SET is_banned = ? 
      WHERE id = ?
    `).bind(isBanned ? 1 : 0, userId).run();
    
    return successResponse({
      message: isBanned ? 'Usuário banido' : 'Usuário desbanido',
      userId,
      is_banned: isBanned
    });
  } catch (error) {
    console.error('[admin/ban] Error:', error);
    return errorResponse('Erro ao atualizar status do usuário', 500);
  }
};
