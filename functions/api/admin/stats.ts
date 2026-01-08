// Admin Dashboard API
import type { Env, User } from '../../../src/types';
import { isAdmin } from '../../../src/lib/auth';
import { errorResponse, successResponse } from '../../../src/lib/utils';

/**
 * GET /api/admin/stats - Get admin dashboard statistics
 */
export const onRequestGet: PagesFunction<Env> = async ({ request, env, data }) => {
  const user = data.user as User;
  
  if (!user || !isAdmin(user)) {
    return errorResponse('Acesso negado', 403);
  }
  
  // Get statistics
  const userCount = await env.DB.prepare('SELECT COUNT(*) as count FROM user').first<{ count: number }>();
  const postCount = await env.DB.prepare('SELECT COUNT(*) as count FROM post WHERE is_deleted = 0').first<{ count: number }>();
  const eduCount = await env.DB.prepare('SELECT COUNT(*) as count FROM edu_content WHERE is_deleted = 0').first<{ count: number }>();
  
  // Get recent users
  const recentUsers = await env.DB.prepare(
    'SELECT id, username, email, created_at, is_admin, is_banned FROM user ORDER BY created_at DESC LIMIT 10'
  ).all();
  
  // Get recent posts
  const recentPosts = await env.DB.prepare(
    'SELECT p.id, p.conteudo, p.data, u.username FROM post p LEFT JOIN user u ON p.usuarie_id = u.id WHERE p.is_deleted = 0 ORDER BY p.data DESC LIMIT 10'
  ).all();
  
  // Get activity for today
  const today = new Date().toISOString().split('T')[0];
  const todayActivity = await env.DB.prepare(
    'SELECT COUNT(*) as count FROM post WHERE DATE(data) = ? AND is_deleted = 0'
  ).bind(today).first<{ count: number }>();
  
  return successResponse({
    total_users: userCount?.count || 0,
    total_posts: postCount?.count || 0,
    activity_today: todayActivity?.count || 0,
    activity_chart: {
      labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
      posts: [5, 8, 12, 6, 15, 10, 7] // TODO: Get real data from last 7 days
    },
    recentUsers: recentUsers.results || [],
    recentPosts: recentPosts.results || []
  });
};
