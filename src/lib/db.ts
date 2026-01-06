// Database helper functions for Cloudflare D1
import type { Env, User, Post, PostWithUser, Comment, EduContent } from '../types';

/**
 * Get user by email
 */
export async function getUserByEmail(db: D1Database, email: string): Promise<User | null> {
  const result = await db.prepare('SELECT * FROM user WHERE email = ?')
    .bind(email)
    .first<User>();
  return result;
}

/**
 * Get user by username
 */
export async function getUserByUsername(db: D1Database, username: string): Promise<User | null> {
  const result = await db.prepare('SELECT * FROM user WHERE username = ?')
    .bind(username)
    .first<User>();
  return result;
}

/**
 * Get user by ID
 */
export async function getUserById(db: D1Database, userId: number): Promise<User | null> {
  const result = await db.prepare('SELECT * FROM user WHERE id = ?')
    .bind(userId)
    .first<User>();
  return result;
}

/**
 * Create a new user
 */
export async function createUser(
  db: D1Database,
  username: string,
  email: string,
  passwordHash: string
): Promise<number | null> {
  try {
    const result = await db.prepare(
      'INSERT INTO user (username, email, password, created_at) VALUES (?, ?, ?, datetime("now")) RETURNING id'
    )
      .bind(username, email, passwordHash)
      .first<{ id: number }>();
    
    return result?.id || null;
  } catch (error) {
    console.error('Error creating user:', error);
    return null;
  }
}

/**
 * Update user profile
 */
export async function updateUser(
  db: D1Database,
  userId: number,
  updates: Partial<User>
): Promise<boolean> {
  try {
    const fields: string[] = [];
    const values: any[] = [];
    
    if (updates.nome !== undefined) {
      fields.push('nome = ?');
      values.push(updates.nome);
    }
    if (updates.bio !== undefined) {
      fields.push('bio = ?');
      values.push(updates.bio);
    }
    if (updates.foto_perfil !== undefined) {
      fields.push('foto_perfil = ?');
      values.push(updates.foto_perfil);
    }
    if (updates.genero !== undefined) {
      fields.push('genero = ?');
      values.push(updates.genero);
    }
    if (updates.pronome !== undefined) {
      fields.push('pronome = ?');
      values.push(updates.pronome);
    }
    
    if (fields.length === 0) return false;
    
    values.push(userId);
    
    await db.prepare(
      `UPDATE user SET ${fields.join(', ')} WHERE id = ?`
    ).bind(...values).run();
    
    return true;
  } catch (error) {
    console.error('Error updating user:', error);
    return false;
  }
}

/**
 * Get posts with user information and counts
 */
export async function getPosts(
  db: D1Database,
  page = 1,
  perPage = 20,
  userId?: number
): Promise<PostWithUser[]> {
  const offset = (page - 1) * perPage;
  
  let query = `
    SELECT 
      p.*,
      u.username,
      u.foto_perfil,
      COUNT(DISTINCT pl.usuarie_id) as like_count,
      COUNT(DISTINCT c.id) as comment_count
      ${userId ? ', EXISTS(SELECT 1 FROM post_likes WHERE post_id = p.id AND usuarie_id = ?) as user_liked' : ''}
    FROM post p
    LEFT JOIN user u ON p.usuarie_id = u.id
    LEFT JOIN post_likes pl ON p.id = pl.post_id
    LEFT JOIN comentario c ON p.id = c.post_id
    WHERE p.is_deleted = 0
    GROUP BY p.id
    ORDER BY p.data DESC
    LIMIT ? OFFSET ?
  `;
  
  const bindings = userId ? [userId, perPage, offset] : [perPage, offset];
  
  const { results } = await db.prepare(query).bind(...bindings).all<PostWithUser>();
  return results || [];
}

/**
 * Get a single post by ID
 */
export async function getPostById(
  db: D1Database,
  postId: number,
  userId?: number
): Promise<PostWithUser | null> {
  let query = `
    SELECT 
      p.*,
      u.username,
      u.foto_perfil,
      COUNT(DISTINCT pl.usuarie_id) as like_count,
      COUNT(DISTINCT c.id) as comment_count
      ${userId ? ', EXISTS(SELECT 1 FROM post_likes WHERE post_id = p.id AND usuarie_id = ?) as user_liked' : ''}
    FROM post p
    LEFT JOIN user u ON p.usuarie_id = u.id
    LEFT JOIN post_likes pl ON p.id = pl.post_id
    LEFT JOIN comentario c ON p.id = c.post_id
    WHERE p.id = ? AND p.is_deleted = 0
    GROUP BY p.id
  `;
  
  const bindings = userId ? [userId, postId] : [postId];
  const result = await db.prepare(query).bind(...bindings).first<PostWithUser>();
  return result;
}

/**
 * Create a new post
 */
