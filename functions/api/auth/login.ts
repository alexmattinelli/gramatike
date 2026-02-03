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
    // Verificar corpo da requisição
    const body = await request.json() as LoginRequest;
    const { email, password } = body;
    
    console.log('[login] Tentativa de login para email:', email);
    
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
    
    console.log('[login] Resultado da busca:', results ? `${results.length} usuário(s) encontrado(s)` : 'Nenhum resultado');
    
    if (!results || results.length === 0) {
      console.log('[login] ❌ Usuário não encontrado para email:', email);
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
    
    // Verificar senha usando PBKDF2
    // Use a função verifyPassword da crypto lib
    if (!user.password_hash) {
      console.log('[login] ❌ Usuário sem password_hash configurado');
      return new Response(JSON.stringify({
        success: false,
        error: 'Email ou senha incorretos'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    console.log('[login] Verificando senha com PBKDF2...');
    const isPasswordValid = await verifyPassword(password, user.password_hash);
    console.log('[login] Senha válida?', isPasswordValid);
    
    if (!isPasswordValid) {
      console.log('[login] ❌ Senha incorreta para:', email);
      return new Response(JSON.stringify({
        success: false,
        error: 'Email ou senha incorretos'
      }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
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
