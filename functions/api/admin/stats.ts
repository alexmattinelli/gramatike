// GET /api/admin/stats - Admin dashboard statistics

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../../src/types';
import { isAdmin } from '../../../src/lib/auth';
import { jsonResponse, errorResponse } from '../../../src/lib/response';

export const onRequestGet: PagesFunction<Env> = async ({ env, data }) => {
  try {
    const user = data.user;
    if (!user || !isAdmin(user)) {
      return errorResponse('Sem permissão', 403);
    }
    
    // Get user count
    const usersCount = await env.DB.prepare(
      'SELECT COUNT(*) as count FROM users'
    ).first();
    
    // Get post count
    const postsCount = await env.DB.prepare(
      'SELECT COUNT(*) as count FROM posts'
    ).first();
    
    // Get comments count
    const commentsCount = await env.DB.prepare(
      'SELECT COUNT(*) as count FROM comments'
    ).first();
    
    // Get likes count
    const likesCount = await env.DB.prepare(
      'SELECT COUNT(*) as count FROM likes'
    ).first();
    
    return jsonResponse({
      stats: {
        users: usersCount?.count || 0,
        posts: postsCount?.count || 0,
        comments: commentsCount?.count || 0,
        likes: likesCount?.count || 0
      }
    });
  } catch (error) {
    console.error('[admin/stats] Error:', error);
    return errorResponse('Erro ao buscar estatísticas', 500);
  }
};
