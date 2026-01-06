// Education Content by ID
import type { Env } from '../../../src/types';
import { getEduContentById } from '../../../src/lib/db';
import { errorResponse, successResponse } from '../../../src/lib/utils';

/**
 * GET /api/education/[id] - Get specific educational content
 */
export const onRequestGet: PagesFunction<Env> = async ({ request, env, params }) => {
  const id = parseInt(params.id as string);
  
  if (isNaN(id)) {
    return errorResponse('ID inválido', 400);
  }
  
  const content = await getEduContentById(env.DB, id);
  
  if (!content) {
    return errorResponse('Conteúdo não encontrado', 404);
  }
  
  return successResponse({ content });
};
