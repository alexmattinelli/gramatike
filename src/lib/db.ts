// Database helper functions for Cloudflare D1
import type { Env, User, Post, PostWithUser, Comment, EduContent, Divulgacao } from '../types';
import { sanitizeForD1, sanitizeParams } from './sanitize';

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
  // Sanitize parameters (username, email, passwordHash should not be undefined for new users)
  const [sanitizedUsername, sanitizedEmail, sanitizedPasswordHash] = sanitizeParams(
    username,
    email,
    passwordHash
  );
  
  // Validate required fields - use explicit null checks
  if (sanitizedUsername == null || sanitizedEmail == null || sanitizedPasswordHash == null) {
    console.error('[createUser] Missing required fields');
    return null;
  }
  
  // Validate non-empty strings (check for string type first)
  if (typeof sanitizedUsername !== 'string' || typeof sanitizedEmail !== 'string' || typeof sanitizedPasswordHash !== 'string') {
    console.error('[createUser] Invalid field types');
    return null;
  }
  
  if (!sanitizedUsername.trim() || !sanitizedEmail.trim() || !sanitizedPasswordHash.trim()) {
    console.error('[createUser] Required fields cannot be empty');
    return null;
  }
  
  try {
    console.log('[createUser] Creating user:', { username: sanitizedUsername, email: sanitizedEmail });
    
    const result = await db.prepare(
      'INSERT INTO user (username, email, password, created_at) VALUES (?, ?, ?, datetime("now")) RETURNING id'
    )
      .bind(sanitizedUsername, sanitizedEmail, sanitizedPasswordHash)
      .first<{ id: number }>();
    
    console.log('[createUser] User created successfully, id:', result?.id);
    return result?.id || null;
  } catch (error) {
    console.error('[createUser] Error:', error);
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
    
    // Sanitize each field before adding to query
    if (updates.nome !== undefined) {
      fields.push('nome = ?');
      values.push(sanitizeForD1(updates.nome));
    }
    if (updates.bio !== undefined) {
      fields.push('bio = ?');
      values.push(sanitizeForD1(updates.bio));
    }
    if (updates.foto_perfil !== undefined) {
      fields.push('foto_perfil = ?');
      values.push(sanitizeForD1(updates.foto_perfil));
    }
    if (updates.genero !== undefined) {
      fields.push('genero = ?');
      values.push(sanitizeForD1(updates.genero));
    }
    if (updates.pronome !== undefined) {
      fields.push('pronome = ?');
      values.push(sanitizeForD1(updates.pronome));
    }
    
    if (fields.length === 0) return false;
    
    values.push(userId);
    
    console.log('[updateUser] Updating user:', { userId, fields, valueCount: values.length });
    
    await db.prepare(
      `UPDATE user SET ${fields.join(', ')} WHERE id = ?`
    ).bind(...values).run();
    
    return true;
  } catch (error) {
    console.error('[updateUser] Error:', error);
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
  // CRITICAL: Sanitize ALL parameters before passing to D1
  const [sanitizedUserId, sanitizedUsername, sanitizedContent, sanitizedImage] = sanitizeParams(
    userId,
    username,
    content,
    image
  );
  
  // Validate required fields - use explicit null checks to allow 0 as valid userId
  if (sanitizedUserId == null || sanitizedUsername == null || sanitizedContent == null) {
    console.error('[createPost] Missing required fields after sanitization');
    return null;
  }
  
  // Validate non-empty strings for username and content (check type first)
  if (typeof sanitizedUsername !== 'string' || typeof sanitizedContent !== 'string') {
    console.error('[createPost] Invalid field types');
    return null;
  }
  
  if (!sanitizedUsername.trim() || !sanitizedContent.trim()) {
    console.error('[createPost] Username and content cannot be empty');
    return null;
  }
  
  try {
    console.log('[createPost] Creating post with sanitized values:', {
      userId: sanitizedUserId,
      username: sanitizedUsername,
      contentLength: sanitizedContent.length,
      hasImage: !!sanitizedImage
    });
    
    const result = await db.prepare(
      'INSERT INTO post (usuarie_id, usuarie, conteudo, imagem, data) VALUES (?, ?, ?, ?, datetime("now")) RETURNING id'
    )
      .bind(sanitizedUserId, sanitizedUsername, sanitizedContent, sanitizedImage)
      .first<{ id: number }>();
    
    console.log('[createPost] Post created successfully, id:', result?.id);
    return result?.id || null;
  } catch (error) {
    console.error('[createPost] Error:', error);
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
  // Sanitize parameters for consistency
  const [sanitizedPostId, sanitizedDeletedBy] = sanitizeParams(postId, deletedBy);
  
  if (sanitizedPostId == null || sanitizedDeletedBy == null) {
    console.error('[deletePost] Missing required parameters');
    return false;
  }
  
  try {
    await db.prepare(
      'UPDATE post SET is_deleted = 1, deleted_at = datetime("now"), deleted_by = ? WHERE id = ?'
    )
      .bind(sanitizedDeletedBy, sanitizedPostId)
      .run();
    
    return true;
  } catch (error) {
    console.error('[deletePost] Error:', error);
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
  // Sanitize parameters for consistency
  const [sanitizedPostId, sanitizedUserId] = sanitizeParams(postId, userId);
  
  if (sanitizedPostId == null || sanitizedUserId == null) {
    console.error('[likePost] Missing required parameters');
    return false;
  }
  
  try {
    await db.prepare(
      'INSERT OR IGNORE INTO post_likes (post_id, usuarie_id, created_at) VALUES (?, ?, datetime("now"))'
    )
      .bind(sanitizedPostId, sanitizedUserId)
      .run();
    
    return true;
  } catch (error) {
    console.error('[likePost] Error:', error);
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
  // Sanitize parameters for consistency
  const [sanitizedPostId, sanitizedUserId] = sanitizeParams(postId, userId);
  
  if (sanitizedPostId == null || sanitizedUserId == null) {
    console.error('[unlikePost] Missing required parameters');
    return false;
  }
  
  try {
    await db.prepare(
      'DELETE FROM post_likes WHERE post_id = ? AND usuarie_id = ?'
    )
      .bind(sanitizedPostId, sanitizedUserId)
      .run();
    
    return true;
  } catch (error) {
    console.error('[unlikePost] Error:', error);
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
  // Sanitize parameter for consistency
  const [sanitizedPostId] = sanitizeParams(postId);
  
  if (sanitizedPostId == null) {
    console.error('[getPostComments] Missing postId');
    return [];
  }
  
  const { results } = await db.prepare(`
    SELECT c.*, u.username, u.foto_perfil
    FROM comentario c
    LEFT JOIN user u ON c.usuarie_id = u.id
    WHERE c.post_id = ?
    ORDER BY c.data ASC
  `)
    .bind(sanitizedPostId)
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
  // Sanitize parameters
  const [sanitizedPostId, sanitizedUserId, sanitizedContent, sanitizedParentId] = sanitizeParams(
    postId,
    userId,
    content,
    parentId
  );
  
  // Validate required fields - use explicit null checks to allow 0 as valid ID
  if (sanitizedPostId == null || sanitizedUserId == null || sanitizedContent == null) {
    console.error('[createComment] Missing required fields');
    return null;
  }
  
  // Validate non-empty content (check type first)
  if (typeof sanitizedContent !== 'string') {
    console.error('[createComment] Invalid content type');
    return null;
  }
  
  if (!sanitizedContent.trim()) {
    console.error('[createComment] Content cannot be empty');
    return null;
  }
  
  try {
    console.log('[createComment] Creating comment:', {
      postId: sanitizedPostId,
      userId: sanitizedUserId,
      hasParent: !!sanitizedParentId
    });
    
    const result = await db.prepare(
      'INSERT INTO comentario (post_id, usuarie_id, conteudo, data, parent_id) VALUES (?, ?, ?, datetime("now"), ?) RETURNING id'
    )
      .bind(sanitizedPostId, sanitizedUserId, sanitizedContent, sanitizedParentId)
      .first<{ id: number }>();
    
    console.log('[createComment] Comment created successfully, id:', result?.id);
    return result?.id || null;
  } catch (error) {
    console.error('[createComment] Error:', error);
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
  // Sanitize all parameters
  const [
    sanitizedTipo,
    sanitizedTitulo,
    sanitizedConteudo,
    sanitizedResumo,
    sanitizedImagem,
    sanitizedArquivoUrl,
    sanitizedLink,
    sanitizedAutorId,
    sanitizedTemaId
  ] = sanitizeParams(tipo, titulo, conteudo, resumo, imagem, arquivo_url, link, autor_id, tema_id);
  
  // Validate required fields
  if (sanitizedTipo == null || sanitizedTitulo == null) {
    console.error('[createEduContent] Missing required fields');
    return null;
  }
  
  // Validate non-empty strings (check type first)
  if (typeof sanitizedTipo !== 'string' || typeof sanitizedTitulo !== 'string') {
    console.error('[createEduContent] Invalid field types');
    return null;
  }
  
  if (!sanitizedTipo.trim() || !sanitizedTitulo.trim()) {
    console.error('[createEduContent] Required fields cannot be empty');
    return null;
  }
  
  try {
    console.log('[createEduContent] Creating educational content:', {
      tipo: sanitizedTipo,
      titulo: sanitizedTitulo
    });
    
    const result = await db.prepare(
      `INSERT INTO edu_content (tipo, titulo, conteudo, resumo, imagem, arquivo_url, link, autor_id, tema_id, data)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime("now")) RETURNING id`
    )
      .bind(
        sanitizedTipo,
        sanitizedTitulo,
        sanitizedConteudo,
        sanitizedResumo,
        sanitizedImagem,
        sanitizedArquivoUrl,
        sanitizedLink,
        sanitizedAutorId,
        sanitizedTemaId
      )
      .first<{ id: number }>();
    
    console.log('[createEduContent] Content created successfully, id:', result?.id);
    return result?.id || null;
  } catch (error) {
    console.error('[createEduContent] Error:', error);
    return null;
  }
}

/**
 * Get divulgacoes (announcements/news)
 */
export async function getDivulgacoes(
  db: D1Database,
  limit = 5
): Promise<Divulgacao[]> {
  const { results } = await db.prepare(`
    SELECT * FROM divulgacao
    WHERE ativo = 1
    ORDER BY created_at DESC
    LIMIT ?
  `).bind(limit).all<Divulgacao>();
  
  return results || [];
}
