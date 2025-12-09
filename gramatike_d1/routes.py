# gramatike_d1/routes.py
# Rotas da API para Cloudflare Workers
# Este módulo contém handlers para todas as rotas da aplicação
#
# NOTA: Renomeado de 'workers/' para 'gramatike_d1/' para evitar conflito
# com o módulo 'workers' built-in do Cloudflare Workers Python.

import json
from urllib.parse import parse_qs
from .db import (
    get_posts, get_post_by_id, create_post, delete_post, like_post, unlike_post, has_liked,
    get_comments, create_comment,
    get_user_by_id, get_user_by_username, update_user_profile,
    follow_user, unfollow_user, is_following, get_followers, get_following,
    get_edu_contents, get_edu_content_by_id, search_edu_contents,
    get_exercise_topics, get_exercise_questions,
    get_dynamics, get_dynamic_by_id, get_dynamic_responses, submit_dynamic_response,
    get_palavras_do_dia, get_palavra_do_dia_atual,
    get_divulgacoes, get_novidades,
    sanitize_for_d1
)
from .auth import get_current_user, login, logout, register, set_session_cookie, clear_session_cookie


# ============================================================================
# API ROUTES - POSTS
# ============================================================================

async def api_get_posts(db, request, params):
    """GET /api/posts - Lista posts."""
    page = int(params.get('page', [1])[0])
    per_page = min(int(params.get('per_page', [20])[0]), 50)
    
    posts = await get_posts(db, page=page, per_page=per_page)
    
    # Verifica se usuárie logade curtiu cada post
    user = await get_current_user(db, request)
    if user:
        for post in posts:
            post['liked'] = await has_liked(db, user['id'], post['id'])
    
    return {'posts': posts, 'page': page, 'per_page': per_page}


async def api_create_post(db, request, user):
    """POST /api/posts - Cria um post."""
    try:
        body = await request.json()
    except:
        body = {}
    
    conteudo = body.get('conteudo', '').strip()
    imagem = body.get('imagem')
    
    if not conteudo:
        return {'error': 'Conteúdo é obrigatório'}, 400
    
    if len(conteudo) > 5000:
        return {'error': 'Conteúdo muito longo (máx 5000 caracteres)'}, 400
    
    # Sanitize usuarie_id to prevent D1_TYPE_ERROR from undefined values
    usuarie_id = sanitize_for_d1(user.get('id') if isinstance(user, dict) else user['id'])
    if usuarie_id is None:
        return {'error': 'Usuárie inválide'}, 400
    
    post_id = await create_post(db, usuarie_id, conteudo, imagem)
    if not post_id:
        return {'error': 'Erro ao criar post'}, 500
    
    post = await get_post_by_id(db, post_id)
    return {'post': post}


async def api_like_post(db, request, user, post_id):
    """POST /api/posts/{id}/like - Curte/descurte um post."""
    already_liked = await has_liked(db, user['id'], post_id)
    
    if already_liked:
        await unlike_post(db, user['id'], post_id)
        return {'liked': False}
    else:
        await like_post(db, user['id'], post_id)
        return {'liked': True}


async def api_delete_post(db, request, user, post_id):
    """DELETE /api/posts/{id} - Remove um post."""
    post = await get_post_by_id(db, post_id)
    if not post:
        return {'error': 'Post não encontrado'}, 404
    
    # Verifica permissão
    if post['usuarie_id'] != user['id'] and not user.get('is_admin'):
        return {'error': 'Sem permissão'}, 403
    
    await delete_post(db, post_id, user['id'])
    return {'success': True}


# ============================================================================
# API ROUTES - COMENTÁRIOS
# ============================================================================

async def api_get_comments(db, request, post_id, params):
    """GET /api/posts/{id}/comentarios - Lista comentários."""
    page = int(params.get('page', [1])[0])
    comments = await get_comments(db, post_id, page=page)
    return {'comentarios': comments}


async def api_create_comment(db, request, user, post_id):
    """POST /api/posts/{id}/comentarios - Cria comentário."""
    try:
        body = await request.json()
    except:
        body = {}
    
    conteudo = body.get('conteudo', '').strip()
    if not conteudo:
        return {'error': 'Conteúdo é obrigatório'}, 400
    
    comment_id = await create_comment(db, post_id, user['id'], conteudo)
    return {'id': comment_id}


# ============================================================================
# API ROUTES - USUÁRIOS
# ============================================================================

async def api_get_profile(db, request, username):
    """GET /api/usuario/{username} - Perfil de usuárie."""
    user = await get_user_by_username(db, username)
    if not user:
        return {'error': 'Usuárie não encontrade'}, 404
    
    # Remove senha
    user.pop('password', None)
    
    # Adiciona contadores
    followers = await get_followers(db, user['id'])
    following = await get_following(db, user['id'])
    user['followers_count'] = len(followers)
    user['following_count'] = len(following)
    
    # Verifica se usuárie logade segue
    current = await get_current_user(db, request)
    if current and current['id'] != user['id']:
        user['is_following'] = await is_following(db, current['id'], user['id'])
    
    return {'user': user}


async def api_follow_user(db, request, user, username):
    """POST /api/usuario/{username}/seguir - Seguir usuárie."""
    target = await get_user_by_username(db, username)
    if not target:
        return {'error': 'Usuárie não encontrade'}, 404
    
    already = await is_following(db, user['id'], target['id'])
    
    if already:
        await unfollow_user(db, user['id'], target['id'])
        return {'following': False}
    else:
        await follow_user(db, user['id'], target['id'])
        return {'following': True}


