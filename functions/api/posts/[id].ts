// functions/api/posts/[id].ts
import type { PagesFunction } from '@cloudflare/workers-types';

interface User {
  id: number;
  username: string;
  role?: string;
}

interface Post {
  id: number;
  user_id: number;
  content: string;
  likes: number;
  comments: number;
  created_at: string;
  updated_at?: string;
  username?: string;
  avatar_initials?: string;
  verified?: boolean;
  user_name?: string;
}

// GET /api/posts/:id - Get single post
export const onRequestGet: PagesFunction<{ DB: any }> = async ({ params, env, data }) => {
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
    
    // Buscar post com informações do usuário
    const { results } = await env.DB.prepare(
      `SELECT 
        posts.*,
        users.username,
        users.avatar_initials,
        users.verified,
        users.name as user_name,
        users.online_status
      FROM posts
      INNER JOIN users ON posts.user_id = users.id
      WHERE posts.id = ?`
    ).bind(postId).all();
    
    if (!results || results.length === 0) {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Post não encontrado' 
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    const post = results[0] as Post;
    
    // Check if the current user has liked this post (if authenticated)
    let userLiked = false;
    const user = data.user as User | null;
    if (user && user.id) {
      try {
        const { results: likeCheck } = await env.DB.prepare(
          'SELECT 1 FROM post_likes WHERE post_id = ? AND user_id = ?'
        ).bind(postId, user.id).all();
        userLiked = likeCheck && likeCheck.length > 0;
      } catch (e) {
        // Error checking likes, keep userLiked = false
        console.error('[posts/id] GET - Error checking user like:', e);
      }
    }
    
    return new Response(JSON.stringify({ 
      success: true, 
      data: { 
        post,
        userLiked
      } 
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('[posts/id] GET Error:', error);
    return new Response(JSON.stringify({ 
      success: false, 
      error: 'Erro ao buscar post' 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

// DELETE /api/posts/:id - Delete post
export const onRequestDelete: PagesFunction<{ DB: any }> = async ({ params, env, data }) => {
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
    
    // Get post to check ownership
    const { results } = await env.DB.prepare(
      'SELECT * FROM posts WHERE id = ?'
    ).bind(postId).all();
    
    const post = results[0] as Post;
    if (!post) {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Post não encontrado' 
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Check if user owns the post or is admin
    const isAdmin = user.role === 'admin' || user.role === 'moderator';
    if (post.user_id !== user.id && !isAdmin) {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Sem permissão' 
      }), {
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Delete post
    const { success } = await env.DB.prepare(
      'DELETE FROM posts WHERE id = ?'
    ).bind(postId).run();
    
    if (!success) {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Erro ao excluir post' 
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return new Response(JSON.stringify({ 
      success: true, 
      message: 'Post excluído com sucesso' 
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('[posts/id] DELETE Error:', error);
    return new Response(JSON.stringify({ 
      success: false, 
      error: 'Erro ao excluir post' 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

// PUT /api/posts/:id - Update post
export const onRequestPut: PagesFunction<{ DB: any }> = async ({ params, request, env, data }) => {
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
        error: 'Conteúdo não pode estar vazio' 
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    if (content.length > 5000) {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Conteúdo muito longo (máx: 5000 caracteres)' 
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Check ownership
    const { results } = await env.DB.prepare(
      'SELECT * FROM posts WHERE id = ?'
    ).bind(postId).all();
    
    const post = results[0] as Post;
    if (!post) {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Post não encontrado' 
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    const isAdmin = user.role === 'admin' || user.role === 'moderator';
    if (post.user_id !== user.id && !isAdmin) {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Sem permissão' 
      }), {
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Update post
    const { success } = await env.DB.prepare(
      'UPDATE posts SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?'
    ).bind(content, postId).run();
    
    if (!success) {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Erro ao atualizar post' 
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return new Response(JSON.stringify({ 
      success: true, 
      message: 'Post atualizado com sucesso',
      data: { content }
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('[posts/id] PUT Error:', error);
    return new Response(JSON.stringify({ 
      success: false, 
      error: 'Erro ao atualizar post' 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

// PATCH /api/posts/:id/like - Like/unlike a post
export const onRequestPatch: PagesFunction<{ DB: any }> = async ({ params, env, data }) => {
  try {
    console.log('[posts/id] PATCH - Starting like/unlike request');
    
    const user = data.user as User | null;
    if (!user) {
      console.error('[posts/id] PATCH - User not authenticated - session may have expired');
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Sessão expirada. Por favor, faça login novamente.',
        errorCode: 'SESSION_EXPIRED'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    console.log('[posts/id] PATCH - User authenticated:', { userId: user.id, username: user.username });
    
    const postId = parseInt(params.id as string);
    if (isNaN(postId)) {
      console.error('[posts/id] PATCH - Invalid post ID:', params.id);
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'ID inválido' 
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    console.log('[posts/id] PATCH - Processing like for post:', postId);
    
    // Verificar se post existe
    const { results: postResults } = await env.DB.prepare(
      'SELECT id FROM posts WHERE id = ?'
    ).bind(postId).all();
    
    if (!postResults || postResults.length === 0) {
      console.error('[posts/id] PATCH - Post not found:', postId);
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Post não encontrado' 
      }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    console.log('[posts/id] PATCH - Post exists, checking if already liked');
    
    // Verificar se usuário já curtiu
    let likeResults;
    try {
      const likeQuery = await env.DB.prepare(
        'SELECT id FROM post_likes WHERE post_id = ? AND user_id = ?'
      ).bind(postId, user.id).all();
      likeResults = likeQuery.results;
      console.log('[posts/id] PATCH - Like check result:', { alreadyLiked: likeResults && likeResults.length > 0 });
    } catch (error) {
      console.error('[posts/id] PATCH - Error checking post_likes table:', error);
      console.error('[posts/id] PATCH - This likely means the post_likes table does not exist in the database');
      console.error('[posts/id] PATCH - Please run: npx wrangler d1 execute <your-db-name> --remote --file=./db/schema.sql');
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Erro de configuração do banco de dados. A tabela post_likes não existe. Contate o administrador.' 
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    const alreadyLiked = likeResults && likeResults.length > 0;
    
    if (alreadyLiked) {
      console.log('[posts/id] PATCH - Removing like');
      // Unlike - remover curtida
      await env.DB.prepare(
        'DELETE FROM post_likes WHERE post_id = ? AND user_id = ?'
      ).bind(postId, user.id).run();
      
      // Decrementar contador
      await env.DB.prepare(
        'UPDATE posts SET likes = CASE WHEN likes > 0 THEN likes - 1 ELSE 0 END WHERE id = ?'
      ).bind(postId).run();
    } else {
      console.log('[posts/id] PATCH - Adding like');
      // Like - adicionar curtida
      await env.DB.prepare(
        'INSERT INTO post_likes (post_id, user_id) VALUES (?, ?)'
      ).bind(postId, user.id).run();
      
      // Incrementar contador
      await env.DB.prepare(
        'UPDATE posts SET likes = likes + 1 WHERE id = ?'
      ).bind(postId).run();
    }
    
    // Buscar novo número de likes e primeiros usuários
    const { results: countResults } = await env.DB.prepare(
      'SELECT likes FROM posts WHERE id = ?'
    ).bind(postId).all();
    
    const { results: usersResults } = await env.DB.prepare(
      `SELECT users.id, users.username, users.name, users.avatar_initials
       FROM post_likes
       INNER JOIN users ON post_likes.user_id = users.id
       WHERE post_likes.post_id = ?
       ORDER BY post_likes.created_at DESC
       LIMIT 3`
    ).bind(postId).all();
    
    console.log('[posts/id] PATCH - Success:', { postId, userId: user.id, liked: !alreadyLiked, newLikes: countResults[0]?.likes });
    
    return new Response(JSON.stringify({ 
      success: true, 
      message: alreadyLiked ? 'Curtida removida' : 'Post curtido',
      data: { 
        likes: countResults[0]?.likes || 0,
        liked: !alreadyLiked,
        likedBy: usersResults || []
      }
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('[posts/id] PATCH Error:', error);
    // More detailed error logging (server-side only)
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    const errorStack = error instanceof Error ? error.stack : '';
    console.error('[posts/id] PATCH Error details:', errorMessage);
    console.error('[posts/id] PATCH Error stack:', errorStack);
    
    return new Response(JSON.stringify({ 
      success: false, 
      error: 'Erro ao curtir post. Por favor, tente novamente.'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
