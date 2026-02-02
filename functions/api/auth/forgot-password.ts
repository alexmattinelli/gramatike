// functions/api/auth/forgot-password.ts
import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../types';

interface ForgotPasswordRequest {
  email: string;
}

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  try {
    const { email } = await request.json() as ForgotPasswordRequest;
    
    if (!email) {
      return Response.json({
        success: false,
        error: 'Email é obrigatório'
      }, { status: 400 });
    }
    
    // Validação de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return Response.json({
        success: false,
        error: 'Email inválido'
      }, { status: 400 });
    }
    
    // Buscar usuário pelo email
    const { results } = await env.DB.prepare(
      'SELECT id, email, username FROM users WHERE email = ? LIMIT 1'
    ).bind(email.toLowerCase().trim()).all();
    
    // Por segurança, sempre retornar sucesso mesmo se usuário não existir
    // Isso evita que atacantes descubram quais emails estão cadastrados
    if (!results || results.length === 0) {
      return Response.json({
        success: true,
        message: 'Se o email existir, você receberá instruções de recuperação'
      }, { status: 200 });
    }
    
    const user = results[0] as { id: number; email: string; username: string };
    
    // Gerar token de recuperação (6 dígitos para simplicidade)
    const token = Math.floor(100000 + Math.random() * 900000).toString();
    const expiresAt = new Date(Date.now() + 30 * 60 * 1000); // 30 minutos
    
    // Salvar token no banco
    await env.DB.prepare(
      'INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)'
    ).bind(user.id, token, expiresAt.toISOString()).run();
    
    // TODO: Em produção, enviar email com o token
    // Por enquanto, retornar o token na resposta (apenas para desenvolvimento)
    console.log(`[forgot-password] Token gerado para ${user.email}: ${token}`);
    
    return Response.json({
      success: true,
      message: 'Se o email existir, você receberá instruções de recuperação',
      // APENAS PARA DESENVOLVIMENTO - remover em produção!
      dev_token: token,
      dev_expires_at: expiresAt.toISOString()
    }, { status: 200 });
    
  } catch (error: any) {
    console.error('[forgot-password] Error:', error);
    return Response.json({
      success: false,
      error: 'Erro ao processar solicitação'
    }, { status: 500 });
  }
};
