/**
 * Get User Followers
 * GET /api/users/[id]/followers - Get list of followers
 */

interface Env {
  DB: D1Database;
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

    // Get followers with user details
    const followers = await db.prepare(`
      SELECT 
        u.id,
        u.username,
        u.name,
        u.avatar_initials,
        u.verified,
        uf.created_at as followed_at
      FROM user_follows uf
      JOIN users u ON u.id = uf.follower_id
      WHERE uf.following_id = ?
      ORDER BY uf.created_at DESC
      LIMIT 100
    `).bind(targetUserId).all();

    const count = await db.prepare(
      'SELECT COUNT(*) as count FROM user_follows WHERE following_id = ?'
    ).bind(targetUserId).first();

    return new Response(JSON.stringify({ 
      success: true,
      followers: followers.results || [],
      count: count?.count || 0
    }), { 
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Error getting followers:', error);
    return new Response(JSON.stringify({ 
      error: 'Erro ao buscar seguidores',
      details: error instanceof Error ? error.message : 'Unknown error'
    }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
