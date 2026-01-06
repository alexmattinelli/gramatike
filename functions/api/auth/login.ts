// Login endpoint
import type { Env } from '../../../src/types';
import { login, setSessionCookie } from '../../../src/lib/auth';
import { errorResponse, successResponse, parseJsonBody, getClientIp, getUserAgent } from '../../../src/lib/utils';

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  const body = await parseJsonBody<{ email: string; password: string }>(request);
  
  if (!body) {
    return errorResponse('Dados inválidos', 400);
  }
  
  const { email, password } = body;
  
  if (!email || !password) {
    return errorResponse('Email e senha são obrigatórios', 400);
  }
  
  // Attempt login
  const result = await login(env.DB, email, password);
  
  if (!result.success || !result.token) {
    return errorResponse(result.error || 'Erro ao fazer login', 401);
  }
  
  // Create response with session cookie
  const response = successResponse(
    {
      user: {
        id: result.user!.id,
        username: result.user!.username,
        email: result.user!.email,
        foto_perfil: result.user!.foto_perfil,
        is_admin: result.user!.is_admin,
        is_superadmin: result.user!.is_superadmin
      }
    },
    'Login realizado com sucesso'
  );
  
  response.headers.set('Set-Cookie', setSessionCookie(result.token));
  
  return response;
};
