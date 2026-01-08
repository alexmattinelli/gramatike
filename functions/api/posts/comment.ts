// Post Comment API
import type { Env, User } from '../../../src/types';
import { errorResponse, successResponse } from '../../../src/lib/utils';

/**
 * POST /api/posts/comment - Add a comment to a post
 */
export const onRequestPost: PagesFunction<Env> = async ({ request, env, data }) => {
  const user = data.user as User;
  
  if (!user) {
    return errorResponse('Usuário não autenticado', 401);
  }
  
  try {
    const body = await request.json() as { post_id: number; conteudo: string; parent_id?: number };
    
    if (!body.post_id || !body.conteudo) {
      return errorResponse('Dados inválidos', 400);
    }
    
    // Clean and validate content
    const conteudo = body.conteudo.trim();
    
    if (conteudo.length === 0 || conteudo.length > 500) {
      return errorResponse('Comentário deve ter entre 1 e 500 caracteres', 400);
    }
    
    // Check if post exists and is not deleted
    const post = await env.DB.prepare(`
      SELECT id FROM post WHERE id = ? AND is_deleted = 0
    `).bind(body.post_id).first();
    
    if (!post) {
      return errorResponse('Post não encontrado', 404);
    }
    
    // Insert comment
    const result = await env.DB.prepare(`
      INSERT INTO comentario (post_id, usuarie_id, conteudo, parent_id)
      VALUES (?, ?, ?, ?)
    `).bind(body.post_id, user.id, conteudo, body.parent_id || null).run();
    
    // Get the created comment with user info
    const comment = await env.DB.prepare(`
      SELECT 
        c.id,
        c.conteudo,
        c.data,
        c.parent_id,
        u.id as user_id,
        u.username,
        u.nome,
        u.foto_perfil
      FROM comentario c
      LEFT JOIN user u ON c.usuarie_id = u.id
      WHERE c.id = ?
    `).bind(result.meta.last_row_id).first();
    
    return successResponse({
      message: 'Comentário adicionado',
      comment
    });
  } catch (error) {
    console.error('[posts/comment] Error:', error);
    return errorResponse('Erro ao adicionar comentário', 500);
  }
};

/**
 * GET /api/posts/comment?post_id=X - Get comments for a post
 */
export const onRequestGet: PagesFunction<Env> = async ({ request, env }) => {
  const url = new URL(request.url);
  const postId = url.searchParams.get('post_id');
  
  if (!postId) {
    return errorResponse('post_id é obrigatório', 400);
  }
  
  try {
    // Get comments for the post
    const comments = await env.DB.prepare(`
      SELECT 
        c.id,
        c.conteudo,
        c.data,
        c.parent_id,
        u.id as user_id,
        u.username,
        u.nome,
        u.foto_perfil
      FROM comentario c
      LEFT JOIN user u ON c.usuarie_id = u.id
      WHERE c.post_id = ? AND c.is_deleted = 0
      ORDER BY c.data DESC
    `).bind(postId).all();
    
    return successResponse({
      comments: comments.results || []
    });
  } catch (error) {
    console.error('[posts/comment] Error:', error);
    return errorResponse('Erro ao buscar comentários', 500);
  }
};
