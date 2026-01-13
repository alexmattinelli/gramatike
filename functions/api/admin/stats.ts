// functions/api/admin/stats.ts
import type { PagesFunction } from '@cloudflare/workers-types';

interface User {
  id: number;
  role?: string;
}

interface Stats {
  totalUsers: number;
  totalPosts: number;
  totalLikes: number;
  totalComments: number;
  usersToday: number;
  postsToday: number;
  activeUsers: number;
}

export const onRequestGet: PagesFunction<{ DB: any }> = async ({ env, data }) => {
  try {
    // Verificar autenticação e permissões
    const user = data.user as User | null;
    
    if (!user) {
      return new Response(JSON.stringify({ error: 'Não autenticado' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    if (user.role !== 'admin' && user.role !== 'moderator') {
      return new Response(JSON.stringify({ error: 'Sem permissão' }), {
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Buscar estatísticas do banco
    const [
      totalUsersResult,
      totalPostsResult,
      totalLikesResult,
      totalCommentsResult,
      usersTodayResult,
      postsTodayResult,
      activeUsersResult
    ] = await Promise.all([
      env.DB.prepare('SELECT COUNT(*) as count FROM users').first(),
      env.DB.prepare('SELECT COUNT(*) as count FROM posts').first(),
      env.DB.prepare('SELECT SUM(likes) as total FROM posts').first(),
      env.DB.prepare('SELECT SUM(comments) as total FROM posts').first(),
      env.DB.prepare(`
        SELECT COUNT(*) as count FROM users 
        WHERE DATE(created_at) = DATE('now')
      `).first(),
      env.DB.prepare(`
        SELECT COUNT(*) as count FROM posts 
        WHERE DATE(created_at) = DATE('now')
      `).first(),
      env.DB.prepare(`
        SELECT COUNT(DISTINCT user_id) as count FROM posts 
        WHERE DATE(created_at) >= DATE('now', '-7 days')
      `).first()
    ]);
    
    const stats: Stats = {
      totalUsers: totalUsersResult?.count || 0,
      totalPosts: totalPostsResult?.count || 0,
      totalLikes: totalLikesResult?.total || 0,
      totalComments: totalCommentsResult?.total || 0,
      usersToday: usersTodayResult?.count || 0,
      postsToday: postsTodayResult?.count || 0,
      activeUsers: activeUsersResult?.count || 0
    };
    
    return new Response(JSON.stringify({
      success: true,
      data: stats,
      timestamp: new Date().toISOString()
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('[admin/stats] Error:', error);
    return new Response(JSON.stringify({ 
      error: 'Erro ao buscar estatísticas',
      success: false 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
