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
    
    return new Response(JSON.stringify({ 
      success: true, 
      data: { post } 
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
    
    // Verificar se usuário já curtiu (em uma tabela de likes separada, se tiver)
    // Por enquanto, apenas incrementa o contador
    const { success } = await env.DB.prepare(
      'UPDATE posts SET likes = likes + 1 WHERE id = ?'
    ).bind(postId).run();
    
    if (!success) {
      return new Response(JSON.stringify({ 
        success: false, 
        error: 'Erro ao curtir post' 
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Buscar novo número de likes
    const { results } = await env.DB.prepare(
      'SELECT likes FROM posts WHERE id = ?'
    ).bind(postId).all();
    
    return new Response(JSON.stringify({ 
      success: true, 
      message: 'Post curtido',
      data: { likes: results[0]?.likes || 0 }
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('[posts/id] PATCH Error:', error);
    return new Response(JSON.stringify({ 
      success: false, 
      error: 'Erro ao curtir post' 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
