// Authentication middleware for Cloudflare Pages Functions
import type { Env, User } from '../src/types';
import { getCurrentUser } from '../src/lib/auth';
import { errorResponse } from '../src/lib/utils';

// Define which routes are public (don't require authentication)
const PUBLIC_ROUTES = [
  '/api/auth/login',
  '/api/auth/register',
  '/api/health',
  '/api/posts', // Allow viewing posts without auth (GET only)
];

// Define which routes require admin access
const ADMIN_ROUTES = [
  '/api/admin/',
  '/api/education/create',
  '/api/education/update',
  '/api/education/delete',
];

export const onRequest: PagesFunction<Env> = async (context) => {
  const { request, next, env, data } = context;
  const url = new URL(request.url);
  const path = url.pathname;
  
  // Allow public routes
  const isPublic = PUBLIC_ROUTES.some(route => path.startsWith(route));
  
  if (isPublic && request.method === 'GET') {
    return next();
  }
  
  // For non-public routes, check authentication
  const user = await getCurrentUser(request, env.DB);
  
  if (!user) {
    return errorResponse('Não autenticado', 401);
  }
  
  // Check if user is banned
  if (user.is_banned) {
    return errorResponse('Usuário banido', 403);
  }
  
  // Check admin routes
  const requiresAdmin = ADMIN_ROUTES.some(route => path.startsWith(route));
  
  if (requiresAdmin) {
    const isAdmin = user.is_admin === 1 || user.is_superadmin === 1;
    if (!isAdmin) {
      return errorResponse('Acesso negado', 403);
    }
  }
  
  // Add user to context data for use in route handlers
  data.user = user;
  
  return next();
};
