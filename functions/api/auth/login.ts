// functions/api/auth/login.ts
import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env, User } from '../../types';
import { jsonResponse, errorResponse } from '../../lib/response';
import type { PagesFunction } from '@cloudflare/workers-types';

interface LoginRequest {
  email: string;
  password: string;
}

interface User {
  id: number;
  username: string;
  email: string;
  password_hash: string;
  name?: string;
  avatar_initials?: string;
  verified: boolean;
  online_status: boolean;
  role: string;
  banned: boolean;
  created_at: string;
}

export const onRequestPost: PagesFunction<{ DB: any }> = async ({ request, env }) => {
  try {
    // Verificar corpo da requisição
    const body = await request.json() as LoginRequest;
    const { email, password } = body;
    
    // Validações básicas
    if (!email || !password) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Email e senha são obrigatórios'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Validação simples de email
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
    
    // Buscar usuário pelo email
    const { results } = await env.DB.prepare(
      'SELECT * FROM users WHERE email = ? LIMIT 1'
    ).bind(email.toLowerCase().trim()).all();
    
    if (!results || results.length === 0) {
      // Retornar erro genérico por segurança
      return new Response(JSON.stringify({
        success: false,
        error: 'Email ou senha incorretos'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    const user = results[0] as User;
    
    // Verificar se usuário está banido
    if (user.banned) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Usuário banido'
      }), {
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // VERIFICAÇÃO DE SENHA (SIMPLIFICADA)
    // IMPORTANTE: Em produção, use bcrypt ou Argon2!
    // Aqui estou usando uma verificação simples para demonstração
    
    // Se não tiver password_hash no banco, cria uma senha padrão
    if (!user.password_hash) {
      // Para desenvolvimento: senha padrão "123456"
      const defaultPassword = '123456';
      if (password !== defaultPassword) {
        return new Response(JSON.stringify({
          success: false,
          error: 'Email ou senha incorretos'
        }), {
          status: 401,
          headers: { 'Content-Type': 'application/json' }
        });
      }
    } else {
      // Em produção, descomente e implemente:
      // const isValid = await verifyPassword(password, user.password_hash);
      // if (!isValid) { return error response }
      
      // Por enquanto, compara diretamente (NÃO FAÇA ISSO EM PRODUÇÃO)
      if (password !== user.password_hash) {
        return new Response(JSON.stringify({
          success: false,
          error: 'Email ou senha incorretos'
        }), {
          status: 401,
          headers: { 'Content-Type': 'application/json' }
        });
      }
    }
    
    // Atualizar status online
    await env.DB.prepare(
      'UPDATE users SET online_status = true, last_active = CURRENT_TIMESTAMP WHERE id = ?'
    ).bind(user.id).run();
    
    // Criar sessão no banco
    const sessionId = crypto.randomUUID();
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 dias
    
    await env.DB.prepare(
      'INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)'
    ).bind(sessionId, user.id, expiresAt.toISOString()).run();
    
    // Criar cookie de sessão
    const sessionCookie = `session=${sessionId}; HttpOnly; Path=/; SameSite=Lax; Expires=${expiresAt.toUTCString()}; ${
      new URL(request.url).protocol === 'https:' ? 'Secure;' : ''
    }`;
    
    // Remover dados sensíveis da resposta
    const { password_hash, ...userWithoutPassword } = user;
    
    return new Response(JSON.stringify({
      success: true,
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        name: user.name,
        avatar_initials: user.avatar_initials,
        verified: user.verified,
        online_status: true,
        role: user.role,
        created_at: user.created_at
      },
      session: {
        id: sessionId,
        expires_at: expiresAt.toISOString()
      }
    }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Set-Cookie': sessionCookie
      }
    });
    
  } catch (error) {
    console.error('[login] Error:', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Erro interno ao fazer login'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};

// GET /api/auth/login - Verificar status (opcional)
export const onRequestGet: PagesFunction<{ DB: any }> = async ({ data }) => {
  const user = data.user;
  
  return new Response(JSON.stringify({
    success: true,
    authenticated: !!user,
    user: user || null
  }), {
    headers: { 'Content-Type': 'application/json' }
  });
};
