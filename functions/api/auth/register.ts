// functions/api/auth/register.ts
import type { PagesFunction } from '@cloudflare/workers-types';

interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  name?: string;
}

interface User {
  id: number;
  username: string;
  email: string;
  password_hash?: string;
  name?: string;
  avatar_initials: string;
  verified: boolean;
  online_status: boolean;
  role: string;
  created_at: string;
}

export const onRequestPost: PagesFunction<{ DB: any }> = async ({ request, env }) => {
  try {
    const body = await request.json() as RegisterRequest;
    let { username, email, password, name } = body;
    
    // Validações básicas
    if (!username || !email || !password) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Usuário, email e senha são obrigatórios'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Limpar e validar inputs
    username = username.trim();
    email = email.toLowerCase().trim();
    name = name?.trim();
    
    // Validação de username (3-20 caracteres alfanuméricos e underline)
    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
    if (!usernameRegex.test(username)) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Usuário inválido. Use 3-20 caracteres (letras, números e _)'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Validação de email
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
    
    // Validação de senha (mínimo 6 caracteres)
    if (password.length < 6) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Senha deve ter no mínimo 6 caracteres'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Verificar se email já existe
    const existingEmail = await env.DB.prepare(
      'SELECT id FROM users WHERE email = ? LIMIT 1'
    ).bind(email).first();
    
    if (existingEmail) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Email já cadastrado'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Verificar se username já existe
    const existingUsername = await env.DB.prepare(
      'SELECT id FROM users WHERE username = ? LIMIT 1'
    ).bind(username).first();
    
    if (existingUsername) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Nome de usuário já existe'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // IMPORTANTE: Em produção, use bcrypt ou Argon2!
    // Aqui estou armazenando a senha em texto simples APENAS para desenvolvimento
    const password_hash = password; // NÃO FAÇA ISSO EM PRODUÇÃO!
    
    // Gerar iniciais do avatar (primeira letra do username)
    const avatar_initials = username.charAt(0).toUpperCase();
    
    // Criar usuário no banco
    const { success, meta } = await env.DB.prepare(`
      INSERT INTO users (username, email, password_hash, name, avatar_initials, verified, online_status, role)
      VALUES (?, ?, ?, ?, ?, false, true, 'user')
    `).bind(username, email, password_hash, name || username, avatar_initials).run();
    
    if (!success) {
      throw new Error('Falha ao criar usuário no banco de dados');
    }
    
    // Buscar usuário criado
    const { results } = await env.DB.prepare(
      'SELECT * FROM users WHERE id = ?'
    ).bind(meta.last_row_id).all();
    
    const newUser = results[0] as User;
    
    // Criar sessão automática após registro
    const sessionId = crypto.randomUUID();
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 dias
    
    await env.DB.prepare(
      'INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)'
    ).bind(sessionId, newUser.id, expiresAt.toISOString()).run();
    
    // Criar cookie de sessão
    const sessionCookie = `session=${sessionId}; HttpOnly; Path=/; SameSite=Lax; Expires=${expiresAt.toUTCString()}; ${
      new URL(request.url).protocol === 'https:' ? 'Secure;' : ''
    }`;
    
    // Remover dados sensíveis da resposta
    const { password_hash: _, ...userWithoutPassword } = newUser;
    
    return new Response(JSON.stringify({
      success: true,
      message: 'Conta criada com sucesso!',
      user: {
        id: newUser.id,
        username: newUser.username,
        email: newUser.email,
        name: newUser.name,
        avatar_initials: newUser.avatar_initials,
        verified: newUser.verified,
        online_status: true,
        role: newUser.role,
        created_at: newUser.created_at
      }
    }), {
      status: 201,
      headers: {
        'Content-Type': 'application/json',
        'Set-Cookie': sessionCookie
      }
    });
    
  } catch (error) {
    console.error('[register] Error:', error);
    
    let errorMessage = 'Erro ao criar conta';
    
    // Verificar se é erro de tabela não existente
    if (error instanceof Error) {
      if (error.message.includes('no such table') || error.message.includes('does not exist')) {
        errorMessage = 'Banco de dados não configurado. Execute o setup primeiro.';
      } else {
        errorMessage = error.message;
      }
    }
    
    return new Response(JSON.stringify({
      success: false,
      error: errorMessage
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
