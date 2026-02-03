// functions/api/auth/login.ts
import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../types';
import { verifyPassword } from '../../../src/lib/crypto';

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
  is_banned: boolean;
  created_at: string;
}

export const onRequestPost: PagesFunction<{ DB: any }> = async ({ request, env }) => {
  try {
    const { email, password } = await request.json();
    
    // ADICIONAR:
    console.log('[login] Tentativa de login:', { email, hasPassword: !!password });
    
    if (!email || !password) {
      console.log('[login] ❌ Email ou senha não fornecidos');
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
    
    // ADICIONAR:
    console.log('[login] Resultado da busca:', { 
      userFound: !!results && results.length > 0,
      username: results && results.length > 0 ? results[0].username : undefined
    });
    
    if (!results || results.length === 0) {
      console.log('[login] ❌ Usuário não encontrado');
      return new Response(JSON.stringify({
        success: false,
        error: 'Email ou senha incorretos'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    const user = results[0] as User;
    console.log('[login] Usuário encontrado:', { id: user.id, username: user.username, email: user.email });
    console.log('[login] Tem password_hash?', !!user.password_hash);
    
    // Verificar se usuário está banido
    if (user.is_banned) {
      console.log('[login] ❌ Usuário banido:', user.username);
      return new Response(JSON.stringify({
        success: false,
        error: 'Usuário banido'
      }), {
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Verificar senha
    console.log('[login] Verificando senha...');
    
    // Se não tiver password_hash no banco, rejeitar
    if (!user.password_hash) {
      console.log('[login] ⚠️ Usuário sem password_hash no banco');
      return new Response(JSON.stringify({
        success: false,
        error: 'Email ou senha incorretos'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    console.log('[login] Comparando senha com hash armazenado');
    const isPasswordValid = await verifyPassword(password, user.password_hash);
    
    if (!isPasswordValid) {
      console.log('[login] ❌ Senha incorreta');
      return new Response(JSON.stringify({
        success: false,
        error: 'Email ou senha incorretos'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    console.log('[login] ✅ Senha correta!');
    
    console.log('[login] ✅ Autenticação bem-sucedida para:', email);
    
    // Atualizar status online
    await env.DB.prepare(
      'UPDATE users SET online_status = 1 WHERE id = ?'
    ).bind(user.id).run();
    
    console.log('[login] Status online atualizado');
    
    // Criar sessão no banco
    const sessionToken = crypto.randomUUID();
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 dias
    
    await env.DB.prepare(
      'INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)'
    ).bind(user.id, sessionToken, expiresAt.toISOString()).run();
    
    console.log('[login] Sessão criada, token:', sessionToken.substring(0, 8) + '...');
    
    // Criar cookie de sessão
    const sessionCookie = `session=${sessionToken}; HttpOnly; Path=/; SameSite=Lax; Expires=${expiresAt.toUTCString()}; ${
      new URL(request.url).protocol === 'https:' ? 'Secure;' : ''
    }`;
    
    // Remover dados sensíveis da resposta
    const { password_hash, ...userWithoutPassword } = user;
    
    console.log('[login] ✅ Login completo com sucesso para:', user.username);
    
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
        token: sessionToken,
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
    console.error('[login] ❌ Erro fatal:', error);
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
