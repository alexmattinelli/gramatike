// GET /api/admin/stats - Admin dashboard statistics

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../../src/types';
import { isAdmin } from '../../../src/lib/auth';
import { jsonResponse, errorResponse } from '../../../src/lib/response';
import { getStats } from '../../../src/lib/db';

export const onRequestGet: PagesFunction<Env> = async ({ env, data }) => {
  try {
    const user = data.user;
    if (!user || !isAdmin(user)) {
      return errorResponse('Sem permissão', 403);
    }
    
    const stats = await getStats(env.DB);
    
    return jsonResponse(stats);
  } catch (error) {
    console.error('[admin/stats] Error:', error);
    return errorResponse('Erro ao buscar estatísticas', 500);
  }
};
