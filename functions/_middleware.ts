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

// Define which page routes are public (allow viewing without auth)
const PUBLIC_PAGE_ROUTES = [
  '/pages',
  '/', // Root/feed page
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
  
  // Allow public API routes
  const isPublic = PUBLIC_ROUTES.some(route => path.startsWith(route));
  
  // Allow public page routes for GET requests
  const isPublicPage = PUBLIC_PAGE_ROUTES.some(route => 
    route === '/' ? path === '/' : path.startsWith(route)
  );
  
  if ((isPublic || isPublicPage) && request.method === 'GET') {
    // Still try to get user for personalized content, but don't require it
    const user = await getCurrentUser(request, env.DB);
    data.user = user;
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
