/**
 * Follow/Unfollow User API
 * POST /api/users/[id]/follow - Follow user
 * DELETE /api/users/[id]/follow - Unfollow user
 */

interface Env {
  DB: D1Database;
}

interface UserSession {
  user_id: number;
  username: string;
  email: string;
}

// Get authenticated user from middleware
function getAuthenticatedUser(context: any): UserSession | null {
  return context.data?.user || null;
}

// POST - Follow user
export const onRequestPost: PagesFunction<Env> = async (context) => {
  try {
    const user = getAuthenticatedUser(context);
    
    if (!user) {
      return new Response(JSON.stringify({ 
        error: 'Não autenticado',
        errorCode: 'UNAUTHORIZED' 
      }), { 
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }

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

    // Prevent following yourself
    if (user.user_id === targetUserId) {
      return new Response(JSON.stringify({ 
        error: 'Você não pode seguir a si mesmo' 
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const db = context.env.DB;

    // Check if target user exists
    const targetUser = await db.prepare(
      'SELECT id FROM users WHERE id = ?'
    ).bind(targetUserId).first();

    if (!targetUser) {
      return new Response(JSON.stringify({ 
        error: 'Usuário não encontrado' 
      }), { 
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Check if already following
    const existingFollow = await db.prepare(
      'SELECT id FROM user_follows WHERE follower_id = ? AND following_id = ?'
    ).bind(user.user_id, targetUserId).first();

    if (existingFollow) {
      return new Response(JSON.stringify({ 
        error: 'Você já segue este usuário',
        following: true
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Create follow relationship
    await db.prepare(
      'INSERT INTO user_follows (follower_id, following_id) VALUES (?, ?)'
    ).bind(user.user_id, targetUserId).run();

    console.log(`User ${user.user_id} followed user ${targetUserId}`);

    return new Response(JSON.stringify({ 
      success: true,
      following: true,
      message: 'Seguindo com sucesso'
    }), { 
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Error following user:', error);
    return new Response(JSON.stringify({ 
      error: 'Erro ao seguir usuário',
      details: error instanceof Error ? error.message : 'Unknown error'
    }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

// DELETE - Unfollow user
export const onRequestDelete: PagesFunction<Env> = async (context) => {
  try {
    const user = getAuthenticatedUser(context);
    
    if (!user) {
      return new Response(JSON.stringify({ 
        error: 'Não autenticado',
        errorCode: 'UNAUTHORIZED' 
      }), { 
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }

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

    // Delete follow relationship
    const result = await db.prepare(
      'DELETE FROM user_follows WHERE follower_id = ? AND following_id = ?'
    ).bind(user.user_id, targetUserId).run();

    if (result.meta.changes === 0) {
      return new Response(JSON.stringify({ 
        error: 'Você não segue este usuário',
        following: false
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    console.log(`User ${user.user_id} unfollowed user ${targetUserId}`);

    return new Response(JSON.stringify({ 
      success: true,
      following: false,
      message: 'Deixou de seguir'
    }), { 
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Error unfollowing user:', error);
    return new Response(JSON.stringify({ 
      error: 'Erro ao deixar de seguir',
      details: error instanceof Error ? error.message : 'Unknown error'
    }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
