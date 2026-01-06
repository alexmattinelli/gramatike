// Education Content Creation (Admin only)
import type { Env, User } from '../../../src/types';
import { createEduContent } from '../../../src/lib/db';
import { isAdmin } from '../../../src/lib/auth';
import { errorResponse, successResponse, parseJsonBody } from '../../../src/lib/utils';

/**
 * POST /api/education/create - Create educational content (admin only)
 */
export const onRequestPost: PagesFunction<Env> = async ({ request, env, data }) => {
  const user = data.user as User;
  
  if (!user || !isAdmin(user)) {
    return errorResponse('Acesso negado', 403);
  }
  
  const body = await parseJsonBody<{
    tipo: string;
    titulo: string;
    conteudo?: string;
    resumo?: string;
    imagem?: string;
    arquivo_url?: string;
    link?: string;
    tema_id?: number;
  }>(request);
  
  if (!body || !body.tipo || !body.titulo) {
    return errorResponse('Tipo e título são obrigatórios', 400);
  }
  
  // Validate tipo
  const validTipos = ['artigo', 'apostila', 'podcast', 'exercicio', 'redacao_tema', 'variacao'];
  if (!validTipos.includes(body.tipo)) {
    return errorResponse('Tipo inválido', 400);
  }
  
  const contentId = await createEduContent(
    env.DB,
    body.tipo,
    body.titulo,
    body.conteudo,
    body.resumo,
    body.imagem,
    body.arquivo_url,
    body.link,
    user.id,
    body.tema_id
  );
  
  if (!contentId) {
    return errorResponse('Erro ao criar conteúdo', 500);
  }
  
  return successResponse(
    { id: contentId },
    'Conteúdo criado com sucesso',
    201
  );
};