async def api_update_profile(db, request, user):
    """POST /api/editar-perfil - Atualiza perfil."""
    try:
        body = await request.json()
    except:
        body = {}
    
    await update_user_profile(db, user['id'], **body)
    
    updated = await get_user_by_id(db, user['id'])
    updated.pop('password', None)
    return {'user': updated}


# ============================================================================
# API ROUTES - CONTEÚDO EDUCACIONAL
# ============================================================================

async def api_get_edu_contents(db, request, params):
    """GET /api/edu - Lista conteúdos educacionais."""
    tipo = params.get('tipo', [None])[0]
    page = int(params.get('page', [1])[0])
    
    contents = await get_edu_contents(db, tipo=tipo, page=page)
    return {'contents': contents}


async def api_search_edu(db, request, params):
    """GET /api/gramatike/search - Pesquisa conteúdos."""
    query = params.get('q', [''])[0]
    tipo = params.get('tipo', [None])[0]
    
    if len(query) < 2:
        return {'error': 'Pesquisa muito curta'}, 400
    
    results = await search_edu_contents(db, query, tipo)
    return {'results': results}


# ============================================================================
# API ROUTES - EXERCÍCIOS
# ============================================================================

async def api_get_exercises(db, request, params):
    """GET /api/exercicios - Lista exercícios."""
    topic_id = params.get('topic_id', [None])[0]
    section_id = params.get('section_id', [None])[0]
    
    topics = await get_exercise_topics(db)
    questions = await get_exercise_questions(db, topic_id, section_id)
    
    return {'topics': topics, 'questions': questions}


# ============================================================================
# API ROUTES - DINÂMICAS
# ============================================================================

async def api_get_dynamics(db, request):
    """GET /api/dinamicas - Lista dinâmicas."""
    dynamics = await get_dynamics(db)
    return {'dinamicas': dynamics}


async def api_get_dynamic(db, request, dynamic_id):
    """GET /api/dinamicas/{id} - Detalhes de uma dinâmica."""
    dynamic = await get_dynamic_by_id(db, dynamic_id)
    if not dynamic:
        return {'error': 'Dinâmica não encontrada'}, 404
    
    responses = await get_dynamic_responses(db, dynamic_id)
    dynamic['responses'] = responses
    
    return {'dinamica': dynamic}


async def api_submit_dynamic(db, request, user, dynamic_id):
    """POST /api/dinamicas/{id}/responder - Responde dinâmica."""
    try:
        body = await request.json()
    except:
        body = {}
    
    response_id = await submit_dynamic_response(db, dynamic_id, user['id'], body)
    return {'id': response_id}


# ============================================================================
# API ROUTES - PALAVRAS DO DIA
# ============================================================================

async def api_get_palavra_do_dia(db, request):
    """GET /api/palavra-do-dia - Palavra do dia atual."""
    palavra = await get_palavra_do_dia_atual(db)
    return {'palavra': palavra}


async def api_get_palavras_do_dia(db, request):
    """GET /api/palavras-do-dia - Lista todas as palavras."""
    palavras = await get_palavras_do_dia(db)
    return {'palavras': palavras}


# ============================================================================
# API ROUTES - DIVULGAÇÃO
# ============================================================================

async def api_get_divulgacao(db, request, params):
    """GET /api/divulgacao - Lista divulgações."""
    area = params.get('area', [None])[0]
    divulgacoes = await get_divulgacoes(db, area=area)
    return {'divulgacoes': divulgacoes}


async def api_get_novidades(db, request):
    """GET /api/novidades - Lista novidades."""
    novidades = await get_novidades(db)
    return {'novidades': novidades}


# ============================================================================
# AUTH ROUTES
# ============================================================================

async def api_login(db, request):
    """POST /api/login - Login."""
    try:
        body = await request.json()
    except:
        body = {}
    
    email = body.get('email', '').strip()
    password = body.get('password', '')
    
    if not email or not password:
        return {'error': 'Email e senha são obrigatórios'}, 400
    
    token, error = await login(db, request, email, password)
    if error:
        return {'error': error}, 401
    
    return {'success': True, 'token': token}, 200, {'Set-Cookie': set_session_cookie(token)}


async def api_logout(db, request):
    """POST /api/logout - Logout."""
    await logout(db, request)
    return {'success': True}, 200, {'Set-Cookie': clear_session_cookie()}


async def api_register(db, request):
    """POST /api/cadastro - Registro."""
    try:
        body = await request.json()
    except:
        body = {}
    
    username = body.get('username', '').strip()
    email = body.get('email', '').strip()
    password = body.get('password', '')
    nome = body.get('nome', '').strip() or None
    
    usuarie_id, error = await register(db, username, email, password, nome)
    if error:
        return {'error': error}, 400
    
    # Auto-login após registro
    token, _ = await login(db, request, email, password)
    
    return {'success': True, 'usuarie_id': usuarie_id}, 201, {'Set-Cookie': set_session_cookie(token)}


async def api_me(db, request):
    """GET /api/me - Usuário atual."""
    user = await get_current_user(db, request)
    if not user:
        return {'error': 'Não autenticado'}, 401
    return {'user': user}