export async function createPost(
  db: D1Database,
  userId: number,
  username: string,
  content: string,
  image?: string
): Promise<number | null> {
  try {
    const result = await db.prepare(
      'INSERT INTO post (usuarie_id, usuarie, conteudo, imagem, data) VALUES (?, ?, ?, ?, datetime("now")) RETURNING id'
    )
      .bind(userId, username, content, image || null)
      .first<{ id: number }>();
    
    return result?.id || null;
  } catch (error) {
    console.error('Error creating post:', error);
    return null;
  }
}

/**
 * Delete a post (soft delete)
 */
export async function deletePost(
  db: D1Database,
  postId: number,
  deletedBy: number
): Promise<boolean> {
  try {
    await db.prepare(
      'UPDATE post SET is_deleted = 1, deleted_at = datetime("now"), deleted_by = ? WHERE id = ?'
    )
      .bind(deletedBy, postId)
      .run();
    
    return true;
  } catch (error) {
    console.error('Error deleting post:', error);
    return false;
  }
}

/**
 * Like a post
 */
export async function likePost(
  db: D1Database,
  postId: number,
  userId: number
): Promise<boolean> {
  try {
    await db.prepare(
      'INSERT OR IGNORE INTO post_likes (post_id, usuarie_id, created_at) VALUES (?, ?, datetime("now"))'
    )
      .bind(postId, userId)
      .run();
    
    return true;
  } catch (error) {
    console.error('Error liking post:', error);
    return false;
  }
}

/**
 * Unlike a post
 */
export async function unlikePost(
  db: D1Database,
  postId: number,
  userId: number
): Promise<boolean> {
  try {
    await db.prepare(
      'DELETE FROM post_likes WHERE post_id = ? AND usuarie_id = ?'
    )
      .bind(postId, userId)
      .run();
    
    return true;
  } catch (error) {
    console.error('Error unliking post:', error);
    return false;
  }
}

/**
 * Get comments for a post
 */
export async function getPostComments(
  db: D1Database,
  postId: number
): Promise<Comment[]> {
  const { results } = await db.prepare(`
    SELECT c.*, u.username, u.foto_perfil
    FROM comentario c
    LEFT JOIN user u ON c.usuarie_id = u.id
    WHERE c.post_id = ?
    ORDER BY c.data ASC
  `)
    .bind(postId)
    .all<Comment>();
  
  return results || [];
}

/**
 * Create a comment
 */
export async function createComment(
  db: D1Database,
  postId: number,
  userId: number,
  content: string,
  parentId?: number
): Promise<number | null> {
  try {
    const result = await db.prepare(
      'INSERT INTO comentario (post_id, usuarie_id, conteudo, data, parent_id) VALUES (?, ?, ?, datetime("now"), ?) RETURNING id'
    )
      .bind(postId, userId, content, parentId || null)
      .first<{ id: number }>();
    
    return result?.id || null;
  } catch (error) {
    console.error('Error creating comment:', error);
    return null;
  }
}

/**
 * Get educational content by type
 */
export async function getEduContent(
  db: D1Database,
  tipo?: string,
  page = 1,
  perPage = 20
): Promise<EduContent[]> {
  const offset = (page - 1) * perPage;
  
  let query = `
    SELECT * FROM edu_content
    WHERE is_deleted = 0
    ${tipo ? 'AND tipo = ?' : ''}
    ORDER BY data DESC
    LIMIT ? OFFSET ?
  `;
  
  const bindings = tipo ? [tipo, perPage, offset] : [perPage, offset];
  
  const { results } = await db.prepare(query).bind(...bindings).all<EduContent>();
  return results || [];
}

/**
 * Get educational content by ID
 */
export async function getEduContentById(
  db: D1Database,
  id: number
): Promise<EduContent | null> {
  const result = await db.prepare(
    'SELECT * FROM edu_content WHERE id = ? AND is_deleted = 0'
  )
    .bind(id)
    .first<EduContent>();
  
  return result;
}

/**
 * Create educational content
 */
export async function createEduContent(
  db: D1Database,
  tipo: string,
  titulo: string,
  conteudo?: string,
  resumo?: string,
  imagem?: string,
  arquivo_url?: string,
  link?: string,
  autor_id?: number,
  tema_id?: number
): Promise<number | null> {
  try {
    const result = await db.prepare(
      `INSERT INTO edu_content (tipo, titulo, conteudo, resumo, imagem, arquivo_url, link, autor_id, tema_id, data)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime("now")) RETURNING id`
    )
      .bind(tipo, titulo, conteudo || null, resumo || null, imagem || null, 
            arquivo_url || null, link || null, autor_id || null, tema_id || null)
      .first<{ id: number }>();
    
    return result?.id || null;
  } catch (error) {
    console.error('Error creating edu content:', error);
    return null;
  }
}
