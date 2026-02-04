/**
 * Get User Posts
 * GET /api/users/[id]/posts - Get posts from a specific user
 */

interface Env {
  DB: D1Database;
}

interface UserSession {
  user_id: number;
  username: string;
  email: string;
}

function getAuthenticatedUser(context: any): UserSession | null {
  return context.data?.user || null;
}

export const onRequestGet: PagesFunction<Env> = async (context) => {
  try {
    const userId = context.params.id as string;
    const targetUserId = parseInt(userId);
    
    if (isNaN(targetUserId)) {
      return new Response(JSON.stringify({ 
        error: 'ID de usuário inválido' 
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const db = context.env.DB;
    const currentUser = getAuthenticatedUser(context);
    
    // Get pagination parameters
    const url = new URL(context.request.url);
    const limit = Math.min(parseInt(url.searchParams.get('limit') || '20'), 100);
    const offset = parseInt(url.searchParams.get('offset') || '0');

    // Check if user exists
    const user = await db.prepare(
      'SELECT id FROM users WHERE id = ? AND is_banned = 0'
    ).bind(targetUserId).first();

    if (!user) {
      return new Response(JSON.stringify({ 
        error: 'Usuário não encontrado' 
      }), { 
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Get user's posts with user info
    const posts = await db.prepare(`
      SELECT 
        p.id,
        p.content,
        p.likes,
        p.comments,
        p.created_at,
        u.id as user_id,
        u.username,
        u.name,
        u.avatar_initials
      FROM posts p
      JOIN users u ON p.user_id = u.id
      WHERE p.user_id = ?
      ORDER BY p.created_at DESC
      LIMIT ? OFFSET ?
    `).bind(targetUserId, limit, offset).all();

    // If current user is logged in, check which posts they liked
    const postsWithLikes = posts.results || [];
    
    if (currentUser && postsWithLikes.length > 0) {
      const postIds = postsWithLikes.map((p: any) => p.id);
      const placeholders = postIds.map(() => '?').join(',');
      
      const likedPosts = await db.prepare(
        `SELECT post_id FROM post_likes WHERE user_id = ? AND post_id IN (${placeholders})`
      ).bind(currentUser.user_id, ...postIds).all();
      
      const likedPostIds = new Set((likedPosts.results || []).map((l: any) => l.post_id));
      
      postsWithLikes.forEach((post: any) => {
        post.liked_by_me = likedPostIds.has(post.id);
      });
    }

    // Get total count
    const totalCount = await db.prepare(
      'SELECT COUNT(*) as count FROM posts WHERE user_id = ?'
    ).bind(targetUserId).first();

    return new Response(JSON.stringify({ 
      success: true,
      posts: postsWithLikes,
      pagination: {
        total: totalCount?.count || 0,
        limit,
        offset,
        has_more: (offset + limit) < (totalCount?.count || 0)
      }
    }), { 
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Error getting user posts:', error);
    return new Response(JSON.stringify({ 
      error: 'Erro ao buscar posts',
      details: error instanceof Error ? error.message : 'Unknown error'
    }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
