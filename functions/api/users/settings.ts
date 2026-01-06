// User Settings API
import type { Env, User } from '../../../src/types';
import { updateUser, getUserById } from '../../../src/lib/db';
import { hashPassword } from '../../../src/lib/crypto';
import { errorResponse, successResponse, parseJsonBody } from '../../../src/lib/utils';

/**
 * GET /api/users/settings - Get current user settings
 */
export const onRequestGet: PagesFunction<Env> = async ({ request, env, data }) => {
  const user = data.user as User;
  
  if (!user) {
    return errorResponse('Não autenticado', 401);
  }
  
  return successResponse({
    user: {
      id: user.id,
      username: user.username,
      email: user.email,
      nome: user.nome,
      foto_perfil: user.foto_perfil,
      bio: user.bio,
      genero: user.genero,
      pronome: user.pronome,
      data_nascimento: user.data_nascimento
    }
  });
};

/**
 * PATCH /api/users/settings - Update user settings
 */
export const onRequestPatch: PagesFunction<Env> = async ({ request, env, data }) => {
  const user = data.user as User;
  
  if (!user) {
    return errorResponse('Não autenticado', 401);
  }
  
  const body = await parseJsonBody<{
    nome?: string;
    bio?: string;
    genero?: string;
    pronome?: string;
    foto_perfil?: string;
  }>(request);
  
  if (!body) {
    return errorResponse('Dados inválidos', 400);
  }
  
  // Update user
  const success = await updateUser(env.DB, user.id, body);
  
  if (!success) {
    return errorResponse('Erro ao atualizar configurações', 500);
  }
  
  // Get updated user
  const updatedUser = await getUserById(env.DB, user.id);
  
  return successResponse(
    {
      user: {
        id: updatedUser!.id,
        username: updatedUser!.username,
        email: updatedUser!.email,
        nome: updatedUser!.nome,
        foto_perfil: updatedUser!.foto_perfil,
        bio: updatedUser!.bio,
        genero: updatedUser!.genero,
        pronome: updatedUser!.pronome
      }
    },
    'Configurações atualizadas com sucesso'
  );
};
