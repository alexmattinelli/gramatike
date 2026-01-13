// functions/api/auth/register.ts (VERSÃO FINAL)
import type { PagesFunction } from '@cloudflare/workers-types';

interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  name?: string;
}

export const onRequestPost: PagesFunction<{ DB: any }> = async ({ request, env }) => {
  try {
    // 1. Obter e validar dados
    const body = await request.json() as RegisterRequest;
    let { username, email, password, name } = body;
    
    if (!username || !email || !password) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Usuário, email e senha são obrigatórios'
      }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Limpar dados
    username = username.trim();
    email = email.toLowerCase().trim();
    name = name?.trim();
    
    // Validações
    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
    if (!usernameRegex.test(username)) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Usuário inválido (3-20 letras, números ou _)'
      }), { status: 400 });
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Email inválido'
      }), { status: 400 });
    }
    
    if (password.length < 6) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Senha deve ter no mínimo 6 caracteres'
      }), { status: 400 });
    }
    
    // 2. Verificar duplicatas
    const existingEmail = await env.DB.prepare(
      'SELECT id FROM users WHERE email = ?'
    ).bind(email).first();
    
    if (existingEmail) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Email já cadastrado'
      }), { status: 400 });
    }
    
    const existingUsername = await env.DB.prepare(
      'SELECT id FROM users WHERE username = ?'
    ).bind(username).first();
    
    if (existingUsername) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Nome de usuário já existe'
      }), { status: 400 });
    }
    
    // 3. Criar usuário (COM password_hash)
    const avatar_initials = username.charAt(0).toUpperCase();
    
    // IMPORTANTE: Em produção use bcrypt! Aqui salva em texto simples para dev
    const password_hash = password; // ⚠️ NÃO FAÇA ISSO EM PRODUÇÃO!
    
    const { success, meta } = await env.DB.prepare(`
      INSERT INTO users (
        username, email, name, avatar_initials, 
        password_hash, verified, online_status, role
      ) VALUES (?, ?, ?, ?, ?, false, true, 'user')
    `).bind(
      username, 
      email, 
      name || username, 
      avatar_initials,
      password_hash
    ).run();
    
    if (!success) {
      throw new Error('Falha ao inserir usuário no banco');
    }
    
    // 4. Buscar usuário criado
    const { results } = await env.DB.prepare(
      `SELECT id, username, email, name, avatar_initials, 
              verified, online_status, role, created_at 
       FROM users WHERE id = ?`
    ).bind(meta.last_row_id).all();
    
    const newUser = results[0];
    
    // 5. Criar sessão automática
    const sessionId = crypto.randomUUID();
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 dias
    
    await env.DB.prepare(
      'INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)'
    ).bind(sessionId, newUser.id, expiresAt.toISOString()).run();
    
    // 6. Cookie de sessão
    const sessionCookie = `session=${sessionId}; HttpOnly; Path=/; SameSite=Lax; Expires=${expiresAt.toUTCString()}`;
    
    // 7. Retornar resposta
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
    
  } catch (error: any) {
    console.error('[register] ERRO DETALHADO:', error);
    
    // Verificar erro específico
    let errorMessage = 'Erro ao criar conta';
    
    if (error.message) {
      if (error.message.includes('password_hash')) {
        errorMessage = 'Erro na coluna password_hash. Execute /setup novamente.';
      } else if (error.message.includes('UNIQUE constraint failed')) {
        if (error.message.includes('username')) {
          errorMessage = 'Nome de usuário já existe';
        } else if (error.message.includes('email')) {
          errorMessage = 'Email já cadastrado';
        }
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
