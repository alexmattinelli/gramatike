// Redirect to feed (post creation is now in feed page)
import { Env } from '../src/types';

export const onRequest: PagesFunction<Env> = async () => {
  // Redirect to feed page where post creation is now integrated
  return Response.redirect('/feed', 302);
};
