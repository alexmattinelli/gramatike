// Database query utilities for Gramátike v3 - Minimalist MVP

import type { User, Post, PostWithUser, Session } from '../types';

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
 * Get all users (admin only)
 */
export async function getAllUsers(db: D1Database): Promise<User[]> {
  const { results } = await db.prepare(
    'SELECT id, username, email, name, is_admin, is_banned, created_at FROM users ORDER BY created_at DESC'
  ).all();
  return results as unknown as User[];
}

/**
 * Ban a user
 */
export async function banUser(db: D1Database, userId: number): Promise<void> {
  await db.prepare('UPDATE users SET is_banned = 1 WHERE id = ?').bind(userId).run();
}

/**
 * Get posts with user info (simplified - no likes/comments)
 */
export async function getPosts(db: D1Database, limit = 20, offset = 0): Promise<PostWithUser[]> {
  const query = `
    SELECT p.*, u.username, u.name
    FROM posts p
    JOIN users u ON p.user_id = u.id
    ORDER BY p.created_at DESC
    LIMIT ? OFFSET ?
  `;
  
  const { results } = await db.prepare(query).bind(limit, offset).all();
  return results as unknown as PostWithUser[];
}

/**
 * Get post by ID
 */
export async function getPostById(db: D1Database, id: number): Promise<Post | null> {
  const { results } = await db.prepare('SELECT * FROM posts WHERE id = ?').bind(id).all();
  return (results[0] as unknown as Post) || null;
}

/**
 * Create a new post (text only)
 */
export async function createPost(db: D1Database, userId: number, content: string): Promise<Post> {
  const { results } = await db.prepare(
    'INSERT INTO posts (user_id, content) VALUES (?, ?) RETURNING *'
  ).bind(userId, content).all();
  return results[0] as unknown as Post;
}

/**
 * Delete a post
 */
export async function deletePost(db: D1Database, postId: number): Promise<void> {
  await db.prepare('DELETE FROM posts WHERE id = ?').bind(postId).run();
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

/**
 * Get database statistics (admin only)
 */
export async function getStats(db: D1Database): Promise<{ users: number; posts: number; banned: number }> {
  const usersResult = await db.prepare('SELECT COUNT(*) as count FROM users').first();
  const postsResult = await db.prepare('SELECT COUNT(*) as count FROM posts').first();
  const bannedResult = await db.prepare('SELECT COUNT(*) as count FROM users WHERE is_banned = 1').first();
  
  return {
    users: (usersResult?.count as number) || 0,
    posts: (postsResult?.count as number) || 0,
    banned: (bannedResult?.count as number) || 0
  };
}
