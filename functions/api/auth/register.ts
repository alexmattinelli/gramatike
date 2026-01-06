// Register endpoint
import type { Env } from '../../../src/types';
import { register, setSessionCookie } from '../../../src/lib/auth';
import { errorResponse, successResponse, parseJsonBody, isValidEmail } from '../../../src/lib/utils';

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  const body = await parseJsonBody<{
    username: string;
    email: string;
    password: string;
  }>(request);
  
  if (!body) {
    return errorResponse('Dados inválidos', 400);
  }
  
  const { username, email, password } = body;
  
  // Validation
  if (!username || !email || !password) {
    return errorResponse('Todos os campos são obrigatórios', 400);
  }
  
  if (!isValidEmail(email)) {
    return errorResponse('Email inválido', 400);
  }
  
  // Attempt registration
  const result = await register(env.DB, username, email, password);
  
  if (!result.success || !result.token) {
    return errorResponse(result.error || 'Erro ao criar conta', 400);
  }
  
  // Create response with session cookie
  const response = successResponse(
    {
      user: {
        id: result.user!.id,
        username: result.user!.username,
        email: result.user!.email,
        foto_perfil: result.user!.foto_perfil
      }
    },
    'Conta criada com sucesso',
    201
  );
  
  response.headers.set('Set-Cookie', setSessionCookie(result.token));
  
  return response;
};
