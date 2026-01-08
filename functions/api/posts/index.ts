// GET /api/posts - List posts
// POST /api/posts - Create post

import type { PagesFunction } from '@cloudflare/workers-types';
import type { Env } from '../../../src/types';
import { getPosts, createPost } from '../../../src/lib/db';
import { isValidPostContent } from '../../../src/lib/validation';
import { jsonResponse, errorResponse } from '../../../src/lib/response';

export const onRequestGet: PagesFunction<Env> = async ({ env, data }) => {
  try {
    const userId = data.user?.id;
    const posts = await getPosts(env.DB, 20, 0, userId);
    
    return jsonResponse({ posts });
  } catch (error) {
    console.error('[posts/index] GET Error:', error);
    return errorResponse('Erro ao buscar posts', 500);
  }
};

export const onRequestPost: PagesFunction<Env> = async ({ request, env, data }) => {
  try {
    const user = data.user;
    if (!user) {
      return errorResponse('Não autorizado', 401);
    }
    
    const { content, image } = await request.json();
    
    if (!isValidPostContent(content)) {
      return errorResponse('Conteúdo inválido (1-5000 caracteres)', 400);
    }
    
    const post = await createPost(env.DB, user.id, content, image);
    
    // Add user info to post
    const postWithUser = {
      ...post,
      username: user.username,
      name: user.name,
      avatar: user.avatar,
      likes_count: 0,
      comments_count: 0
    };
    
    return jsonResponse({ post: postWithUser }, 201);
  } catch (error) {
    console.error('[posts/index] POST Error:', error);
    return errorResponse('Erro ao criar post', 500);
  }
};
