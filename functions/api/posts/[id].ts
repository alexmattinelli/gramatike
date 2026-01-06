// Individual Post API - Get, Update, Delete
import type { Env, User } from '../../../src/types';
import { getPostById, deletePost } from '../../../src/lib/db';
import { isAdmin } from '../../../src/lib/auth';
import { errorResponse, successResponse } from '../../../src/lib/utils';

/**
 * GET /api/posts/[id] - Get a specific post
 */
export const onRequestGet: PagesFunction<Env> = async ({ request, env, params }) => {
  const postId = parseInt(params.id as string);
  
  if (isNaN(postId)) {
    return errorResponse('ID inválido', 400);
  }
  
  const post = await getPostById(env.DB, postId);
  
  if (!post) {
    return errorResponse('Post não encontrado', 404);
  }
  
  return successResponse({ post });
};

/**
 * DELETE /api/posts/[id] - Delete a post
 */
export const onRequestDelete: PagesFunction<Env> = async ({ request, env, data, params }) => {
  const user = data.user as User;
  
  if (!user) {
    return errorResponse('Não autenticado', 401);
  }
  
  const postId = parseInt(params.id as string);
  
  if (isNaN(postId)) {
    return errorResponse('ID inválido', 400);
  }
  
  // Get the post
  const post = await getPostById(env.DB, postId);
  
  if (!post) {
    return errorResponse('Post não encontrado', 404);
  }
  
  // Check if user owns the post or is admin
  const canDelete = post.usuarie_id === user.id || isAdmin(user);
  
  if (!canDelete) {
    return errorResponse('Sem permissão para deletar este post', 403);
  }
  
  // Delete the post
  const success = await deletePost(env.DB, postId, user.id);
  
  if (!success) {
    return errorResponse('Erro ao deletar post', 500);
  }
  
  return successResponse({}, 'Post deletado com sucesso');
};
