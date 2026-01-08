// Global authentication middleware for Gramátike v2

import type { PagesFunction, EventContext } from '@cloudflare/workers-types';
import type { Env, AuthContext } from '../src/types';
import { getUserFromRequest } from '../src/lib/auth';

export const onRequest: PagesFunction<Env> = async (context) => {
  const { request, env, next } = context;
  
  // Get user from session
  const authContext = await getUserFromRequest(request, env);
  
  // Attach user to context data for use in route handlers
  context.data.user = authContext.user;
  context.data.session = authContext.session;
  
  // Continue to next handler
  return next();
};
