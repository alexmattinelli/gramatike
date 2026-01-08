// Authentication utilities for Gramátike v2

import type { Env, User, Session, AuthContext } from '../types';
import { getUserById, getSessionByToken } from './db';

/**
 * Get user from session cookie
 */
export async function getUserFromRequest(request: Request, env: Env): Promise<AuthContext> {
  const cookie = request.headers.get('Cookie');
  if (!cookie) return { user: null, session: null };
  
  const sessionToken = getCookieValue(cookie, 'session');
  if (!sessionToken) return { user: null, session: null };
  
  const session = await getSessionByToken(env.DB, sessionToken);
  if (!session) return { user: null, session: null };
  
  const user = await getUserById(env.DB, session.user_id);
  return { user, session };
}

/**
 * Extract cookie value by name
 */
function getCookieValue(cookie: string, name: string): string | null {
  const match = cookie.match(new RegExp(`(^|;\\s*)${name}=([^;]*)`));
  return match ? decodeURIComponent(match[2]) : null;
}

/**
 * Create session cookie header
 */
export function createSessionCookie(token: string, maxAge = 7 * 24 * 60 * 60): string {
  return `session=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${maxAge}; Secure`;
}

/**
 * Delete session cookie header
 */
export function deleteSessionCookie(): string {
  return 'session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0; Secure';
}

/**
 * Check if user is admin
 */
export function isAdmin(user: User | null): boolean {
  return user?.is_admin === 1;
}

/**
 * Check if user is banned
 */
export function isBanned(user: User | null): boolean {
  return user?.is_banned === 1;
}
