/**
 * Get Mutual Friends (Amigos)
 * GET /api/users/me/amigos - Get list of mutual followers (users who follow each other)
 */

interface Env {
  DB: D1Database;
}

interface User {
  id: number;
  username: string;
}

export const onRequestGet: PagesFunction<Env> = async (context) => {
  try {
    const currentUser = context.data.user as User | null;
    
    if (!currentUser) {
      return new Response(JSON.stringify({ 
        error: 'Não autorizado' 
      }), { 
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const db = context.env.DB;
    const userId = currentUser.id;

    // Get mutual followers (users who follow each other)
    // A user is a "friend" if:
    // 1. Current user follows them (follower_id = currentUser, following_id = other)
    // 2. They follow current user back (follower_id = other, following_id = currentUser)
    const amigos = await db.prepare(`
      SELECT DISTINCT
        u.id,
        u.username,
        u.name,
        u.avatar_initials,
        u.verified,
        u.online_status as online
      FROM user_follows uf1
      JOIN user_follows uf2 ON uf1.following_id = uf2.follower_id AND uf1.follower_id = uf2.following_id
      JOIN users u ON u.id = uf1.following_id
      WHERE uf1.follower_id = ?
      ORDER BY u.name, u.username
      LIMIT 100
    `).bind(userId).all();

    return new Response(JSON.stringify({ 
      success: true,
      amigos: amigos.results || []
    }), { 
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Error getting amigos:', error);
    return new Response(JSON.stringify({ 
      error: 'Erro ao buscar amigues',
      details: error instanceof Error ? error.message : 'Unknown error'
    }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
