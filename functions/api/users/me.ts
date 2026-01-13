// functions/api/users/me.ts
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
  password_hash?: string;
  banned?: boolean;
}

// GET /api/users/me - Get current user
export const onRequestGet: PagesFunction<{ DB: any }> = async ({ data, env }) => {
  try {
    const user = data.user as User | null;
    
    if (!user) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Não autorizado'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Atualizar último acesso
    try {
      await env.DB.prepare(
        'UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE id = ?'
      ).bind(user.id).run();
    } catch (updateError) {
      console.warn('[users/me] Não foi possível atualizar last_active:', updateError);
    }
    
    // Buscar dados atualizados do usuário (opcional, mas bom para garantir dados frescos)
    const { results } = await env.DB.prepare(
      `SELECT 
        id, username, email, name, avatar_initials, 
        verified, online_status, role, created_at, banned
      FROM users WHERE id = ?`
    ).bind(user.id).all();
    
    const currentUser = results?.[0] || user;
    
    // Formatar resposta
    const userResponse = {
      id: currentUser.id,
      username: currentUser.username,
      email: currentUser.email ? currentUser.email.replace(/(.{2})(.*)(@.*)/, '$1***$3') : null, // Ocultar email parcialmente
      name: currentUser.name || currentUser.username,
      avatar_initials: currentUser.avatar_initials || currentUser.username?.charAt(0).toUpperCase() || 'U',
      verified: Boolean(currentUser.verified),
      online_status: Boolean(currentUser.online_status),
      role: currentUser.role || 'user',
      created_at: currentUser.created_at,
      banned: Boolean(currentUser.banned),
      stats: {
        // Poderia adicionar mais stats aqui (posts, likes, etc.)
      }
    };
    
    return new Response(JSON.stringify({
      success: true,
      data: { user: userResponse }
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('[users/me] GET Error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Erro ao buscar dados do usuário'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

// PUT /api/users/me - Update current user
export const onRequestPut: PagesFunction<{ DB: any }> = async ({ request, env, data }) => {
  try {
    const user = data.user as User | null;
    
    if (!user) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Não autorizado'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    const body = await request.json() as {
      name?: string;
      avatar_initials?: string;
      email?: string;
    };
    
    const updates: string[] = [];
    const params: any[] = [];
    
    // Validar e preparar updates
    if (body.name !== undefined) {
      const name = body.name.trim();
      if (name.length > 0 && name.length <= 50) {
        updates.push('name = ?');
        params.push(name);
      }
    }
    
    if (body.avatar_initials !== undefined) {
      const initials = body.avatar_initials.trim().toUpperCase();
      if (initials.length === 1 || initials.length === 2) {
        updates.push('avatar_initials = ?');
        params.push(initials);
      }
    }
    
    if (body.email !== undefined) {
      const email = body.email.toLowerCase().trim();
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      
      if (!emailRegex.test(email)) {
        return new Response(JSON.stringify({
          success: false,
          error: 'Email inválido'
        }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
      }
      
      // Verificar se email já está em uso por outro usuário
      const existing = await env.DB.prepare(
        'SELECT id FROM users WHERE email = ? AND id != ?'
      ).bind(email, user.id).first();
      
      if (existing) {
        return new Response(JSON.stringify({
          success: false,
          error: 'Email já está em uso'
        }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
      }
      
      updates.push('email = ?');
      params.push(email);
    }
    
    // Se não houver updates, retornar erro
    if (updates.length === 0) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Nenhum dado válido para atualizar'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Adicionar WHERE clause
    params.push(user.id);
    
    // Executar update
    const query = `UPDATE users SET ${updates.join(', ')}, updated_at = CURRENT_TIMESTAMP WHERE id = ?`;
    const { success } = await env.DB.prepare(query).bind(...params).run();
    
    if (!success) {
      throw new Error('Falha ao atualizar usuário');
    }
    
    // Buscar usuário atualizado
    const { results } = await env.DB.prepare(
      `SELECT 
        id, username, email, name, avatar_initials, 
        verified, online_status, role, created_at
      FROM users WHERE id = ?`
    ).bind(user.id).all();
    
    const updatedUser = results[0];
    
    return new Response(JSON.stringify({
      success: true,
      message: 'Perfil atualizado com sucesso',
      data: { user: updatedUser }
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('[users/me] PUT Error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Erro ao atualizar perfil'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
