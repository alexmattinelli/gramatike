// /functions/api/posts/[id].ts
import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env, User } from '../../../src/types';
import { errorResponse, jsonResponse } from '../../../src/lib/response';
import { isAdmin } from '../../../src/lib/auth';

// GET /api/posts/:id - Get single post
export const onRequestGet: PagesFunction<Env> = async ({ params, env }) => {
  try {
    const postId = parseInt(params.id as string);
    if (isNaN(postId)) {
      return errorResponse('ID inválido', 400);
    }
    
    // Buscar post com informações do usuário
    const { results } = await env.DB.prepare(
      `SELECT 
        posts.*,
        users.username,
        users.avatar_initials,
        users.verified,
        users.name as user_name
      FROM posts
      INNER JOIN users ON posts.user_id = users.id
      WHERE posts.id = ?`
    ).bind(postId).all();
    
    if (!results || results.length === 0) {
      return errorResponse('Post não encontrado', 404);
    }
    
    const post = results[0];
    
    return jsonResponse({ post });
  } catch (error) {
    console.error('[posts/id] GET Error:', error);
    return errorResponse('Erro ao buscar post', 500);
  }
};

// DELETE /api/posts/:id - Delete post
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

// PUT /api/posts/:id - Update post (opcional)
export const onRequestPut: PagesFunction<Env> = async ({ params, request, env, data }) => {
  try {
    const user = data.user as User;
    if (!user) {
      return errorResponse('Não autorizado', 401);
    }
    
    const postId = parseInt(params.id as string);
    if (isNaN(postId)) {
      return errorResponse('ID inválido', 400);
    }
    
    const body = await request.json() as { content: string };
    const { content } = body;
    
    // Validação de conteúdo (você pode usar sua lib validation)
    if (!content || content.trim().length === 0 || content.length > 5000) {
      return errorResponse('Conteúdo inválido (1-5000 caracteres)', 400);
    }
    
    // Check ownership
    const { results } = await env.DB.prepare(
      'SELECT * FROM posts WHERE id = ?'
    ).bind(postId).all();
    
    const post = results[0] as any;
    if (!post) {
      return errorResponse('Post não encontrado', 404);
    }
    
    if (post.user_id !== user.id && !isAdmin(user)) {
      return errorResponse('Sem permissão', 403);
    }
    
    // Update post
    const { success } = await env.DB.prepare(
      'UPDATE posts SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?'
    ).bind(content.trim(), postId).run();
    
    if (!success) {
      return errorResponse('Erro ao atualizar post', 500);
    }
    
    return jsonResponse({ success: true, message: 'Post atualizado' });
  } catch (error) {
    console.error('[posts/id] PUT Error:', error);
    return errorResponse('Erro ao atualizar post', 500);
  }
};
