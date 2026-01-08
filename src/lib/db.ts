// Database query utilities for Gramátike v2

import type { User, Post, Comment, Session } from '../types';

/**
 * Get user by ID
 */
export async function getUserById(db: D1Database, id: number): Promise<User | null> {
  const { results } = await db.prepare('SELECT * FROM users WHERE id = ?').bind(id).all();
  return (results[0] as unknown as User) || null;
}

/**
 * Get user by username
 */
export async function getUserByUsername(db: D1Database, username: string): Promise<User | null> {
  const { results } = await db.prepare('SELECT * FROM users WHERE username = ?').bind(username).all();
  return (results[0] as unknown as User) || null;
}

/**
 * Get user by email
 */
export async function getUserByEmail(db: D1Database, email: string): Promise<User | null> {
  const { results } = await db.prepare('SELECT * FROM users WHERE email = ?').bind(email).all();
  return (results[0] as unknown as User) || null;
}

/**
 * Create a new user
 */
export async function createUser(db: D1Database, data: {
  username: string;
  email: string;
  password: string;
  name?: string;
}): Promise<User> {
  const { results } = await db.prepare(
    'INSERT INTO users (username, email, password, name) VALUES (?, ?, ?, ?) RETURNING *'
  ).bind(data.username, data.email, data.password, data.name || null).all();
  return results[0] as unknown as User;
}

/**
 * Get posts with user info
 */
export async function getPosts(db: D1Database, limit = 20, offset = 0, userId?: number): Promise<Post[]> {
  let query = `
    SELECT p.*, u.username, u.name, u.avatar,
           COUNT(DISTINCT l.id) as likes_count,
           COUNT(DISTINCT c.id) as comments_count
           ${userId ? `, EXISTS(SELECT 1 FROM likes WHERE user_id = ? AND post_id = p.id) as user_liked` : ''}
    FROM posts p
    JOIN users u ON p.user_id = u.id
    LEFT JOIN likes l ON p.id = l.post_id
    LEFT JOIN comments c ON p.id = c.post_id
    GROUP BY p.id
    ORDER BY p.created_at DESC
    LIMIT ? OFFSET ?
  `;
  
  const bindings = userId ? [userId, limit, offset] : [limit, offset];
  const { results } = await db.prepare(query).bind(...bindings).all();
  return results as unknown as Post[];
}

/**
 * Create a new post
 */
export async function createPost(db: D1Database, userId: number, content: string, image?: string): Promise<Post> {
  const { results } = await db.prepare(
    'INSERT INTO posts (user_id, content, image) VALUES (?, ?, ?) RETURNING *'
  ).bind(userId, content, image || null).all();
  return results[0] as unknown as Post;
}

/**
 * Toggle like on a post
 */
export async function toggleLike(db: D1Database, userId: number, postId: number): Promise<boolean> {
  const { results } = await db.prepare(
    'SELECT * FROM likes WHERE user_id = ? AND post_id = ?'
  ).bind(userId, postId).all();
  
  if (results.length > 0) {
    await db.prepare('DELETE FROM likes WHERE user_id = ? AND post_id = ?').bind(userId, postId).run();
    return false;
  } else {
    await db.prepare('INSERT INTO likes (user_id, post_id) VALUES (?, ?)').bind(userId, postId).run();
    return true;
  }
}

/**
 * Create a session
 */
export async function createSession(db: D1Database, userId: number, token: string, expiresAt: string): Promise<Session> {
  const { results } = await db.prepare(
    'INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?) RETURNING *'
  ).bind(userId, token, expiresAt).all();
  return results[0] as unknown as Session;
}

/**
 * Get session by token
 */
export async function getSessionByToken(db: D1Database, token: string): Promise<Session | null> {
  const { results } = await db.prepare(
    "SELECT * FROM sessions WHERE token = ? AND expires_at > datetime('now')"
  ).bind(token).all();
  return (results[0] as unknown as Session) || null;
}

/**
 * Delete session
 */
export async function deleteSession(db: D1Database, token: string): Promise<void> {
  await db.prepare('DELETE FROM sessions WHERE token = ?').bind(token).run();
}
