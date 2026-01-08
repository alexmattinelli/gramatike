// POST /api/auth/login - User login

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../../src/types';
import { getUserByEmail } from '../../../src/lib/db';
import { verifyPassword, generateToken } from '../../../src/lib/crypto';
import { createSession } from '../../../src/lib/db';
import { isValidEmail } from '../../../src/lib/validation';
import { jsonResponse, errorResponse } from '../../../src/lib/response';
import { createSessionCookie, isBanned } from '../../../src/lib/auth';

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  try {
    const { email, password } = await request.json();
    
    // Validate input
    if (!email || !password) {
      return errorResponse('Email e senha são obrigatórios', 400);
    }
    
    if (!isValidEmail(email)) {
      return errorResponse('Email inválido', 400);
    }
    
    // Get user by email
    const user = await getUserByEmail(env.DB, email);
    if (!user) {
      return errorResponse('Email ou senha incorretos', 401);
    }
    
    // Check if user is banned
    if (isBanned(user)) {
      return errorResponse('Usuário banido', 403);
    }
    
    // Verify password
    const isValid = await verifyPassword(password, user.password);
    if (!isValid) {
      return errorResponse('Email ou senha incorretos', 401);
    }
    
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
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Set-Cookie': createSessionCookie(token)
      }
    });
  } catch (error) {
    console.error('[login] Error:', error);
    return errorResponse('Erro ao fazer login', 500);
  }
};
