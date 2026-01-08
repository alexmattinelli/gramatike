// DELETE /api/admin/posts/:id - Delete any post (admin)

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../../../src/types';
import { isAdmin } from '../../../../src/lib/auth';
import { jsonResponse, errorResponse } from '../../../../src/lib/response';

export const onRequestDelete: PagesFunction<Env> = async ({ params, env, data }) => {
  try {
    const user = data.user;
    if (!user || !isAdmin(user)) {
      return errorResponse('Sem permissão', 403);
    }
    
    const postId = parseInt(params.id as string);
    if (isNaN(postId)) {
      return errorResponse('ID inválido', 400);
    }
    
    // Delete post
    await env.DB.prepare('DELETE FROM posts WHERE id = ?').bind(postId).run();
    
    return jsonResponse({
      success: true,
      message: 'Post excluído'
    });
  } catch (error) {
    console.error('[admin/posts/id] Error:', error);
    return errorResponse('Erro ao excluir post', 500);
  }
};
