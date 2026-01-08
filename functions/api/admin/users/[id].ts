// PATCH /api/admin/users/:id - Ban/unban user

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../../../src/types';
import { isAdmin } from '../../../../src/lib/auth';
import { jsonResponse, errorResponse } from '../../../../src/lib/response';

export const onRequestPatch: PagesFunction<Env> = async ({ params, request, env, data }) => {
  try {
    const user = data.user;
    if (!user || !isAdmin(user)) {
      return errorResponse('Sem permissão', 403);
    }
    
    const userId = parseInt(params.id as string);
    if (isNaN(userId)) {
      return errorResponse('ID inválido', 400);
    }
    
    const { is_banned } = await request.json();
    
    if (typeof is_banned !== 'number' || (is_banned !== 0 && is_banned !== 1)) {
      return errorResponse('Valor inválido para is_banned', 400);
    }
    
    // Update user
    await env.DB.prepare(
      'UPDATE users SET is_banned = ? WHERE id = ?'
    ).bind(is_banned, userId).run();
    
    return jsonResponse({
      success: true,
      message: is_banned ? 'Usuário banido' : 'Usuário desbanido'
    });
  } catch (error) {
    console.error('[admin/users/id] Error:', error);
    return errorResponse('Erro ao atualizar usuário', 500);
  }
};
