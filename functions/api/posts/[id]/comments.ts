// GET /api/posts/:id/comments - List comments
// POST /api/posts/:id/comments - Create comment

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../../../src/types';
import { isValidCommentContent } from '../../../../src/lib/validation';
import { jsonResponse, errorResponse } from '../../../../src/lib/response';

export const onRequestGet: PagesFunction<Env> = async ({ params, env }) => {
  try {
    const postId = parseInt(params.id as string);
    if (isNaN(postId)) {
      return errorResponse('ID inválido', 400);
    }
    
    const { results } = await env.DB.prepare(`
      SELECT c.*, u.username, u.name, u.avatar
      FROM comments c
      JOIN users u ON c.user_id = u.id
      WHERE c.post_id = ?
      ORDER BY c.created_at ASC
    `).bind(postId).all();
    
    return jsonResponse({ comments: results });
  } catch (error) {
    console.error('[comments] GET Error:', error);
    return errorResponse('Erro ao buscar comentários', 500);
  }
};

export const onRequestPost: PagesFunction<Env> = async ({ params, request, env, data }) => {
  try {
    const user = data.user;
    if (!user) {
      return errorResponse('Não autorizado', 401);
    }
    
    const postId = parseInt(params.id as string);
    if (isNaN(postId)) {
      return errorResponse('ID inválido', 400);
    }
    
    const { content } = await request.json();
    
    if (!isValidCommentContent(content)) {
      return errorResponse('Comentário inválido (1-1000 caracteres)', 400);
    }
    
    const { results } = await env.DB.prepare(
      'INSERT INTO comments (user_id, post_id, content) VALUES (?, ?, ?) RETURNING *'
    ).bind(user.id, postId, content).all();
    
    const comment = results[0] as any;
    
    // Add user info
    const commentWithUser = {
      ...comment,
      username: user.username,
      name: user.name,
      avatar: user.avatar
    };
    
    return jsonResponse({ comment: commentWithUser }, 201);
  } catch (error) {
    console.error('[comments] POST Error:', error);
    return errorResponse('Erro ao criar comentário', 500);
  }
};
