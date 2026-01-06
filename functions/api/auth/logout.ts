// Logout endpoint
import type { Env } from '../../../src/types';
import { deleteSession, clearSessionCookie } from '../../../src/lib/auth';
import { successResponse, errorResponse } from '../../../src/lib/utils';

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  // Get token from cookie
  const cookieHeader = request.headers.get('Cookie');
  
  if (!cookieHeader) {
    return errorResponse('Não autenticado', 401);
  }
  
  const token = cookieHeader
    .split(';')
    .map(c => c.trim())
    .find(c => c.startsWith('session='))
    ?.split('=')[1];
  
  if (!token) {
    return errorResponse('Não autenticado', 401);
  }
  
  // Delete session from database
  await deleteSession(env.DB, token);
  
  // Create response with cleared cookie
  const response = successResponse({}, 'Logout realizado com sucesso');
  response.headers.set('Set-Cookie', clearSessionCookie());
  
  return response;
};
