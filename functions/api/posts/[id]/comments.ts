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
    console.log('[posts/id/comments] POST - Starting comment creation');
    
    const user = data.user as User | null;
    if (!user) {
      console.error('[posts/id/comments] POST - User not authenticated - session may have expired');
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Sessão expirada. Por favor, faça login novamente.',
        errorCode: 'SESSION_EXPIRED'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    console.log('[posts/id/comments] POST - User authenticated:', { userId: user.id, username: user.username });
    
    const postId = parseInt(params.id as string);
    if (isNaN(postId)) {
      console.error('[posts/id/comments] POST - Invalid post ID:', params.id);
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
    
    console.log('[posts/id/comments] POST - Comment content length:', content?.length || 0);
    
    // Validação de conteúdo
    if (!content || content.length === 0) {
      console.warn('[posts/id/comments] POST - Empty comment content');
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Comentário não pode estar vazio' 
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    if (content.length > 1000) {
      console.warn('[posts/id/comments] POST - Comment too long:', content.length);
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
      console.error('[posts/id/comments] POST - Post not found:', postId);
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Post não encontrado' 
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    console.log('[posts/id/comments] POST - Creating comment for post:', postId);
    
    // Criar comentário
    const { success, meta } = await env.DB.prepare(
      `INSERT INTO post_comments (post_id, user_id, content) 
       VALUES (?, ?, ?)`
    ).bind(postId, user.id, content).run();
    
    if (!success) {
      console.error('[posts/id/comments] POST - Failed to create comment in database');
      throw new Error('Falha ao criar comentário no banco');
    }
    
    console.log('[posts/id/comments] POST - Comment created with ID:', meta.last_row_id);
    
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
    
    console.log('[posts/id/comments] POST - Success:', { commentId: meta.last_row_id, postId, userId: user.id });
    
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
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    const errorStack = error instanceof Error ? error.stack : '';
    console.error('[posts/id/comments] POST Error details:', errorMessage);
    console.error('[posts/id/comments] POST Error stack:', errorStack);
    
    return new Response(JSON.stringify({ 
      success: false, 
      error: 'Erro ao criar comentário. Por favor, tente novamente.' 
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
