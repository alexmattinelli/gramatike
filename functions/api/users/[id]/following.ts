/**
 * Get User Following
 * GET /api/users/[id]/following - Get list of users being followed
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

    // Get following with user details
    const following = await db.prepare(`
      SELECT 
        u.id,
        u.username,
        u.name,
        u.avatar_initials,
        u.verified,
        uf.created_at as followed_at
      FROM user_follows uf
      JOIN users u ON u.id = uf.following_id
      WHERE uf.follower_id = ?
      ORDER BY uf.created_at DESC
      LIMIT 100
    `).bind(targetUserId).all();

    const count = await db.prepare(
      'SELECT COUNT(*) as count FROM user_follows WHERE follower_id = ?'
    ).bind(targetUserId).first();

    return new Response(JSON.stringify({ 
      success: true,
      following: following.results || [],
      count: count?.count || 0
    }), { 
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Error getting following:', error);
    return new Response(JSON.stringify({ 
      error: 'Erro ao buscar seguindo',
      details: error instanceof Error ? error.message : 'Unknown error'
    }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
