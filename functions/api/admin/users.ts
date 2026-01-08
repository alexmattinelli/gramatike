// Admin Users API
import type { Env, User } from '../../../src/types';
import { isAdmin } from '../../../src/lib/auth';
import { errorResponse, successResponse } from '../../../src/lib/utils';

/**
 * GET /api/admin/users - Get users list with pagination
 */
export const onRequestGet: PagesFunction<Env> = async ({ request, env, data }) => {
  const user = data.user as User;
  
  if (!user || !isAdmin(user)) {
    return errorResponse('Acesso negado', 403);
  }
  
  const url = new URL(request.url);
  const page = parseInt(url.searchParams.get('page') || '1');
  const perPage = 20;
  const offset = (page - 1) * perPage;
  
  try {
    // Get users with pagination
    const users = await env.DB.prepare(`
      SELECT 
        id, 
        username, 
        email, 
        nome,
        foto_perfil,
        created_at, 
        is_admin, 
        is_superadmin,
        is_banned,
        verified
      FROM user 
      ORDER BY created_at DESC 
      LIMIT ? OFFSET ?
    `).bind(perPage, offset).all();
    
    return successResponse({
      users: users.results || [],
      page,
      perPage
    });
  } catch (error) {
    console.error('[admin/users] Error:', error);
    return errorResponse('Erro ao buscar usuários', 500);
  }
};

/**
 * PATCH /api/admin/users/:id - Update user (not used, see ban endpoint below)
 */
export const onRequestPatch: PagesFunction<Env> = async ({ request, env, data }) => {
  const user = data.user as User;
  
  if (!user || !isAdmin(user)) {
    return errorResponse('Acesso negado', 403);
  }
  
  // This endpoint can be used for future user updates
  return errorResponse('Not implemented', 501);
};
