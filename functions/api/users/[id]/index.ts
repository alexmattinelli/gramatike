/**
 * Get User Profile
 * GET /api/users/[id] - Get user profile with follow stats
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

    // Get user profile
    const user = await db.prepare(`
      SELECT 
        id,
        username,
        name,
        email,
        avatar_initials,
        verified,
        online_status,
        created_at
      FROM users
      WHERE id = ? AND is_banned = 0
    `).bind(targetUserId).first();

    if (!user) {
      return new Response(JSON.stringify({ 
        error: 'Usuário não encontrado' 
      }), { 
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Get follower count
    const followersCount = await db.prepare(
      'SELECT COUNT(*) as count FROM user_follows WHERE following_id = ?'
    ).bind(targetUserId).first();

    // Get following count
    const followingCount = await db.prepare(
      'SELECT COUNT(*) as count FROM user_follows WHERE follower_id = ?'
    ).bind(targetUserId).first();

    // Check if current user is following this user
    let isFollowing = false;
    let followsYou = false;

    if (currentUser) {
      const followCheck = await db.prepare(
        'SELECT id FROM user_follows WHERE follower_id = ? AND following_id = ?'
      ).bind(currentUser.user_id, targetUserId).first();
      
      isFollowing = !!followCheck;

      // Check if this user follows current user back
      const followBackCheck = await db.prepare(
        'SELECT id FROM user_follows WHERE follower_id = ? AND following_id = ?'
      ).bind(targetUserId, currentUser.user_id).first();
      
      followsYou = !!followBackCheck;
    }

    return new Response(JSON.stringify({ 
      success: true,
      user: {
        ...user,
        followers_count: followersCount?.count || 0,
        following_count: followingCount?.count || 0,
        is_following: isFollowing,
        follows_you: followsYou,
        is_mutual: isFollowing && followsYou
      }
    }), { 
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Error getting user profile:', error);
    return new Response(JSON.stringify({ 
      error: 'Erro ao buscar perfil',
      details: error instanceof Error ? error.message : 'Unknown error'
    }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
