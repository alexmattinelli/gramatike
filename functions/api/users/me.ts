// GET /api/users/me - Get current user
// PATCH /api/users/me - Update profile

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../../src/types';
import { jsonResponse, errorResponse } from '../../../src/lib/response';

export const onRequestGet: PagesFunction<Env> = async ({ data }) => {
  try {
    const user = data.user;
    if (!user) {
      return errorResponse('Não autorizado', 401);
    }
    
    // Remove password from response
    const { password, ...userWithoutPassword } = user;
    
    return jsonResponse({ user: userWithoutPassword });
  } catch (error) {
    console.error('[users/me] GET Error:', error);
    return errorResponse('Erro ao buscar usuário', 500);
  }
};

export const onRequestPatch: PagesFunction<Env> = async ({ request, env, data }) => {
  try {
    const user = data.user;
    if (!user) {
      return errorResponse('Não autorizado', 401);
    }
    
    const { name, bio, avatar } = await request.json();
    
    const updates: string[] = [];
    const values: any[] = [];
    
    if (name !== undefined) {
      updates.push('name = ?');
      values.push(name);
    }
    if (bio !== undefined) {
      updates.push('bio = ?');
      values.push(bio);
    }
    if (avatar !== undefined) {
      updates.push('avatar = ?');
      values.push(avatar);
    }
    
    if (updates.length === 0) {
      return errorResponse('Nenhum campo para atualizar', 400);
    }
    
    updates.push("updated_at = datetime('now')");
    values.push(user.id);
    
    await env.DB.prepare(
      `UPDATE users SET ${updates.join(', ')} WHERE id = ?`
    ).bind(...values).run();
    
    // Get updated user
    const { results } = await env.DB.prepare(
      'SELECT * FROM users WHERE id = ?'
    ).bind(user.id).all();
    
    const updatedUser = results[0] as any;
    const { password, ...userWithoutPassword } = updatedUser;
    
    return jsonResponse({ user: userWithoutPassword });
  } catch (error) {
    console.error('[users/me] PATCH Error:', error);
    return errorResponse('Erro ao atualizar perfil', 500);
  }
};
