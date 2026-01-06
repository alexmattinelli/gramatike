// Post Like API
import type { Env, User } from '../../../src/types';
import { likePost, unlikePost, getPostById } from '../../../src/lib/db';
import { errorResponse, successResponse, parseJsonBody } from '../../../src/lib/utils';

/**
 * POST /api/posts/like - Like or unlike a post
 */
export const onRequestPost: PagesFunction<Env> = async ({ request, env, data }) => {
  const user = data.user as User;
  
  if (!user) {
    return errorResponse('Não autenticado', 401);
  }
  
  const body = await parseJsonBody<{
    post_id: number;
    action: 'like' | 'unlike';
  }>(request);
  
  if (!body || !body.post_id) {
    return errorResponse('Dados inválidos', 400);
  }
  
  const { post_id, action } = body;
  
  // Check if post exists
  const post = await getPostById(env.DB, post_id, user.id);
  
  if (!post) {
    return errorResponse('Post não encontrado', 404);
  }
  
  // Like or unlike
  let success: boolean;
  
  if (action === 'unlike') {
    success = await unlikePost(env.DB, post_id, user.id);
  } else {
    success = await likePost(env.DB, post_id, user.id);
  }
  
  if (!success) {
    return errorResponse('Erro ao processar curtida', 500);
  }
  
  return successResponse(
    { post_id, action },
    action === 'like' ? 'Post curtido' : 'Curtida removida'
  );
};
