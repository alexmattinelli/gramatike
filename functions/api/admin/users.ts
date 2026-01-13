// functions/api/admin/users.ts
import type { PagesFunction } from '@cloudflare/workers-types';

interface User {
  id: number;
  username: string;
  email?: string;
  name?: string;
  avatar_initials?: string;
  verified: boolean;
  online_status: boolean;
  role: string;
  created_at: string;
  post_count?: number;
  banned?: boolean;
}

export const onRequestGet: PagesFunction<{ DB: any }> = async ({ env, data, request }) => {
  // Verificar autenticação e permissões
  const currentUser = data.user as User | null;
  
  if (!currentUser) {
    return new Response(JSON.stringify({ error: 'Não autenticado' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  if (currentUser.role !== 'admin' && currentUser.role !== 'moderator') {
    return new Response(JSON.stringify({ error: 'Acesso negado' }), {
      status: 403,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  try {
    // Obter parâmetros de paginação da URL
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '50');
    const offset = (page - 1) * limit;
    
    // Buscar usuários com contagem de posts
    const { results: users } = await env.DB.prepare(`
      SELECT 
        users.*,
        COUNT(posts.id) as post_count,
        (SELECT COUNT(*) FROM posts WHERE user_id = users.id AND DATE(created_at) = DATE('now')) as posts_today
      FROM users
      LEFT JOIN posts ON users.id = posts.user_id
      GROUP BY users.id
      ORDER BY users.created_at DESC
      LIMIT ? OFFSET ?
    `).bind(limit, offset).all();
    
    // Buscar total de usuários para paginação
    const { results: countResult } = await env.DB.prepare(
      'SELECT COUNT(*) as total FROM users'
    ).all();
    const total = countResult[0]?.total || 0;
    
    // Formatar dados sensíveis (ocultar email parcialmente)
    const safeUsers = users.map((user: any) => ({
      id: user.id,
      username: user.username,
      email: user.email ? user.email.replace(/(.{2})(.*)(@.*)/, '$1***$3') : null,
      name: user.name,
      avatar_initials: user.avatar_initials,
      verified: Boolean(user.verified),
      online_status: Boolean(user.online_status),
      role: user.role,
      banned: Boolean(user.banned),
      created_at: user.created_at,
      post_count: user.post_count || 0,
      posts_today: user.posts_today || 0,
      last_active: user.last_active
    }));
    
    return new Response(JSON.stringify({
      success: true,
      data: {
        users: safeUsers,
        pagination: {
          page,
          limit,
          total,
          pages: Math.ceil(total / limit),
          hasNext: offset + limit < total,
          hasPrev: page > 1
        }
      }
    }), {
      headers: { 
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store'
      }
    });
    
  } catch (error) {
    console.error('[admin/users] Error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Erro ao buscar usuários'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
