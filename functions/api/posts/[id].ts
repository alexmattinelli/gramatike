// GET /api/posts/:id - Get single post (to be implemented)
// DELETE /api/posts/:id - Delete post

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env, User } from '../../../src/types';
import { errorResponse, jsonResponse } from '../../../src/lib/response';
import { isAdmin } from '../../../src/lib/auth';

export const onRequestDelete: PagesFunction<Env> = async ({ params, env, data }) => {
  try {
    const user = data.user as User;
    if (!user) {
      return errorResponse('Não autorizado', 401);
    }
    
    const postId = parseInt(params.id as string);
    if (isNaN(postId)) {
      return errorResponse('ID inválido', 400);
    }
    
    // Get post to check ownership
    const { results } = await env.DB.prepare(
      'SELECT * FROM posts WHERE id = ?'
    ).bind(postId).all();
    
    const post = results[0] as any;
    if (!post) {
      return errorResponse('Post não encontrado', 404);
    }
    
    // Check if user owns the post or is admin
    if (post.user_id !== user.id && !isAdmin(user)) {
      return errorResponse('Sem permissão', 403);
    }
    
    // Delete post
    await env.DB.prepare('DELETE FROM posts WHERE id = ?').bind(postId).run();
    
    return jsonResponse({ success: true, message: 'Post excluído' });
  } catch (error) {
    console.error('[posts/id] DELETE Error:', error);
    return errorResponse('Erro ao excluir post', 500);
  }
};
