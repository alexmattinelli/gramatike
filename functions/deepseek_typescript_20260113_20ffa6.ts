// functions/lib/auth.ts
export async function getUserFromRequest(request: Request, env: any): Promise<any> {
  try {
    // Versão SIMPLIFICADA - sempre retorna usuário 1 (admin)
    // Depois você implementa com cookies/sessões
    const { results } = await env.DB.prepare(
      "SELECT * FROM users WHERE id = 1 LIMIT 1"
    ).all();
    
    if (!results || results.length === 0) {
      return { user: null, session: null };
    }
    
    return {
      user: results[0],
      session: { id: 'temp', user_id: 1, expires_at: new Date().toISOString() }
    };
    
  } catch (error) {
    console.error('Auth error:', error);
    return { user: null, session: null };
  }
}

export function isAdmin(user: any): boolean {
  if (!user) return false;
  return user.role === 'admin' || user.role === 'moderator';
}