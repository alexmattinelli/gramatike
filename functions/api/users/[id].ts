// User Profile API
import type { Env, User } from '../../../src/types';
import { getUserById, getUserByUsername, getPosts } from '../../../src/lib/db';
import { errorResponse, successResponse } from '../../../src/lib/utils';

/**
 * GET /api/users/[id] - Get user profile
 */
export const onRequestGet: PagesFunction<Env> = async ({ request, env, params }) => {
  const identifier = params.id as string;
  
  let user: User | null = null;
  
  // Try to parse as ID first
  const userId = parseInt(identifier);
  if (!isNaN(userId)) {
    user = await getUserById(env.DB, userId);
  } else {
    // Otherwise treat as username
    user = await getUserByUsername(env.DB, identifier);
  }
  
  if (!user) {
    return errorResponse('Usuário não encontrado', 404);
  }
  
  // Get user's posts
  const posts = await getPosts(env.DB, 1, 10, user.id);
  
  // Return public user info (don't expose password hash)
  return successResponse({
    user: {
      id: user.id,
      username: user.username,
      nome: user.nome,
      foto_perfil: user.foto_perfil,
      bio: user.bio,
      genero: user.genero,
      pronome: user.pronome,
      created_at: user.created_at,
      is_admin: user.is_admin
    },
    posts
  });
};
