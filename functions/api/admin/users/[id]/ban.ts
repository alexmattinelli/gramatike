// functions/api/admin/users/[id]/ban.ts
import type { PagesFunction } from '@cloudflare/workers-types';

interface User {
  id: number;
  username: string;
  role?: string;
}

/**
 * POST /api/admin/users/[id]/ban - Ban a user
 */
export const onRequestPost: PagesFunction<{ DB: any }> = async ({ env, data, params }) => {
  // Verificar se usuário está autenticado
  const user = data.user as User | null;
  
  if (!user) {
    return new Response(JSON.stringify({ error: 'Não autenticado' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  // Verificar se é admin
  if (user.role !== 'admin' && user.role !== 'moderator') {
    return new Response(JSON.stringify({ error: 'Acesso negado' }), {
      status: 403,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  // Validar ID do usuário a ser banido
  const userId = parseInt(params.id as string);
  
  if (isNaN(userId)) {
    return new Response(JSON.stringify({ error: 'ID do usuário inválido' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  // Não pode banir a si mesmo
  if (userId === user.id) {
    return new Response(JSON.stringify({ error: 'Não pode banir a si mesmo' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  try {
    // Banir usuário no banco de dados
    const { success } = await env.DB.prepare(
      'UPDATE users SET banned = true, banned_at = CURRENT_TIMESTAMP, banned_by = ? WHERE id = ?'
    ).bind(user.id, userId).run();
    
    if (!success) {
      return new Response(JSON.stringify({ error: 'Erro ao banir usuário' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    return new Response(JSON.stringify({
      success: true,
      message: 'Usuário banido com sucesso'
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('[admin/ban] Error:', error);
    return new Response(JSON.stringify({ error: 'Erro interno do servidor' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

/**
 * DELETE /api/admin/users/[id]/ban - Unban a user (opcional)
 */
export const onRequestDelete: PagesFunction<{ DB: any }> = async ({ env, data, params }) => {
  const user = data.user as User | null;
  
  if (!user || (user.role !== 'admin' && user.role !== 'moderator')) {
    return new Response(JSON.stringify({ error: 'Acesso negado' }), {
      status: 403,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  const userId = parseInt(params.id as string);
  
  if (isNaN(userId)) {
    return new Response(JSON.stringify({ error: 'ID inválido' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  try {
    await env.DB.prepare(
      'UPDATE users SET banned = false, banned_at = NULL, banned_by = NULL WHERE id = ?'
    ).bind(userId).run();
    
    return new Response(JSON.stringify({
      success: true,
      message: 'Usuário desbanido'
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('[admin/unban] Error:', error);
    return new Response(JSON.stringify({ error: 'Erro ao desbanir usuário' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
