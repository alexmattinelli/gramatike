// functions/api/posts/index.ts
import type { PagesFunction } from '@cloudflare/workers-types';

interface User {
  id: number;
  username: string;
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
  online_status?: boolean;
}

// GET /api/posts - List posts with pagination
export const onRequestGet: PagesFunction<{ DB: any }> = async ({ request, env }) => {
  try {
    const url = new URL(request.url);
    const limit = Math.min(parseInt(url.searchParams.get('limit') || '50'), 100); // Máximo 100
    const offset = parseInt(url.searchParams.get('offset') || '0');
    const userId = url.searchParams.get('user_id'); // Filtro opcional por usuário
    
    let query = `
      SELECT 
        posts.*,
        users.username,
        users.avatar_initials,
        users.verified,
        users.name as user_name,
        users.online_status
      FROM posts
      INNER JOIN users ON posts.user_id = users.id
    `;
    
    let params: any[] = [];
    
    // Adicionar filtro por usuário se especificado
    if (userId && !isNaN(parseInt(userId))) {
      query += ' WHERE posts.user_id = ?';
      params.push(parseInt(userId));
    }
    
    query += ' ORDER BY posts.created_at DESC LIMIT ? OFFSET ?';
    params.push(limit, offset);
    
    // Buscar posts
    const { results } = await env.DB.prepare(query).bind(...params).all();
    
    // Contar total de posts (com filtro se aplicável)
    let countQuery = 'SELECT COUNT(*) as total FROM posts';
    let countParams: any[] = [];
    
    if (userId && !isNaN(parseInt(userId))) {
      countQuery += ' WHERE user_id = ?';
      countParams.push(parseInt(userId));
    }
    
    const { results: countResults } = await env.DB.prepare(countQuery)
      .bind(...countParams).all();
    
    const total = countResults[0]?.total || 0;
    
    return new Response(JSON.stringify({
      success: true,
      data: {
        posts: results || [],
        pagination: {
          limit,
          offset,
          total,
          pages: Math.ceil(total / limit),
          hasMore: offset + limit < total,
          hasPrev: offset > 0
        }
      }
    }), {
      headers: { 
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=60' // Cache de 1 minuto
      }
    });
    
  } catch (error) {
    console.error('[posts/index] GET Error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Erro ao buscar posts'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

// POST /api/posts - Create post
export const onRequestPost: PagesFunction<{ DB: any }> = async ({ request, env, data }) => {
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
    
    const body = await request.json() as { content: string };
    const content = body.content?.trim();
    
    // Validação
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
    
    // Criar post
    const { success, meta } = await env.DB.prepare(
      `INSERT INTO posts (user_id, content, likes, comments) 
       VALUES (?, ?, 0, 0)`
    ).bind(user.id, content).run();
    
    if (!success) {
      throw new Error('Falha ao criar post no banco');
    }
    
    // Buscar post criado com dados do usuário
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
    ).bind(meta.last_row_id).all();
    
    const post = results[0] as Post;
    
    return new Response(JSON.stringify({
      success: true,
      message: 'Post criado com sucesso',
      data: { post }
    }), {
      status: 201,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('[posts/index] POST Error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Erro ao criar post'
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
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400',
    },
  });
};
