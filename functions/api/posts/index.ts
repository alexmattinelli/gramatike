// /functions/api/posts/index.ts
import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env, User, Post } from '../../../src/types';
import { jsonResponse, errorResponse } from '../../../src/lib/response';

// GET /api/posts - List posts with pagination
export const onRequestGet: PagesFunction<Env> = async ({ request, env }) => {
  try {
    const url = new URL(request.url);
    const limit = parseInt(url.searchParams.get('limit') || '50');
    const offset = parseInt(url.searchParams.get('offset') || '0');
    
    // Buscar posts com informações dos usuários
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
      ORDER BY posts.created_at DESC
      LIMIT ? OFFSET ?`
    ).bind(limit, offset).all();
    
    // Contar total de posts para paginação
    const { results: countResults } = await env.DB.prepare(
      'SELECT COUNT(*) as total FROM posts'
    ).all();
    const total = countResults[0]?.total || 0;
    
    return jsonResponse({ 
      posts: results,
      pagination: {
        limit,
        offset,
        total,
        hasMore: offset + limit < total
      }
    });
  } catch (error) {
    console.error('[posts/index] GET Error:', error);
    return errorResponse('Erro ao buscar posts', 500);
  }
};

// POST /api/posts - Create post
export const onRequestPost: PagesFunction<Env> = async ({ request, env, data }) => {
  try {
    const user = data.user as User;
    if (!user) {
      return errorResponse('Não autorizado', 401);
    }
    
    const body = await request.json() as { content: string };
    const { content } = body;
    
    // Validação básica
    if (!content || content.trim().length === 0) {
      return errorResponse('Conteúdo não pode estar vazio', 400);
    }
    
    if (content.length > 5000) {
      return errorResponse('Conteúdo muito longo (máx: 5000 caracteres)', 400);
    }
    
    // Criar post
    const { success, meta } = await env.DB.prepare(
      `INSERT INTO posts (user_id, content, likes, comments) 
       VALUES (?, ?, 0, 0)`
    ).bind(user.id, content.trim()).run();
    
    if (!success) {
      return errorResponse('Erro ao criar post', 500);
    }
    
    // Buscar o post criado com dados do usuário
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
    ).bind(meta.last_row_id).all();
    
    const post = results[0];
    
    return jsonResponse({ post }, 201);
  } catch (error) {
    console.error('[posts/index] POST Error:', error);
    return errorResponse('Erro ao criar post', 500);
  }
};

// OPTIONS para CORS (importante para frontend)
export const onRequestOptions: PagesFunction = async () => {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400',
    },
  });
};
