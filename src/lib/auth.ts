// Authentication utilities
import type { Env, User, Session, AuthResult } from '../types';
import { getUserByEmail, getUserByUsername, getUserById, createUser } from './db';
import { hashPassword, verifyPassword, generateToken } from './crypto';
import { sanitizeParams } from './sanitize';

const SESSION_DURATION = 30 * 24 * 60 * 60 * 1000; // 30 days in milliseconds

/**
 * Register a new user
 */
export async function register(
  db: D1Database,
  username: string,
  email: string,
  password: string
): Promise<AuthResult> {
  // Validation
  if (!username || username.length < 3) {
    return { success: false, error: 'Nome de usuário deve ter no mínimo 3 caracteres' };
  }
  
  if (!email || !email.includes('@')) {
    return { success: false, error: 'Email inválido' };
  }
  
  if (!password || password.length < 8) {
    return { success: false, error: 'Senha deve ter no mínimo 8 caracteres' };
  }
  
  // Check if user already exists
  const existingEmail = await getUserByEmail(db, email);
  if (existingEmail) {
    return { success: false, error: 'Email já cadastrado' };
  }
  
  const existingUsername = await getUserByUsername(db, username);
  if (existingUsername) {
    return { success: false, error: 'Nome de usuário já cadastrado' };
  }
  
  // Hash password
  const passwordHash = await hashPassword(password);
  
  // Create user
  const userId = await createUser(db, username, email, passwordHash);
  
  if (!userId) {
    return { success: false, error: 'Erro ao criar usuário' };
  }
  
  // Get created user
  const user = await getUserById(db, userId);
  
  if (!user) {
    return { success: false, error: 'Erro ao buscar usuário criado' };
  }
  
  // Create session
  const token = await createSession(db, userId);
  
  return {
    success: true,
    user,
    token
  };
}

/**
 * Login a user
 */
export async function login(
  db: D1Database,
  emailOrUsername: string,
  password: string
): Promise<AuthResult> {
  // Find user by email or username
  let user = await getUserByEmail(db, emailOrUsername);
  
  if (!user) {
    user = await getUserByUsername(db, emailOrUsername);
  }
  
  if (!user) {
    return { success: false, error: 'Credenciais inválidas' };
  }
  
  // Check if user is banned
  if (user.is_banned) {
    return { success: false, error: 'Usuário banido' };
  }
  
  // Verify password
  const valid = await verifyPassword(password, user.password);
  
  if (!valid) {
    return { success: false, error: 'Credenciais inválidas' };
  }
  
  // Create session
  const token = await createSession(db, user.id);
  
  return {
    success: true,
    user,
    token
  };
}

/**
 * Create a session for a user
 */
export async function createSession(
  db: D1Database,
  userId: number,
  userAgent?: string,
  ipAddress?: string
): Promise<string> {
  const token = await generateToken(32);
  const expiresAt = new Date(Date.now() + SESSION_DURATION).toISOString();
  
  // Sanitize optional parameters
  const [sanitizedUserAgent, sanitizedIpAddress] = sanitizeParams(userAgent, ipAddress);
  
  console.log('[createSession] Creating session for user:', userId);
  
  await db.prepare(
    'INSERT INTO user_session (user_id, token, expires_at, user_agent, ip_address) VALUES (?, ?, ?, ?, ?)'
  )
    .bind(userId, token, expiresAt, sanitizedUserAgent, sanitizedIpAddress)
    .run();
  
  return token;
}

/**
 * Get session by token
 */
export async function getSession(
  db: D1Database,
  token: string
): Promise<Session | null> {
  const session = await db.prepare(
    'SELECT * FROM user_session WHERE token = ? AND expires_at > datetime("now")'
  )
    .bind(token)
    .first<Session>();
  
  return session;
}

/**
 * Delete a session (logout)
 */
export async function deleteSession(
  db: D1Database,
  token: string
): Promise<boolean> {
  try {
    await db.prepare('DELETE FROM user_session WHERE token = ?')
      .bind(token)
      .run();
    return true;
  } catch (error) {
    console.error('Error deleting session:', error);
    return false;
  }
}

/**
 * Get current user from request
 */
export async function getCurrentUser(
  request: Request,
  db: D1Database
): Promise<User | null> {
  // Get token from cookie
  const cookieHeader = request.headers.get('Cookie');
  if (!cookieHeader) {
    return null;
  }
  
  const token = cookieHeader
    .split(';')
    .map(c => c.trim())
    .find(c => c.startsWith('session='))
    ?.split('=')[1];
  
  if (!token) {
    return null;
  }
  
  // Get session
  const session = await getSession(db, token);
  if (!session) {
    return null;
  }
  
  // Get user
  const user = await getUserById(db, session.user_id);
  return user;
}

/**
 * Set session cookie
 */
export function setSessionCookie(token: string): string {
  const maxAge = SESSION_DURATION / 1000; // Convert to seconds
  return `session=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${maxAge}`;
}

/**
 * Clear session cookie
 */
export function clearSessionCookie(): string {
  return 'session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0';
}

/**
 * Check if user is admin
 */
export function isAdmin(user: User | null): boolean {
  if (!user) return false;
  return user.is_admin === 1 || user.is_superadmin === 1;
}

/**
 * Check if user is superadmin
 */
export function isSuperAdmin(user: User | null): boolean {
  if (!user) return false;
  return user.is_superadmin === 1;
}
