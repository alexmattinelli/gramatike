// POST /api/auth/register - User registration

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../../src/types';
import { getUserByEmail, getUserByUsername, createUser } from '../../../src/lib/db';
import { hashPassword, generateToken } from '../../../src/lib/crypto';
import { createSession } from '../../../src/lib/db';
import { isValidEmail, isValidUsername, isValidPassword } from '../../../src/lib/validation';
import { errorResponse } from '../../../src/lib/response';
import { createSessionCookie } from '../../../src/lib/auth';

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  try {
    const body = await request.json() as { username: string; email: string; password: string; name?: string };
    const { username, email, password, name } = body;
    
    // Validate input
    if (!username || !email || !password) {
      return errorResponse('Usuário, email e senha são obrigatórios', 400);
    }
    
    if (!isValidUsername(username)) {
      return errorResponse('Usuário inválido (3-20 caracteres alfanuméricos)', 400);
    }
    
    if (!isValidEmail(email)) {
      return errorResponse('Email inválido', 400);
    }
    
    if (!isValidPassword(password)) {
      return errorResponse('Senha deve ter no mínimo 6 caracteres', 400);
    }
    
    // Check if user already exists
    const existingUser = await getUserByEmail(env.DB, email);
    if (existingUser) {
      return errorResponse('Email já cadastrado', 400);
    }
    
    const existingUsername = await getUserByUsername(env.DB, username);
    if (existingUsername) {
      return errorResponse('Usuário já existe', 400);
    }
    
    // Hash password
    const hashedPassword = await hashPassword(password);
    
    // Create user
    const user = await createUser(env.DB, {
      username,
      email,
      password: hashedPassword,
      name
    });
    
    // Create session
    const token = await generateToken();
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();
    await createSession(env.DB, user.id, token, expiresAt);
    
    // Remove password from response
    const { password: _, ...userWithoutPassword } = user;
    
    return new Response(JSON.stringify({
      success: true,
      user: userWithoutPassword
    }), {
      status: 201,
      headers: {
        'Content-Type': 'application/json',
        'Set-Cookie': createSessionCookie(token)
      }
    });
  } catch (error) {
    console.error('[register] Error:', error);
    console.error('[register] Stack:', error instanceof Error ? error.stack : 'N/A');
    
    // Erro específico se for banco não inicializado
    const errorMessage = error instanceof Error ? error.message : String(error);
    if (errorMessage && errorMessage.includes('no such table')) {
      return errorResponse('Erro: Banco de dados não inicializado. Execute: wrangler d1 execute gramatike --remote --file=./db/schema.sql', 500);
    }
    
    return errorResponse(`Erro ao criar conta: ${errorMessage || 'Erro desconhecido'}`, 500);
  }
};
