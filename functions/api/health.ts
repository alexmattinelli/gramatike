// Health check endpoint

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../src/types';
import { jsonResponse } from '../../src/lib/response';

export const onRequestGet: PagesFunction<Env> = async () => {
  return jsonResponse({
    status: 'ok',
    service: 'gramatike-v2',
    timestamp: new Date().toISOString()
  });
};
