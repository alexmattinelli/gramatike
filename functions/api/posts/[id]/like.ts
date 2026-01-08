// POST /api/posts/:id/like - Toggle like

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../../../src/types';
import { toggleLike } from '../../../../src/lib/db';
import { jsonResponse, errorResponse } from '../../../../src/lib/response';

export const onRequestPost: PagesFunction<Env> = async ({ params, env, data }) => {
  try {
    const user = data.user;
    if (!user) {
      return errorResponse('Não autorizado', 401);
    }
    
    const postId = parseInt(params.id as string);
    if (isNaN(postId)) {
      return errorResponse('ID inválido', 400);
    }
    
    const liked = await toggleLike(env.DB, user.id, postId);
    
    return jsonResponse({
      success: true,
      liked,
      message: liked ? 'Post curtido' : 'Curtida removida'
    });
  } catch (error) {
    console.error('[posts/like] Error:', error);
    return errorResponse('Erro ao curtir post', 500);
  }
};
