// Posts API - List and Create
import type { Env, User } from '../../../src/types';
import { getPosts, createPost } from '../../../src/lib/db';
import { getCurrentUser } from '../../../src/lib/auth';
import { errorResponse, successResponse, parseJsonBody, getQueryParam, validateContent } from '../../../src/lib/utils';

/**
 * GET /api/posts - List posts
 */
export const onRequestGet: PagesFunction<Env> = async ({ request, env }) => {
  const pageParam = getQueryParam(request, 'page');
  const page = pageParam ? parseInt(pageParam) : 1;
  const perPage = 20;
  
  // Get current user (optional for viewing posts)
  const user = await getCurrentUser(request, env.DB);
  const userId = user?.id;
  
  const posts = await getPosts(env.DB, page, perPage, userId);
  
  return successResponse({ posts, page, perPage });
};

/**
 * POST /api/posts - Create a new post
 */
export const onRequestPost: PagesFunction<Env> = async ({ request, env, data }) => {
  const user = data.user as User;
  
  if (!user) {
    return errorResponse('Não autenticado', 401);
  }
  
  const body = await parseJsonBody<{
    conteudo: string;
    imagem?: string;
  }>(request);
  
  if (!body) {
    return errorResponse('Dados inválidos', 400);
  }
  
  let { conteudo, imagem } = body;
  
  // Validate content
  const validation = validateContent(conteudo);
  if (!validation.valid) {
    return errorResponse(validation.error || 'Conteúdo inválido', 400);
  }
  
  // Ensure empty strings become undefined (will be sanitized to null in createPost)
  if (imagem && imagem.trim() === '') {
    imagem = undefined;
  }
  
  console.log('[POST /api/posts] Creating post:', {
    userId: user.id,
    contentLength: conteudo.length,
    hasImage: !!imagem
  });
  
  // Create post - createPost will sanitize parameters
  const postId = await createPost(env.DB, user.id, conteudo, imagem);
  
  if (!postId) {
    return errorResponse('Erro ao criar post', 500);
  }
  
  return successResponse(
    { id: postId },
    'Post criado com sucesso',
    201
  );
};
