// functions/api/auth/reset-password.ts
import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../types';

interface ResetPasswordRequest {
  email: string;
  token: string;
  newPassword: string;
}

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  try {
    const { email, token, newPassword } = await request.json() as ResetPasswordRequest;
    
    // Validações
    if (!email || !token || !newPassword) {
      return Response.json({
        success: false,
        error: 'Email, token e nova senha são obrigatórios'
      }, { status: 400 });
    }
    
    if (newPassword.length < 6) {
      return Response.json({
        success: false,
        error: 'A senha deve ter no mínimo 6 caracteres'
      }, { status: 400 });
    }
    
    // Buscar usuário pelo email
    const { results: userResults } = await env.DB.prepare(
      'SELECT id, email FROM users WHERE email = ? LIMIT 1'
    ).bind(email.toLowerCase().trim()).all();
    
    if (!userResults || userResults.length === 0) {
      return Response.json({
        success: false,
        error: 'Token inválido ou expirado'
      }, { status: 400 });
    }
    
    const user = userResults[0] as { id: number; email: string };
    
    // Buscar token de recuperação válido
    const { results: tokenResults } = await env.DB.prepare(`
      SELECT id, expires_at, used 
      FROM password_resets 
      WHERE user_id = ? AND token = ? AND used = 0
      ORDER BY created_at DESC
      LIMIT 1
    `).bind(user.id, token).all();
    
    if (!tokenResults || tokenResults.length === 0) {
      return Response.json({
        success: false,
        error: 'Token inválido ou já utilizado'
      }, { status: 400 });
    }
    
    const resetToken = tokenResults[0] as { id: number; expires_at: string; used: number };
    
    // Verificar se o token expirou
    const expiresAt = new Date(resetToken.expires_at);
    if (expiresAt < new Date()) {
      return Response.json({
        success: false,
        error: 'Token expirado. Solicite uma nova recuperação de senha'
      }, { status: 400 });
    }
    
    // Atualizar a senha do usuário
    // TODO: SECURITY - Hash password before production! Use bcrypt.hash(newPassword, 10)
    // ⚠️ CRITICAL: Currently storing plain text passwords - NEVER use in production
    await env.DB.prepare(
      'UPDATE users SET password_hash = ? WHERE id = ?'
    ).bind(newPassword, user.id).run();
    
    // Marcar token como usado
    await env.DB.prepare(
      'UPDATE password_resets SET used = 1 WHERE id = ?'
    ).bind(resetToken.id).run();
    
    // Invalidar todas as sessões do usuário (por segurança)
    await env.DB.prepare(
      'DELETE FROM sessions WHERE user_id = ?'
    ).bind(user.id).run();
    
    return Response.json({
      success: true,
      message: 'Senha alterada com sucesso! Faça login com sua nova senha'
    }, { status: 200 });
    
  } catch (error: any) {
    console.error('[reset-password] Error:', error);
    return Response.json({
      success: false,
      error: 'Erro ao redefinir senha'
    }, { status: 500 });
  }
};
