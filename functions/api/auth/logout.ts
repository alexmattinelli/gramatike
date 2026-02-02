// functions/api/auth/logout.ts
import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env, User } from '../../types';
import { jsonResponse, errorResponse } from '../../lib/response';
import type { PagesFunction } from '@cloudflare/workers-types';

interface Session {
  id: string;
  user_id: number;
  expires_at: string;
}

export const onRequestPost: PagesFunction<{ DB: any }> = async ({ env, data }) => {
  try {
    const session = data.session as Session | null;
    
    // Se houver sessão no banco, removê-la
    if (session?.id) {
      try {
        await env.DB.prepare('DELETE FROM sessions WHERE id = ?')
          .bind(session.id)
          .run();
      } catch (dbError) {
        console.warn('[logout] Erro ao remover sessão do banco:', dbError);
        // Continua mesmo se falhar
      }
    }
    
    // Atualizar status online do usuário (se tiver user_id)
    if (session?.user_id) {
      try {
        await env.DB.prepare('UPDATE users SET online_status = 0 WHERE id = ?')
          .bind(session.user_id)
          .run();
      } catch (updateError) {
        console.warn('[logout] Erro ao atualizar status online:', updateError);
      }
    }
    
    // Cookie para expirar a sessão no cliente
    const logoutCookie = `session=; HttpOnly; Path=/; SameSite=Lax; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0`;
    
    return new Response(JSON.stringify({
      success: true,
      message: 'Logout realizado com sucesso'
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Set-Cookie': logoutCookie
      }
    });
    
  } catch (error) {
    console.error('[logout] Error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Erro ao fazer logout'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

// GET /api/auth/logout - Logout via GET também (para links simples)
export const onRequestGet: PagesFunction<{ DB: any }> = async ({ env, data }) => {
  try {
    const session = data.session as Session | null;
    
    // Mesma lógica do POST
    if (session?.id) {
      try {
        await env.DB.prepare('DELETE FROM sessions WHERE id = ?')
          .bind(session.id)
          .run();
      } catch (dbError) {
        console.warn('[logout GET] Erro ao remover sessão:', dbError);
      }
    }
    
    if (session?.user_id) {
      try {
        await env.DB.prepare('UPDATE users SET online_status = 0 WHERE id = ?')
          .bind(session.user_id)
          .run();
      } catch (updateError) {
        console.warn('[logout GET] Erro ao atualizar status:', updateError);
      }
    }
    
    const logoutCookie = `session=; HttpOnly; Path=/; SameSite=Lax; Expires=Thu, 01 Jan 1970 00:00:00 GMT`;
    
    // Redirecionar para a página inicial após logout
    return new Response(null, {
      status: 302,
      headers: {
        'Location': '/',
        'Set-Cookie': logoutCookie
      }
    });
    
  } catch (error) {
    console.error('[logout GET] Error:', error);
    // Mesmo com erro, redireciona e limpa cookie
    const logoutCookie = `session=; HttpOnly; Path=/; SameSite=Lax; Expires=Thu, 01 Jan 1970 00:00:00 GMT`;
    
    return new Response(null, {
      status: 302,
      headers: {
        'Location': '/',
        'Set-Cookie': logoutCookie
      }
    });
  }
};

// DELETE /api/auth/logout - Alternativa DELETE
export const onRequestDelete: PagesFunction<{ DB: any }> = async ({ env, data }) => {
  return onRequestPost({ env, data } as any);
};
