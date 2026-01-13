// functions/api/auth/register.ts (VERSÃO SEM password_hash)
import type { PagesFunction } from '@cloudflare/workers-types';

interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  name?: string;
}

export const onRequestPost: PagesFunction<{ DB: any }> = async ({ request, env }) => {
  try {
    const body = await request.json() as RegisterRequest;
    let { username, email, password, name } = body;
    
    // Validações básicas (igual antes)
    if (!username || !email || !password) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Usuário, email e senha são obrigatórios'
      }), { status: 400 });
    }
    
    username = username.trim();
    email = email.toLowerCase().trim();
    name = name?.trim();
    
    // Validação de username
    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
    if (!usernameRegex.test(username)) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Usuário inválido. Use 3-20 caracteres (letras, números e _)'
      }), { status: 400 });
    }
    
    // Validação de email
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
    
    // Verificar duplicatas
    const existingEmail = await env.DB.prepare(
      'SELECT id FROM users WHERE email = ? LIMIT 1'
    ).bind(email).first();
    
    if (existingEmail) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Email já cadastrado'
      }), { status: 400 });
    }
    
    const existingUsername = await env.DB.prepare(
      'SELECT id FROM users WHERE username = ? LIMIT 1'
    ).bind(username).first();
    
    if (existingUsername) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Nome de usuário já existe'
      }), { status: 400 });
    }
    
    // *** MUDANÇA AQUI: Não usar password_hash ainda ***
    // Para desenvolvimento, podemos salvar em outra coluna ou ignorar
    const avatar_initials = username.charAt(0).toUpperCase();
    
    // TENTAR inserir SEM password_hash primeiro
    try {
      const { success, meta } = await env.DB.prepare(`
        INSERT INTO users (username, email, name, avatar_initials, verified, online_status, role)
        VALUES (?, ?, ?, ?, false, true, 'user')
      `).bind(username, email, name || username, avatar_initials).run();
      
      if (!success) {
        throw new Error('Falha ao criar usuário');
      }
      
      // Buscar usuário criado
      const { results } = await env.DB.prepare(
        'SELECT * FROM users WHERE id = ?'
      ).bind(meta.last_row_id).all();
      
      const newUser = results[0];
      
      // Criar sessão
      const sessionId = crypto.randomUUID();
      const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
      
      await env.DB.prepare(
        'INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)'
      ).bind(sessionId, newUser.id, expiresAt.toISOString()).run();
      
      // Cookie
      const sessionCookie = `session=${sessionId}; HttpOnly; Path=/; SameSite=Lax; Expires=${expiresAt.toUTCString()}`;
      
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
      
    } catch (dbError: any) {
      // Se falhar porque não tem coluna password_hash, tente sem
      if (dbError.message && dbError.message.includes('password_hash')) {
        // Adicionar a coluna e tentar novamente
        await env.DB.prepare(`
          ALTER TABLE users 
          ADD COLUMN password_hash TEXT
        `).run();
        
        // Agora tentar com password_hash (simplificado)
        const { success, meta } = await env.DB.prepare(`
          INSERT INTO users (username, email, name, avatar_initials, password_hash, verified, online_status, role)
          VALUES (?, ?, ?, ?, ?, false, true, 'user')
        `).bind(username, email, name || username, avatar_initials, password).run();
        
        if (!success) throw new Error('Falha após adicionar coluna');
        
        // ... resto do código igual acima
        const { results } = await env.DB.prepare(
          'SELECT * FROM users WHERE id = ?'
        ).bind(meta.last_row_id).all();
        
        const newUser = results[0];
        
        // Criar sessão
        const sessionId = crypto.randomUUID();
        const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
        
        await env.DB.prepare(
          'INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)'
        ).bind(sessionId, newUser.id, expiresAt.toISOString()).run();
        
        const sessionCookie = `session=${sessionId}; HttpOnly; Path=/; SameSite=Lax; Expires=${expiresAt.toUTCString()}`;
        
        return new Response(JSON.stringify({
          success: true,
          message: 'Conta criada com sucesso! (coluna password_hash adicionada)',
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
      }
      
      throw dbError;
    }
    
  } catch (error: any) {
    console.error('[register] Error:', error);
    
    let errorMessage = 'Erro ao criar conta';
    if (error.message) {
      if (error.message.includes('no such table')) {
        errorMessage = 'Tabela users não existe. Execute /setup primeiro.';
      } else if (error.message.includes('password_hash')) {
        errorMessage = 'Problema na estrutura do banco. Execute /setup para corrigir.';
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
