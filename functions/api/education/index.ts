// Education Content API - List and Get
import type { Env } from '../../../src/types';
import { getEduContent, getEduContentById } from '../../../src/lib/db';
import { errorResponse, successResponse, getQueryParam, getQueryParams } from '../../../src/lib/utils';

/**
 * GET /api/education - List educational content
 * Query params: tipo (optional), page (optional)
 */
export const onRequestGet: PagesFunction<Env> = async ({ request, env }) => {
  const { tipo, page: pageParam } = getQueryParams(request, 'tipo', 'page');
  const page = pageParam ? parseInt(pageParam) : 1;
  const perPage = 20;
  
  const content = await getEduContent(env.DB, tipo || undefined, page, perPage);
  
  return successResponse({ content, page, perPage, tipo: tipo || 'all' });
};
