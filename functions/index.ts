// Landing page - redirect to feed or login

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../src/types';
import { redirectResponse, htmlResponse } from '../src/lib/response';

export const onRequestGet: PagesFunction<Env> = async ({ data }) => {
  const user = data.user;
  
  // If logged in, redirect to feed
  if (user) {
    return redirectResponse('/feed');
  }
  
  // Otherwise redirect to login
  return redirectResponse('/login');
};
