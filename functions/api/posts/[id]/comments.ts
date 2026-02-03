// functions/api/posts/[id]/comments.ts
import type { PagesFunction } from '@cloudflare/workers-types';

interface User {
  id: number;
  username: string;
  name?: string;
  avatar_initials?: string;
}

interface Comment {
  id: number;
  post_id: number;
  user_id: number;
  content: string;
  created_at: string;
  username?: string;
  user_name?: string;
  avatar_initials?: string;
}

// GET /api/posts/:id/comments - Get all comments for a post
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
    
    // Buscar todos os comentários com informações do usuário
    const { results } = await env.DB.prepare(
      `SELECT 
        post_comments.id,
        post_comments.post_id,
        post_comments.user_id,
        post_comments.content,
        post_comments.created_at,
        users.username,
        users.name as user_name,
        users.avatar_initials,
        users.verified
       FROM post_comments
       INNER JOIN users ON post_comments.user_id = users.id
       WHERE post_comments.post_id = ?
       ORDER BY post_comments.created_at ASC`
    ).bind(postId).all();
    
    return new Response(JSON.stringify({ 
      success: true, 
      data: {
        comments: results || [],
        total: results?.length || 0
      }
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('[posts/id/comments] GET Error:', error);
    return new Response(JSON.stringify({ 
      success: false, 
      error: 'Erro ao buscar comentários' 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

// POST /api/posts/:id/comments - Create a comment on a post
export const onRequestPost: PagesFunction<{ DB: any }> = async ({ params, request, env, data }) => {
  try {
    const user = data.user as User | null;
    if (!user) {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Não autorizado' 
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
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
    
    const body = await request.json() as { content: string };
    const content = body.content?.trim();
    
    // Validação de conteúdo
    if (!content || content.length === 0) {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Comentário não pode estar vazio' 
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    if (content.length > 1000) {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Comentário muito longo (máx: 1000 caracteres)' 
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Verificar se post existe
    const { results: postResults } = await env.DB.prepare(
      'SELECT id, comments FROM posts WHERE id = ?'
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
    
    // Criar comentário
    const { success, meta } = await env.DB.prepare(
      `INSERT INTO post_comments (post_id, user_id, content) 
       VALUES (?, ?, ?)`
    ).bind(postId, user.id, content).run();
    
    if (!success) {
      throw new Error('Falha ao criar comentário no banco');
    }
    
    // Incrementar contador de comentários no post
    await env.DB.prepare(
      'UPDATE posts SET comments = comments + 1 WHERE id = ?'
    ).bind(postId).run();
    
    // Buscar comentário criado com dados do usuário
    const { results } = await env.DB.prepare(
      `SELECT 
        post_comments.*,
        users.username,
        users.name as user_name,
        users.avatar_initials,
        users.verified
       FROM post_comments
       INNER JOIN users ON post_comments.user_id = users.id
       WHERE post_comments.id = ?`
    ).bind(meta.last_row_id).all();
    
    const comment = results[0] as Comment;
    
    return new Response(JSON.stringify({ 
      success: true, 
      message: 'Comentário criado com sucesso',
      data: { comment }
    }), {
      status: 201,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('[posts/id/comments] POST Error:', error);
    return new Response(JSON.stringify({ 
      success: false, 
      error: 'Erro ao criar comentário' 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

// OPTIONS para CORS
export const onRequestOptions: PagesFunction = async () => {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400',
    },
  });
};
