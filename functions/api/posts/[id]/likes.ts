// functions/api/posts/[id]/likes.ts
import type { PagesFunction } from '@cloudflare/workers-types';

interface User {
  id: number;
  username: string;
  name?: string;
  avatar_initials?: string;
}

// GET /api/posts/:id/likes - Get all users who liked a post
export const onRequestGet: PagesFunction<{ DB: any }> = async ({ params, env }) => {
  try {
    const postId = parseInt(params.id as string);
    if (isNaN(postId)) {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'ID inválido' 
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Verificar se post existe
    const { results: postResults } = await env.DB.prepare(
      'SELECT id FROM posts WHERE id = ?'
    ).bind(postId).all();
    
    if (!postResults || postResults.length === 0) {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Post não encontrado' 
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Buscar todos os usuários que curtiram
    const { results } = await env.DB.prepare(
      `SELECT 
        users.id,
        users.username,
        users.name,
        users.avatar_initials,
        users.verified,
        post_likes.created_at
       FROM post_likes
       INNER JOIN users ON post_likes.user_id = users.id
       WHERE post_likes.post_id = ?
       ORDER BY post_likes.created_at DESC`
    ).bind(postId).all();
    
    return new Response(JSON.stringify({ 
      success: true, 
      data: {
        likes: results || [],
        total: results?.length || 0
      }
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('[posts/id/likes] GET Error:', error);
    return new Response(JSON.stringify({ 
      success: false, 
      error: 'Erro ao buscar curtidas' 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
