# index.py
# Cloudflare Workers Python entry point with D1 Database
# Uses native WorkerEntrypoint pattern + D1 SQLite
# Docs: https://developers.cloudflare.com/workers/languages/python/
#
# Este arquivo serve as páginas HTML com a mesma estética e funcionalidades
# da aplicação Flask original, usando Cloudflare D1 como banco de dados.
# Usa linguagem neutra (usuáries, seguidories, amigues).

import json
from urllib.parse import urlparse, parse_qs
from workers import WorkerEntrypoint, Response

# Importar módulos de banco de dados e autenticação
try:
    from workers.db import (
        # Posts e interações
        get_posts, get_post_by_id, create_post, delete_post, like_post, unlike_post, has_liked,
        get_comments, create_comment,
        # Usuáries
        get_user_by_id, get_user_by_username, update_user_profile,
        follow_user, unfollow_user, is_following, get_followers, get_following,
        # Educação
        get_edu_contents, search_edu_contents,
        get_exercise_topics, get_exercise_questions,
        get_dynamics, get_dynamic_by_id, get_dynamic_responses, submit_dynamic_response,
        get_palavra_do_dia_atual, get_palavras_do_dia,
        get_divulgacoes, get_novidades,
        # Notificações
        create_notification, get_notifications, count_unread_notifications,
        mark_notification_read, mark_all_notifications_read,
        # Amigues
        send_friend_request, respond_friend_request, get_amigues,
        get_pending_friend_requests, are_amigues, remove_amizade,
        # Tokens de email
        create_email_token, verify_email_token, use_email_token,
        confirm_user_email, update_user_password, update_user_email,
        # Denúncias
        create_report, get_reports, resolve_report, count_pending_reports,
        # Suporte
        create_support_ticket, get_support_tickets, get_user_tickets,
        respond_ticket, close_ticket,
        # Divulgação
        create_divulgacao, update_divulgacao, delete_divulgacao,
        # Upload
        save_upload, get_user_uploads,
        # Admin
        get_all_usuaries, ban_usuarie, unban_usuarie, suspend_usuarie,
        make_admin, get_admin_stats,
        # Rate limiting e logs
        check_rate_limit, log_activity,
        # Gamificação
        get_user_points, add_points, get_ranking, get_all_badges,
        get_user_badges, award_badge, check_and_award_badges,
        # Exercícios e progresso
        record_exercise_answer, get_user_exercise_stats, get_questions_not_scored,
        create_exercise_list, add_to_exercise_list, get_exercise_lists,
        get_exercise_list_questions, save_quiz_result,
        # Flashcards
        create_flashcard_deck, add_flashcard, get_flashcard_decks,
        get_flashcards, get_cards_to_review, record_flashcard_review,
        # Favoritos
        add_favorite, remove_favorite, is_favorite, get_favorites,
        # Histórico
        add_to_history, get_user_history,
        # Preferências
        get_user_preferences, update_user_preferences,
        # Mensagens diretas
        send_direct_message, get_conversations, get_messages_with_user,
        # Grupos de estudo
        create_study_group, join_study_group, leave_study_group,
        get_study_groups, get_group_messages, send_group_message,
        # Acessibilidade
        get_accessibility_content, save_accessibility_content,
        # Validação de senha
        validate_password_strength
    )
    from workers.auth import (
        get_current_user, login, logout, register,
        set_session_cookie, clear_session_cookie
    )
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


def json_response(data, status=200, headers=None):
    """Create a JSON response."""
    resp_headers = {"Content-Type": "application/json; charset=utf-8"}
    if headers:
        resp_headers.update(headers)
    return Response(
        json.dumps(data, ensure_ascii=False),
        status=status,
        headers=resp_headers
    )


def html_response(content, status=200, headers=None):
    """Create an HTML response."""
    resp_headers = {"Content-Type": "text/html; charset=utf-8"}
    if headers:
        resp_headers.update(headers)
    return Response(
        content,
        status=status,
        headers=resp_headers
    )


def redirect(url, status=302, headers=None):
    """Create a redirect response."""
    resp_headers = {"Location": url}
    if headers:
        resp_headers.update(headers)
    return Response("", status=status, headers=resp_headers)


# ============================================================================
# CSS STYLES - Mesma estética do Gramátike
# ============================================================================

BASE_CSS = """
:root {
    --primary: #9B5DE5;
    --primary-dark: #7d3dc9;
    --bg: #f7f8ff;
    --card: #ffffff;
    --border: #e5e7eb;
    --text: #222;
    --text-dim: #666;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { 
    height: 100%; 
    overflow-x: hidden;
    width: 100%;
    max-width: 100vw;
}
body {
    font-family: 'Nunito', system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.55;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}
h1, h2, h3 { font-weight: 800; margin: 0 0 0.9rem; line-height: 1.12; }

/* Header */
header.site-head {
    background: var(--primary);
    padding: 28px clamp(16px, 4vw, 40px) 46px;
    border-bottom-left-radius: 40px;
    border-bottom-right-radius: 40px;
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.logo {
    font-family: 'Mansalva', cursive;
    font-size: 2.6rem;
    color: #fff;
    letter-spacing: 1px;
    font-weight: 400;
}
.edu-nav {
    margin-top: 1.1rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.65rem;
    justify-content: center;
}
.edu-nav a {
    text-decoration: none;
    font-weight: 700;
    font-size: 0.7rem;
    letter-spacing: 0.55px;
    padding: 0.65rem 1.05rem 0.62rem;
    background: rgba(255,255,255,0.1);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.3);
    backdrop-filter: blur(4px);
    border-radius: 22px;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.18);
    transition: 0.25s;
}
.edu-nav a:hover, .edu-nav a.active {
    background: #fff;
    color: var(--primary-dark);
}

/* Main */
main {
    flex: 1;
    width: 100%;
    max-width: 1380px;
    margin: 2rem auto 4.2rem;
    padding: 0 clamp(14px, 3vw, 44px);
}

/* Cards */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 1.5rem 1.8rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    margin-bottom: 1.5rem;
}
.feed-item {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 28px;
    padding: 1.3rem 1.5rem 1.2rem;
    box-shadow: 0 10px 24px -8px rgba(0,0,0,0.10);
    transition: 0.28s;
    margin-bottom: 1.3rem;
}
.feed-item:hover {
    box-shadow: 0 18px 42px -12px rgba(0,0,0,0.26);
    transform: translateY(-3px);
}
.fi-title {
    font-size: 1rem;
    font-weight: 800;
    letter-spacing: 0.45px;
    color: #6233B5;
    margin: 0 0 0.5rem;
    line-height: 1.3;
}
.fi-meta {
    font-size: 0.6rem;
    letter-spacing: 0.55px;
    font-weight: 800;
    text-transform: uppercase;
    color: #7d3dc9;
    margin: 0 0 0.45rem;
}
.fi-body {
    font-size: 0.75rem;
    line-height: 1.5;
    color: var(--text-dim);
    font-weight: 500;
}

/* Buttons */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    padding: 0.7rem 1.4rem;
    border-radius: 14px;
    border: none;
    cursor: pointer;
    font-weight: 700;
    font-size: 0.85rem;
    text-decoration: none;
    transition: all 0.2s;
}
.btn-primary {
    background: var(--primary);
    color: white;
    box-shadow: 0 4px 12px rgba(130,87,229,0.45);
}
.btn-primary:hover {
    background: var(--primary-dark);
    transform: translateY(-2px);
}

/* Search */
.search-box {
    display: flex;
    max-width: 880px;
    margin: 0 auto 2.1rem;
    gap: 0.55rem;
}
.search-box input {
    flex: 1;
    height: 48px;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 0 1rem;
    font-size: 0.9rem;
    background: var(--card);
    font-weight: 500;
}
.search-btn {
    height: 48px;
    width: 48px;
    border: none;
    background: var(--primary);
    color: #fff;
    border-radius: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(130,87,229,0.45);
}
.search-btn:hover {
    background: var(--primary-dark);
}

/* Layout */
.layout {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 330px;
    gap: 2.2rem;
    align-items: start;
}
@media (max-width: 1080px) {
    .layout { grid-template-columns: 1fr; }
}

/* Sidebar */
.side-col {
    display: flex;
    flex-direction: column;
    gap: 1.4rem;
    position: sticky;
    top: 12px;
}
.side-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 28px;
    padding: 1.1rem 1.15rem 0.95rem;
    box-shadow: 0 6px 18px -8px rgba(0,0,0,0.08);
}
.side-card h3 {
    margin: 0.15rem 0 0.55rem;
    font-size: 0.85rem;
    letter-spacing: 0.5px;
    font-weight: 800;
    color: #6233B5;
}

/* Quick nav */
.quick-nav {
    display: flex;
    gap: 0.5rem;
    margin: 0 0 0.6rem;
}
.quick-nav a {
    text-decoration: none;
    font-weight: 800;
    font-size: 0.62rem;
    letter-spacing: 0.4px;
    padding: 0.45rem 0.75rem 0.4rem;
    border-radius: 16px;
    border: 1px solid var(--border);
    background: #fff;
    color: #6233B5;
    box-shadow: 0 4px 10px rgba(0,0,0,0.06);
}
.quick-nav a:hover {
    background: #f7f2ff;
    border-color: #e1d4fb;
}

/* Footer */
footer {
    margin-top: auto;
    background: var(--primary);
    color: #fff;
    text-align: center;
    padding: 1.4rem 1rem 1.6rem;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
    font-weight: 700;
    border-top-left-radius: 38px;
    border-top-right-radius: 38px;
}

/* Mobile nav */
.mobile-nav {
    display: none;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #ffffff;
    border-top: 1px solid var(--border);
    padding: 8px 0 calc(8px + env(safe-area-inset-bottom));
    box-shadow: 0 -4px 12px rgba(0,0,0,0.08);
    z-index: 1000;
}
.mobile-nav a {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    color: #666;
    text-decoration: none;
    font-size: 0.65rem;
    font-weight: 600;
}
.mobile-nav a:hover { color: var(--primary); }
.mobile-nav svg { color: inherit; }

/* Mobile */
@media (max-width: 980px) {
    header.site-head { padding: 12px clamp(12px, 3vw, 24px) 18px; }
    .logo { font-size: 1.5rem; }
    .edu-nav { display: none !important; }
    .quick-nav { display: none !important; }
    footer { display: none !important; }
    .mobile-nav {
        display: flex;
        justify-content: space-around;
        align-items: center;
    }
    main { margin-bottom: calc(60px + env(safe-area-inset-bottom)) !important; }
    .side-col { display: none; }
}
@media (max-width: 720px) {
    .feed-item { padding: 1rem 1.05rem 0.9rem; }
}

/* Form styles */
.form-group { margin-bottom: 1rem; }
.form-group label {
    display: block;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.6px;
    margin: 0 0 0.35rem;
    text-transform: uppercase;
    opacity: 0.8;
}
.form-group input {
    width: 100%;
    padding: 0.75rem 0.85rem;
    border: 1.5px solid #d9e1ea;
    border-radius: 12px;
    background: #fff;
    font-size: 0.9rem;
    font-family: 'Nunito', sans-serif;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.form-group input:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(155,93,229,0.15);
}
.button-primary {
    width: 100%;
    background: var(--primary);
    color: #fff;
    font-weight: 700;
    font-size: 0.95rem;
    letter-spacing: 0.7px;
    padding: 0.9rem 1rem 0.95rem;
    border: none;
    border-radius: 14px;
    cursor: pointer;
    box-shadow: 0 2px 8px -2px rgba(155,93,229,0.6);
    transition: 0.25s;
}
.button-primary:hover {
    background: var(--primary-dark);
    box-shadow: 0 6px 20px -4px rgba(155,93,229,0.5);
}

/* Grid for modules */
.modules-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}
.module-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1.5rem;
    text-align: center;
    text-decoration: none;
    color: var(--text);
    transition: all 0.2s;
}
.module-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.12);
    border-color: var(--primary);
}
.module-card .icon { font-size: 2rem; margin-bottom: 0.8rem; }
.module-card h3 { color: var(--primary); font-size: 1.1rem; margin-bottom: 0.4rem; }
.module-card p { color: var(--text-dim); font-size: 0.85rem; margin: 0; }

.muted { color: #666; font-weight: 600; }
.empty { font-size: 0.7rem; font-weight: 600; color: #666; text-align: center; padding: 2rem 0; }
.placeholder { 
    font-size: 0.6rem; 
    font-weight: 700; 
    letter-spacing: 0.5px; 
    color: #999; 
    padding: 0.65rem 0.85rem; 
    border: 1px dashed #d2c5ef; 
    border-radius: 18px; 
    background: #faf7ff; 
}
"""

# ============================================================================
# PAGE TEMPLATES
# ============================================================================

def page_head(title, extra_css=""):
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="theme-color" content="#9B5DE5">
    <link href="https://fonts.googleapis.com/css2?family=Mansalva&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>{BASE_CSS}{extra_css}</style>
</head>
<body>"""

def mobile_nav():
    return """
    <nav class="mobile-nav">
        <a href="/">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            <span>Início</span>
        </a>
        <a href="/educacao">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
            </svg>
            <span>Educação</span>
        </a>
        <a href="/login" style="background: var(--primary); color: white; border-radius: 50%; width: 48px; height: 48px; margin: -10px 0; padding: 0;">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
            </svg>
        </a>
        <a href="/dinamicas">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="6" width="20" height="12" rx="2"></rect>
                <path d="M6 12h4"></path>
                <path d="M14 12h4"></path>
            </svg>
            <span>Dinâmicas</span>
        </a>
        <a href="/exercicios">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            <span>Exercícios</span>
        </a>
    </nav>"""

def page_footer():
    return f"""
    <footer>© 2025 Gramátike • Inclusão e Gênero Neutro</footer>
    {mobile_nav()}
</body>
</html>"""


class Default(WorkerEntrypoint):
    """Cloudflare Worker entry point with D1 Database support."""

    async def fetch(self, request):
        """Handle incoming HTTP requests."""
        url = request.url
        path = "/"
        query_params = {}
        
        if url:
            parsed = urlparse(url)
            path = parsed.path or "/"
            query_params = parse_qs(parsed.query)
        
        method = request.method
        
        # Obter banco de dados D1
        db = getattr(self.env, 'DB', None)
        
        # Obter usuário atual se DB disponível
        current_user = None
        if db and DB_AVAILABLE:
            try:
                current_user = await get_current_user(db, request)
            except:
                pass
        
        # ====================================================================
        # API ROUTES
        # ====================================================================
        
        if path.startswith('/api/'):
            return await self._handle_api(request, path, method, query_params, db, current_user)
        
        # ====================================================================
        # PAGE ROUTES
        # ====================================================================
        
        # Rotas que requerem autenticação
        if path == '/' and not current_user:
            # Redireciona para login se não autenticado na página principal
            pass  # Permite ver a página inicial sem login
        
        # Route handling
        page_routes = {
            "/": lambda: self._index_page(db, current_user),
            "": lambda: self._index_page(db, current_user),
            "/educacao": lambda: self._educacao_page(db, current_user),
            "/login": lambda: self._login_page(db, current_user, request, method),
            "/cadastro": lambda: self._cadastro_page(db, current_user, request, method),
            "/dinamicas": lambda: self._dinamicas_page(db, current_user),
            "/exercicios": lambda: self._exercicios_page(db, current_user),
            "/artigos": lambda: self._artigos_page(db, current_user),
            "/apostilas": lambda: self._apostilas_page(db, current_user),
            "/podcasts": lambda: self._podcasts_page(db, current_user),
            "/logout": lambda: self._logout(db, request),
        }

        handler = page_routes.get(path)
        if handler:
            result = await self._safe_call(handler)
            if isinstance(result, Response):
                return result
            return html_response(result)
        
        # Rotas dinâmicas (perfil de usuário)
        if path.startswith('/u/'):
            username = path[3:]
            result = await self._profile_page(db, current_user, username)
            return html_response(result) if not isinstance(result, Response) else result
        
        return html_response(self._not_found_page(path), status=404)

    async def _safe_call(self, handler):
        """Chama handler de forma segura."""
        try:
            result = handler()
            if hasattr(result, '__await__'):
                result = await result
            return result
        except Exception as e:
            return f"<h1>Erro</h1><p>{str(e)}</p>"

    async def _handle_api(self, request, path, method, params, db, current_user):
        """Handle API routes."""
        
        # Health check (não precisa de DB)
        if path == '/api/health':
            return json_response({
                "status": "ok",
                "platform": "Cloudflare Workers + D1",
                "db_available": db is not None and DB_AVAILABLE
            })
        
        if path == '/api/info':
            return json_response({
                "name": "Gramátike",
                "version": "2.0.0",
                "features": ["D1 Database", "Auth", "Posts", "Education"]
            })
        
        # Se DB não disponível, retorna erro
        if not db or not DB_AVAILABLE:
            return json_response({"error": "Database não disponível"}, 503)
        
        try:
            # ================================================================
            # AUTH ROUTES
            # ================================================================
            
            if path == '/api/login' and method == 'POST':
                body = await request.json()
                email = body.get('email', '').strip()
                password = body.get('password', '')
                
                token, error = await login(db, request, email, password)
                if error:
                    return json_response({"error": error}, 401)
                
                return json_response(
                    {"success": True},
                    headers={"Set-Cookie": set_session_cookie(token)}
                )
            
            if path == '/api/logout' and method == 'POST':
                await logout(db, request)
                return json_response(
                    {"success": True},
                    headers={"Set-Cookie": clear_session_cookie()}
                )
            
            if path == '/api/cadastro' and method == 'POST':
                body = await request.json()
                username = body.get('username', '').strip()
                email = body.get('email', '').strip()
                password = body.get('password', '')
                nome = body.get('nome', '').strip() or None
                
                user_id, error = await register(db, username, email, password, nome)
                if error:
                    return json_response({"error": error}, 400)
                
                token, _ = await login(db, request, email, password)
                return json_response(
                    {"success": True, "user_id": user_id},
                    status=201,
                    headers={"Set-Cookie": set_session_cookie(token)}
                )
            
            if path == '/api/me':
                if not current_user:
                    return json_response({"error": "Não autenticado"}, 401)
                return json_response({"user": current_user})
            
            # ================================================================
            # POSTS ROUTES
            # ================================================================
            
            if path == '/api/posts':
                if method == 'GET':
                    page = int(params.get('page', [1])[0])
                    posts = await get_posts(db, page=page)
                    
                    # Verifica likes do usuário atual
                    if current_user:
                        for post in posts:
                            post['liked'] = await has_liked(db, current_user['id'], post['id'])
                    
                    return json_response({"posts": posts, "page": page})
                
                elif method == 'POST':
                    if not current_user:
                        return json_response({"error": "Não autenticado"}, 401)
                    
                    body = await request.json()
                    conteudo = body.get('conteudo', '').strip()
                    imagem = body.get('imagem')
                    
                    if not conteudo:
                        return json_response({"error": "Conteúdo é obrigatório"}, 400)
                    
                    post_id = await create_post(db, current_user['id'], conteudo, imagem)
                    post = await get_post_by_id(db, post_id)
                    return json_response({"post": post}, 201)
            
            # Like/Unlike post
            if path.startswith('/api/posts/') and path.endswith('/like') and method == 'POST':
                if not current_user:
                    return json_response({"error": "Não autenticado"}, 401)
                
                try:
                    post_id = int(path.split('/')[3])
                except (ValueError, IndexError):
                    return json_response({"error": "ID de post inválido"}, 400)
                
                already_liked = await has_liked(db, current_user['id'], post_id)
                
                if already_liked:
                    await unlike_post(db, current_user['id'], post_id)
                    return json_response({"liked": False})
                else:
                    await like_post(db, current_user['id'], post_id)
                    return json_response({"liked": True})
            
            # Comentários
            if '/comentarios' in path:
                try:
                    post_id = int(path.split('/')[3])
                except (ValueError, IndexError):
                    return json_response({"error": "ID de post inválido"}, 400)
                
                if method == 'GET':
                    comments = await get_comments(db, post_id)
                    return json_response({"comentarios": comments})
                
                elif method == 'POST':
                    if not current_user:
                        return json_response({"error": "Não autenticado"}, 401)
                    
                    body = await request.json()
                    conteudo = body.get('conteudo', '').strip()
                    
                    if not conteudo:
                        return json_response({"error": "Conteúdo é obrigatório"}, 400)
                    
                    comment_id = await create_comment(db, post_id, current_user['id'], conteudo)
                    return json_response({"id": comment_id}, 201)
            
            # ================================================================
            # EDUCATION ROUTES
            # ================================================================
            
            if path == '/api/gramatike/search':
                query = params.get('q', [''])[0]
                tipo = params.get('tipo', [None])[0]
                
                if len(query) < 2:
                    return json_response({"error": "Pesquisa muito curta"}, 400)
                
                results = await search_edu_contents(db, query, tipo)
                return json_response({"results": results})
            
            if path == '/api/edu':
                tipo = params.get('tipo', [None])[0]
                page = int(params.get('page', [1])[0])
                contents = await get_edu_contents(db, tipo=tipo, page=page)
                return json_response({"contents": contents})
            
            # ================================================================
            # DYNAMICS ROUTES
            # ================================================================
            
            if path == '/api/dinamicas':
                dynamics = await get_dynamics(db)
                return json_response({"dinamicas": dynamics})
            
            if path.startswith('/api/dinamicas/') and '/responder' in path and method == 'POST':
                if not current_user:
                    return json_response({"error": "Não autenticado"}, 401)
                
                try:
                    dynamic_id = int(path.split('/')[3])
                except (ValueError, IndexError):
                    return json_response({"error": "ID de dinâmica inválido"}, 400)
                
                body = await request.json()
                
                response_id = await submit_dynamic_response(db, dynamic_id, current_user['id'], body)
                return json_response({"id": response_id}, 201)
            
            # ================================================================
            # PALAVRA DO DIA
            # ================================================================
            
            if path == '/api/palavra-do-dia':
                palavra = await get_palavra_do_dia_atual(db)
                return json_response({"palavra": palavra})
            
            # ================================================================
            # DIVULGAÇÃO / NOVIDADES
            # ================================================================
            
            if path == '/api/divulgacao':
                area = params.get('area', [None])[0]
                divulgacoes = await get_divulgacoes(db, area=area)
                return json_response({"divulgacoes": divulgacoes})
            
            if path == '/api/novidades':
                novidades = await get_novidades(db)
                return json_response({"novidades": novidades})
            
            # ================================================================
            # FOLLOW/UNFOLLOW
            # ================================================================
            
            if path.startswith('/api/usuario/') and '/seguir' in path and method == 'POST':
                if not current_user:
                    return json_response({"error": "Não autenticado"}, 401)
                
                username = path.split('/')[3]
                target = await get_user_by_username(db, username)
                if not target:
                    return json_response({"error": "Usuárie não encontrade"}, 404)
                
                already = await is_following(db, current_user['id'], target['id'])
                
                if already:
                    await unfollow_user(db, current_user['id'], target['id'])
                    return json_response({"following": False})
                else:
                    await follow_user(db, current_user['id'], target['id'])
                    return json_response({"following": True})
            
            # ================================================================
            # NOTIFICAÇÕES
            # ================================================================
            
            if path == '/api/notificacoes':
                if not current_user:
                    return json_response({"error": "Não autenticado"}, 401)
                
                apenas_nao_lidas = params.get('nao_lidas', ['0'])[0] == '1'
                notifications = await get_notifications(db, current_user['id'], apenas_nao_lidas)
                unread_count = await count_unread_notifications(db, current_user['id'])
                
                return json_response({
                    "notificacoes": notifications,
                    "nao_lidas": unread_count
                })
            
            if path == '/api/notificacoes/marcar-lida' and method == 'POST':
                if not current_user:
                    return json_response({"error": "Não autenticado"}, 401)
                
                body = await request.json()
                notification_id = body.get('id')
                
                if notification_id:
                    await mark_notification_read(db, notification_id, current_user['id'])
                else:
                    await mark_all_notifications_read(db, current_user['id'])
                
                return json_response({"success": True})
            
            # ================================================================
            # AMIGUES
            # ================================================================
            
            if path == '/api/amigues':
                if not current_user:
                    return json_response({"error": "Não autenticado"}, 401)
                
                amigues = await get_amigues(db, current_user['id'])
                return json_response({"amigues": amigues})
            
            if path == '/api/amigues/pedidos':
                if not current_user:
                    return json_response({"error": "Não autenticado"}, 401)
                
                pedidos = await get_pending_friend_requests(db, current_user['id'])
                return json_response({"pedidos": pedidos})
            
            if path == '/api/amigues/solicitar' and method == 'POST':
                if not current_user:
                    return json_response({"error": "Não autenticado"}, 401)
                
                body = await request.json()
                destinatarie_id = body.get('usuario_id')
                
                if not destinatarie_id:
                    return json_response({"error": "ID de usuárie é obrigatório"}, 400)
                
                amizade_id, error = await send_friend_request(db, current_user['id'], destinatarie_id)
                if error:
                    return json_response({"error": error}, 400)
                
                return json_response({"id": amizade_id}, 201)
            
            if path == '/api/amigues/responder' and method == 'POST':
                if not current_user:
                    return json_response({"error": "Não autenticado"}, 401)
                
                body = await request.json()
                amizade_id = body.get('amizade_id')
                aceitar = body.get('aceitar', True)
                
                success, error = await respond_friend_request(db, amizade_id, current_user['id'], aceitar)
                if error:
                    return json_response({"error": error}, 400)
                
                return json_response({"success": True, "aceito": aceitar})
            
            if path == '/api/amigues/remover' and method == 'POST':
                if not current_user:
                    return json_response({"error": "Não autenticado"}, 401)
                
                body = await request.json()
                amigue_id = body.get('usuario_id')
                
                await remove_amizade(db, current_user['id'], amigue_id)
                return json_response({"success": True})
            
            # ================================================================
            # DENÚNCIAS
            # ================================================================
            
            if path == '/api/denunciar' and method == 'POST':
                if not current_user:
                    return json_response({"error": "Não autenticado"}, 401)
                
                body = await request.json()
                post_id = body.get('post_id')
                motivo = body.get('motivo', '').strip()
                category = body.get('categoria')
                
                if not post_id or not motivo:
                    return json_response({"error": "Post e motivo são obrigatórios"}, 400)
                
                report_id = await create_report(db, post_id, current_user['id'], motivo, category)
                return json_response({"id": report_id}, 201)
            
            # ================================================================
            # SUPORTE
            # ================================================================
            
            if path == '/api/suporte' and method == 'POST':
                body = await request.json()
                mensagem = body.get('mensagem', '').strip()
                nome = body.get('nome')
                email = body.get('email')
                
                if not mensagem:
                    return json_response({"error": "Mensagem é obrigatória"}, 400)
                
                usuario_id = current_user['id'] if current_user else None
                ticket_id = await create_support_ticket(db, mensagem, usuario_id, nome, email)
                
                return json_response({"id": ticket_id, "message": "Ticket criado com sucesso!"}, 201)
            
            if path == '/api/suporte/meus-tickets':
                if not current_user:
                    return json_response({"error": "Não autenticado"}, 401)
                
                tickets = await get_user_tickets(db, current_user['id'])
                return json_response({"tickets": tickets})
            
            # ================================================================
            # ADMIN ROUTES
            # ================================================================
            
            if path.startswith('/api/admin/'):
                if not current_user:
                    return json_response({"error": "Não autenticado"}, 401)
                
                if not current_user.get('is_admin') and not current_user.get('is_superadmin'):
                    return json_response({"error": "Acesso negado"}, 403)
                
                # Dashboard stats
                if path == '/api/admin/stats':
                    stats = await get_admin_stats(db)
                    return json_response({"stats": stats})
                
                # Lista usuáries
                if path == '/api/admin/usuaries':
                    page = int(params.get('page', [1])[0])
                    search = params.get('q', [None])[0]
                    usuaries = await get_all_usuaries(db, page=page, search=search)
                    return json_response({"usuaries": usuaries})
                
                # Ban/Unban usuárie
                if path == '/api/admin/ban' and method == 'POST':
                    body = await request.json()
                    usuario_id = body.get('usuario_id')
                    reason = body.get('motivo')
                    action = body.get('action', 'ban')
                    
                    if action == 'ban':
                        await ban_usuarie(db, usuario_id, reason, current_user['id'])
                    else:
                        await unban_usuarie(db, usuario_id)
                    
                    return json_response({"success": True})
                
                # Denúncias
                if path == '/api/admin/denuncias':
                    apenas_pendentes = params.get('pendentes', ['1'])[0] == '1'
                    reports = await get_reports(db, apenas_pendentes)
                    return json_response({"denuncias": reports})
                
                if path == '/api/admin/denuncias/resolver' and method == 'POST':
                    body = await request.json()
                    report_id = body.get('report_id')
                    await resolve_report(db, report_id, current_user['id'])
                    return json_response({"success": True})
                
                # Tickets de suporte
                if path == '/api/admin/tickets':
                    status = params.get('status', [None])[0]
                    tickets = await get_support_tickets(db, status)
                    return json_response({"tickets": tickets})
                
                if path == '/api/admin/tickets/responder' and method == 'POST':
                    body = await request.json()
                    ticket_id = body.get('ticket_id')
                    resposta = body.get('resposta')
                    await respond_ticket(db, ticket_id, resposta)
                    return json_response({"success": True})
                
                if path == '/api/admin/tickets/fechar' and method == 'POST':
                    body = await request.json()
                    ticket_id = body.get('ticket_id')
                    await close_ticket(db, ticket_id)
                    return json_response({"success": True})
                
                # Divulgação
                if path == '/api/admin/divulgacao' and method == 'POST':
                    body = await request.json()
                    div_id = await create_divulgacao(
                        db,
                        area=body.get('area', 'geral'),
                        titulo=body.get('titulo'),
                        texto=body.get('texto'),
                        link=body.get('link'),
                        imagem=body.get('imagem'),
                        author_id=current_user['id']
                    )
                    return json_response({"id": div_id}, 201)
                
                if path == '/api/admin/divulgacao/remover' and method == 'POST':
                    body = await request.json()
                    div_id = body.get('id')
                    await delete_divulgacao(db, div_id)
                    return json_response({"success": True})
            
            # ================================================================
            # GAMIFICAÇÃO E PONTOS
            # ================================================================
            
            if path == '/api/pontos':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                pontos = await get_user_points(db, current_user['id'])
                badges = await get_user_badges(db, current_user['id'])
                return json_response({
                    "pontos": pontos,
                    "badges": badges
                })
            
            if path == '/api/ranking':
                tipo = params.get('tipo', [None])[0]
                limit = int(params.get('limit', ['10'])[0])
                ranking = await get_ranking(db, limit=limit, tipo=tipo)
                return json_response({"ranking": ranking})
            
            if path == '/api/badges':
                all_badges = await get_all_badges(db)
                my_badges = []
                if current_user:
                    my_badges = await get_user_badges(db, current_user['id'])
                return json_response({
                    "todos": all_badges,
                    "meus": my_badges
                })
            
            # ================================================================
            # EXERCÍCIOS COM PROGRESSO E PONTUAÇÃO
            # ================================================================
            
            if path == '/api/exercicios/responder' and method == 'POST':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                body = await request.json()
                question_id = body.get('question_id')
                resposta = body.get('resposta')
                correto = body.get('correto', False)
                tempo = body.get('tempo_resposta')
                
                pontos = await record_exercise_answer(
                    db, current_user['id'], question_id, 
                    resposta, correto, tempo
                )
                return json_response({
                    "pontos_ganhos": pontos,
                    "correto": correto
                })
            
            if path == '/api/exercicios/stats':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                topic_id = params.get('topic_id', [None])[0]
                stats = await get_user_exercise_stats(db, current_user['id'], topic_id)
                return json_response(stats)
            
            if path == '/api/exercicios/nao-pontuados':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                topic_id = params.get('topic_id', [None])[0]
                limit = int(params.get('limit', ['10'])[0])
                questions = await get_questions_not_scored(db, current_user['id'], topic_id, limit)
                return json_response({"questions": questions})
            
            # ================================================================
            # LISTAS PERSONALIZADAS DE EXERCÍCIOS
            # ================================================================
            
            if path == '/api/listas-exercicios':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                if method == 'GET':
                    listas = await get_exercise_lists(db, current_user['id'])
                    return json_response({"listas": listas})
                
                if method == 'POST':
                    body = await request.json()
                    list_id = await create_exercise_list(
                        db, current_user['id'],
                        nome=body.get('nome'),
                        descricao=body.get('descricao'),
                        modo=body.get('modo', 'estudo'),
                        tempo_limite=body.get('tempo_limite')
                    )
                    return json_response({"id": list_id}, 201)
            
            if path.startswith('/api/listas-exercicios/') and '/questoes' in path:
                list_id = path.split('/')[3]
                if method == 'GET':
                    questions = await get_exercise_list_questions(db, list_id)
                    return json_response({"questions": questions})
                
                if method == 'POST' and current_user:
                    body = await request.json()
                    success = await add_to_exercise_list(
                        db, list_id, 
                        body.get('question_id'),
                        body.get('ordem', 0)
                    )
                    return json_response({"success": success})
            
            if path == '/api/quiz/resultado' and method == 'POST':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                body = await request.json()
                result_id = await save_quiz_result(
                    db, current_user['id'],
                    body.get('acertos', 0),
                    body.get('erros', 0),
                    body.get('pontos', 0),
                    body.get('tempo_total'),
                    body.get('list_id'),
                    body.get('topic_id')
                )
                return json_response({"id": result_id})
            
            # ================================================================
            # FLASHCARDS
            # ================================================================
            
            if path == '/api/flashcards/decks':
                if method == 'GET':
                    user_id = current_user['id'] if current_user else None
                    decks = await get_flashcard_decks(db, user_id)
                    return json_response({"decks": decks})
                
                if method == 'POST' and current_user:
                    body = await request.json()
                    deck_id = await create_flashcard_deck(
                        db, body.get('titulo'),
                        current_user['id'],
                        body.get('descricao'),
                        body.get('is_public', False)
                    )
                    return json_response({"id": deck_id}, 201)
            
            if path.startswith('/api/flashcards/decks/') and path.count('/') == 4:
                deck_id = path.split('/')[4]
                cards = await get_flashcards(db, deck_id)
                return json_response({"cards": cards})
            
            if path == '/api/flashcards/cards' and method == 'POST':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                body = await request.json()
                card_id = await add_flashcard(
                    db, body.get('deck_id'),
                    body.get('frente'),
                    body.get('verso'),
                    body.get('dica'),
                    body.get('ordem', 0)
                )
                return json_response({"id": card_id}, 201)
            
            if path == '/api/flashcards/revisar':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                deck_id = params.get('deck_id', [None])[0]
                limit = int(params.get('limit', ['20'])[0])
                cards = await get_cards_to_review(db, current_user['id'], deck_id, limit)
                return json_response({"cards": cards})
            
            if path == '/api/flashcards/review' and method == 'POST':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                body = await request.json()
                result = await record_flashcard_review(
                    db, current_user['id'],
                    body.get('flashcard_id'),
                    body.get('quality', 3)
                )
                return json_response(result)
            
            # ================================================================
            # FAVORITOS
            # ================================================================
            
            if path == '/api/favoritos':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                if method == 'GET':
                    tipo = params.get('tipo', [None])[0]
                    favs = await get_favorites(db, current_user['id'], tipo)
                    return json_response({"favoritos": favs})
                
                if method == 'POST':
                    body = await request.json()
                    success = await add_favorite(
                        db, current_user['id'],
                        body.get('tipo'),
                        body.get('item_id')
                    )
                    return json_response({"success": success})
                
                if method == 'DELETE':
                    body = await request.json()
                    await remove_favorite(
                        db, current_user['id'],
                        body.get('tipo'),
                        body.get('item_id')
                    )
                    return json_response({"success": True})
            
            # ================================================================
            # HISTÓRICO
            # ================================================================
            
            if path == '/api/historico':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                item_tipo = params.get('tipo', [None])[0]
                limit = int(params.get('limit', ['50'])[0])
                history = await get_user_history(db, current_user['id'], item_tipo, limit)
                return json_response({"historico": history})
            
            # ================================================================
            # PREFERÊNCIAS DE USUÁRIE (Tema, Acessibilidade)
            # ================================================================
            
            if path == '/api/preferencias':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                if method == 'GET':
                    prefs = await get_user_preferences(db, current_user['id'])
                    return json_response(prefs)
                
                if method == 'POST' or method == 'PUT':
                    body = await request.json()
                    await update_user_preferences(db, current_user['id'], **body)
                    prefs = await get_user_preferences(db, current_user['id'])
                    return json_response(prefs)
            
            # ================================================================
            # MENSAGENS DIRETAS
            # ================================================================
            
            if path == '/api/mensagens':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                conversations = await get_conversations(db, current_user['id'])
                return json_response({"conversations": conversations})
            
            if path.startswith('/api/mensagens/') and method == 'GET':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                other_user_id = path.split('/')[3]
                try:
                    other_user_id = int(other_user_id)
                except ValueError:
                    return json_response({"error": "ID inválido"}, 400)
                
                page = int(params.get('page', ['1'])[0])
                messages = await get_messages_with_user(
                    db, current_user['id'], other_user_id, page
                )
                return json_response({"messages": messages})
            
            if path == '/api/mensagens/enviar' and method == 'POST':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                body = await request.json()
                msg_id = await send_direct_message(
                    db, current_user['id'],
                    body.get('destinatarie_id'),
                    body.get('conteudo')
                )
                return json_response({"id": msg_id}, 201)
            
            # ================================================================
            # GRUPOS DE ESTUDO
            # ================================================================
            
            if path == '/api/grupos':
                if method == 'GET':
                    apenas_meus = params.get('meus', ['0'])[0] == '1'
                    user_id = current_user['id'] if current_user else None
                    grupos = await get_study_groups(db, user_id, apenas_meus)
                    return json_response({"grupos": grupos})
                
                if method == 'POST' and current_user:
                    body = await request.json()
                    grupo_id = await create_study_group(
                        db, body.get('nome'),
                        current_user['id'],
                        body.get('descricao'),
                        body.get('is_public', True),
                        body.get('max_membros', 50)
                    )
                    return json_response({"id": grupo_id}, 201)
            
            if path.startswith('/api/grupos/') and '/entrar' in path:
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                grupo_id = path.split('/')[3]
                success, error = await join_study_group(db, grupo_id, current_user['id'])
                if error:
                    return json_response({"error": error}, 400)
                return json_response({"success": True})
            
            if path.startswith('/api/grupos/') and '/sair' in path:
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                grupo_id = path.split('/')[3]
                await leave_study_group(db, grupo_id, current_user['id'])
                return json_response({"success": True})
            
            if path.startswith('/api/grupos/') and '/mensagens' in path:
                grupo_id = path.split('/')[3]
                
                if method == 'GET':
                    page = int(params.get('page', ['1'])[0])
                    messages = await get_group_messages(db, grupo_id, page)
                    return json_response({"messages": messages})
                
                if method == 'POST' and current_user:
                    body = await request.json()
                    msg_id = await send_group_message(
                        db, grupo_id, current_user['id'],
                        body.get('conteudo')
                    )
                    return json_response({"id": msg_id}, 201)
            
            # ================================================================
            # ACESSIBILIDADE (Libras e Áudio)
            # ================================================================
            
            if path == '/api/acessibilidade':
                tipo = params.get('tipo', [''])[0]
                item_id = params.get('id', [''])[0]
                
                if not tipo or not item_id:
                    return json_response({"error": "tipo e id são obrigatórios"}, 400)
                
                content = await get_accessibility_content(db, tipo, item_id)
                return json_response(content or {})
            
            # Admin: salvar conteúdo de acessibilidade
            if path == '/api/admin/acessibilidade' and method == 'POST':
                if not current_user or not current_user.get('is_admin'):
                    return json_response({"error": "Admin apenas"}, 403)
                
                body = await request.json()
                await save_accessibility_content(
                    db, body.get('tipo_conteudo'),
                    body.get('conteudo_id'),
                    body.get('video_libras_url'),
                    body.get('audio_url'),
                    body.get('audio_duracao'),
                    body.get('transcricao')
                )
                return json_response({"success": True})
            
            # ================================================================
            # LOGS DE ATIVIDADE (Admin)
            # ================================================================
            
            if path == '/api/admin/logs':
                if not current_user or not current_user.get('is_admin'):
                    return json_response({"error": "Admin apenas"}, 403)
                
                usuario_id = params.get('usuario_id', [None])[0]
                acao = params.get('acao', [None])[0]
                page = int(params.get('page', ['1'])[0])
                
                logs = await get_activity_log(db, usuario_id, acao, page)
                return json_response({"logs": logs})
            
            return json_response({"error": "Rota não encontrada"}, 404)
            
        except Exception as e:
            return json_response({"error": str(e)}, 500)

    async def _logout(self, db, request):
        """Faz logout e redireciona."""
        if db and DB_AVAILABLE:
            try:
                await logout(db, request)
            except:
                pass
        return redirect('/login', headers={"Set-Cookie": clear_session_cookie()})

    async def _index_page(self, db, current_user):
        """Página inicial - Feed/Rede Social."""
        return f"""{page_head("Gramátike")}
    <header class="site-head">
        <h1 class="logo">Gramátike</h1>
    </header>
    <main>
        <div class="card" style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: var(--primary); margin-bottom: 0.5rem;">Bem-vinde ao Gramátike!</h2>
            <p style="color: var(--text-dim); margin-bottom: 1.5rem;">
                Plataforma educacional de gramática portuguesa com foco em inclusão e gênero neutro.
            </p>
            <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                <a href="/login" class="btn btn-primary">Entrar</a>
                <a href="/cadastro" class="btn btn-primary">Criar Conta</a>
            </div>
        </div>
        
        <h2 style="text-align: center; color: var(--primary); margin: 2rem 0 1.5rem;">Explore</h2>
        <div class="modules-grid">
            <a href="/educacao" class="module-card">
                <div class="icon">📚</div>
                <h3>Educação</h3>
                <p>Hub educacional completo</p>
            </a>
            <a href="/dinamicas" class="module-card">
                <div class="icon">🎮</div>
                <h3>Dinâmicas</h3>
                <p>Jogos e atividades</p>
            </a>
            <a href="/exercicios" class="module-card">
                <div class="icon">✏️</div>
                <h3>Exercícios</h3>
                <p>Pratique gramática</p>
            </a>
            <a href="/artigos" class="module-card">
                <div class="icon">📰</div>
                <h3>Artigos</h3>
                <p>Conteúdo educacional</p>
            </a>
            <a href="/apostilas" class="module-card">
                <div class="icon">📖</div>
                <h3>Apostilas</h3>
                <p>Material de estudo</p>
            </a>
            <a href="/podcasts" class="module-card">
                <div class="icon">🎧</div>
                <h3>Podcasts</h3>
                <p>Aprenda ouvindo</p>
            </a>
        </div>
    </main>
{page_footer()}"""

    async def _educacao_page(self, db, current_user):
        """Página Educação - Hub educacional."""
        # Buscar dados do banco se disponível
        palavras = []
        novidades = []
        contents = []
        
        if db and DB_AVAILABLE:
            try:
                palavra = await get_palavra_do_dia_atual(db)
                if palavra:
                    palavras = [palavra]
                novidades = await get_novidades(db, limit=3)
                contents = await get_edu_contents(db, page=1, per_page=10)
            except:
                pass
        
        # Renderizar conteúdos
        contents_html = ""
        if contents:
            for c in contents:
                contents_html += f"""
                <div class="feed-item">
                    <div class="fi-meta">{c.get('tipo', 'artigo').upper()}</div>
                    <h3 class="fi-title">{c.get('titulo', '')}</h3>
                    <p class="fi-body">{(c.get('resumo') or '')[:200]}...</p>
                </div>"""
        else:
            contents_html = '<div class="empty">Nenhum conteúdo encontrado.</div>'
        
        # Palavras do dia
        palavras_html = ""
        if palavras:
            for p in palavras:
                palavras_html += f"""
                <div style="padding: 0.5rem 0;">
                    <strong style="color: var(--primary);">{p.get('palavra', '')}</strong>
                    <p style="font-size: 0.75rem; color: var(--text-dim);">{p.get('significado', '')[:100]}...</p>
                </div>"""
        else:
            palavras_html = '<div class="placeholder">Nenhuma palavra disponível</div>'
        
        # Novidades
        novidades_html = ""
        if novidades:
            for n in novidades:
                novidades_html += f"""
                <div style="padding: 0.5rem 0; border-bottom: 1px solid var(--border);">
                    <strong style="font-size: 0.8rem;">{n.get('titulo', '')}</strong>
                </div>"""
        else:
            novidades_html = '<div class="placeholder">Nenhuma novidade.</div>'
        
        return f"""{page_head("Gramátike Edu")}
    <header class="site-head">
        <h1 class="logo">Gramátike Edu</h1>
        <nav class="edu-nav">
            <a href="/educacao" class="active">🏠 Início</a>
            <a href="/apostilas">📖 Apostilas</a>
            <a href="/exercicios">✏️ Exercícios</a>
            <a href="/artigos">📰 Artigos</a>
        </nav>
    </header>
    <main>
        <div class="search-box">
            <input type="text" placeholder="Buscar posts do @gramatike...">
            <button class="search-btn">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
                    <circle cx="11" cy="11" r="7"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
            </button>
        </div>
        
        <div class="layout">
            <div>
                {contents_html}
            </div>
            <aside class="side-col">
                <div class="quick-nav">
                    <a href="/dinamicas">🎮 Dinâmicas</a>
                    <a href="/">💬 Gramátike</a>
                </div>
                <div class="side-card">
                    <h3>💡 Palavras do Dia</h3>
                    {palavras_html}
                </div>
                <div class="side-card">
                    <h3>📣 Novidades</h3>
                    {novidades_html}
                </div>
            </aside>
        </div>
    </main>
{page_footer()}"""

    async def _login_page(self, db, current_user, request, method):
        """Página de Login."""
        # Se já logado, redireciona
        if current_user:
            return redirect('/')
        
        error_msg = ""
        
        # Processar form de login
        if method == 'POST' and db and DB_AVAILABLE:
            try:
                # Ler form data
                body_text = await request.text()
                form_data = parse_qs(body_text)
                
                email = form_data.get('email', [''])[0].strip()
                password = form_data.get('password', [''])[0]
                
                if email and password:
                    token, err = await login(db, request, email, password)
                    if token:
                        return redirect('/', headers={"Set-Cookie": set_session_cookie(token)})
                    else:
                        error_msg = err or "Credenciais inválidas"
                else:
                    error_msg = "Preencha todos os campos"
            except Exception as e:
                error_msg = f"Erro ao processar login"
        
        error_html = f'<div class="error-msg" style="background:#ffebee;color:#c62828;padding:0.8rem;border-radius:10px;margin-bottom:1rem;font-size:0.85rem;">{error_msg}</div>' if error_msg else ""
        
        extra_css = """
        .login-wrapper { flex:1; display:flex; align-items:flex-start; justify-content:center; padding:2.2rem 1.2rem 3.5rem; }
        .login-card { width:100%; max-width:380px; background:#fff; border-radius:18px; padding:2.2rem 2rem 2.4rem; box-shadow:0 10px 26px -4px rgba(0,0,0,.12); }
        .login-card h2 { margin:0 0 1.4rem; font-size:1.55rem; font-weight:800; text-align:center; }
        .signup-hint { text-align:center; margin-top:1.6rem; font-size:.85rem; }
        .signup-hint a { color: var(--primary); text-decoration: none; font-weight: 700; }
        .signup-hint a:hover { text-decoration: underline; }
        header.site-head { display: none; }
        footer { display: none; }
        """
        return f"""{page_head("Entrar • Gramátike", extra_css)}
    <div class="login-wrapper">
        <div class="login-card">
            {error_html}
            <h2>Entrar</h2>
            <form method="POST" action="/login">
                <div class="form-group">
                    <label>Usuárie / Email</label>
                    <input type="text" name="email" placeholder="Usuárie ou email" required>
                </div>
                <div class="form-group">
                    <label>Senha</label>
                    <input type="password" name="password" placeholder="••••••••" required>
                </div>
                <button type="submit" class="button-primary" style="margin-top: 1rem;">Entrar</button>
            </form>
            <div class="signup-hint">
                Ainda não tem conta? <a href="/cadastro">Cadastre-se</a>
            </div>
        </div>
    </div>
    {mobile_nav()}
</body>
</html>"""

    async def _cadastro_page(self, db, current_user, request, method):
        """Página de Cadastro."""
        # Se já logado, redireciona
        if current_user:
            return redirect('/')
        
        error_msg = ""
        success_msg = ""
        
        # Processar form de cadastro
        if method == 'POST' and db and DB_AVAILABLE:
            try:
                body_text = await request.text()
                form_data = parse_qs(body_text)
                
                username = form_data.get('username', [''])[0].strip()
                email = form_data.get('email', [''])[0].strip()
                password = form_data.get('password', [''])[0]
                nome = form_data.get('nome', [''])[0].strip() or None
                
                if username and email and password:
                    user_id, err = await register(db, username, email, password, nome)
                    if user_id:
                        # Auto-login
                        token, _ = await login(db, request, email, password)
                        if token:
                            return redirect('/', headers={"Set-Cookie": set_session_cookie(token)})
                        success_msg = "Conta criada! Faça login."
                    else:
                        error_msg = err or "Erro ao criar conta"
                else:
                    error_msg = "Preencha todos os campos obrigatórios"
            except Exception as e:
                error_msg = "Erro ao processar cadastro"
        
        error_html = f'<div class="error-msg" style="background:#ffebee;color:#c62828;padding:0.8rem;border-radius:10px;margin-bottom:1rem;font-size:0.85rem;">{error_msg}</div>' if error_msg else ""
        success_html = f'<div class="success-msg" style="background:#e8f5e9;color:#2e7d32;padding:0.8rem;border-radius:10px;margin-bottom:1rem;font-size:0.85rem;">{success_msg}</div>' if success_msg else ""
        
        extra_css = """
        .login-wrapper { flex:1; display:flex; align-items:flex-start; justify-content:center; padding:2.2rem 1.2rem 3.5rem; }
        .login-card { width:100%; max-width:380px; background:#fff; border-radius:18px; padding:2.2rem 2rem 2.4rem; box-shadow:0 10px 26px -4px rgba(0,0,0,.12); }
        .login-card h2 { margin:0 0 1.4rem; font-size:1.55rem; font-weight:800; text-align:center; }
        .signup-hint { text-align:center; margin-top:1.6rem; font-size:.85rem; }
        .signup-hint a { color: var(--primary); text-decoration: none; font-weight: 700; }
        header.site-head { display: none; }
        footer { display: none; }
        """
        return f"""{page_head("Cadastro • Gramátike", extra_css)}
    <div class="login-wrapper">
        <div class="login-card">
            {error_html}
            {success_html}
            <h2>Criar Conta</h2>
            <form method="POST" action="/cadastro">
                <div class="form-group">
                    <label>Nome (opcional)</label>
                    <input type="text" name="nome" placeholder="Seu nome">
                </div>
                <div class="form-group">
                    <label>Nome de Usuárie *</label>
                    <input type="text" name="username" placeholder="seu_usuario" required>
                </div>
                <div class="form-group">
                    <label>Email *</label>
                    <input type="email" name="email" placeholder="seu@email.com" required>
                </div>
                <div class="form-group">
                    <label>Senha *</label>
                    <input type="password" name="password" placeholder="••••••••" required minlength="6">
                </div>
                <button type="submit" class="button-primary" style="margin-top: 1rem;">Criar Conta</button>
            </form>
            <div class="signup-hint">
                Já tem conta? <a href="/login">Entrar</a>
            </div>
        </div>
    </div>
    {mobile_nav()}
</body>
</html>"""

    async def _dinamicas_page(self, db, current_user):
        """Página de Dinâmicas."""
        dynamics_html = ""
        
        if db and DB_AVAILABLE:
            try:
                dynamics = await get_dynamics(db)
                if dynamics:
                    for d in dynamics:
                        tipo_emoji = {"poll": "📊", "form": "📝", "oneword": "💬"}.get(d.get('tipo'), '🎮')
                        dynamics_html += f"""
                        <div class="feed-item">
                            <div class="fi-meta">{tipo_emoji} {d.get('tipo', 'dinâmica').upper()}</div>
                            <h3 class="fi-title">{d.get('titulo', '')}</h3>
                            <p class="fi-body">{d.get('descricao') or 'Participe desta dinâmica!'}</p>
                            <div style="margin-top: 1rem;">
                                <span style="font-size: 0.7rem; color: var(--text-dim);">
                                    {d.get('response_count', 0)} participações
                                </span>
                            </div>
                        </div>"""
            except:
                pass
        
        if not dynamics_html:
            dynamics_html = '<div class="empty">Nenhuma dinâmica disponível no momento.</div>'
        
        return f"""{page_head("Dinâmicas — Gramátike Edu")}
    <header class="site-head">
        <h1 class="logo">Dinâmicas</h1>
    </header>
    <main>
        {dynamics_html}
    </main>
{page_footer()}"""

    async def _exercicios_page(self, db, current_user):
        """Página de Exercícios."""
        topics_html = ""
        
        if db and DB_AVAILABLE:
            try:
                topics = await get_exercise_topics(db)
                if topics:
                    for t in topics:
                        topics_html += f"""
                        <div class="feed-item">
                            <h3 class="fi-title">{t.get('nome', '')}</h3>
                            <p class="fi-body">{t.get('descricao') or 'Tópico de exercícios'}</p>
                            <div style="margin-top: 0.8rem;">
                                <span style="font-size: 0.7rem; color: var(--text-dim); background: #f1edff; padding: 0.3rem 0.6rem; border-radius: 10px;">
                                    {t.get('question_count', 0)} questões
                                </span>
                            </div>
                        </div>"""
            except:
                pass
        
        if not topics_html:
            topics_html = '<div class="empty">Nenhum exercício disponível.</div>'
        
        return f"""{page_head("Gramátike Edu — Exercícios")}
    <header class="site-head">
        <h1 class="logo">Gramátike Edu</h1>
        <nav class="edu-nav">
            <a href="/educacao">🏠 Início</a>
            <a href="/apostilas">📖 Apostilas</a>
            <a href="/exercicios" class="active">✏️ Exercícios</a>
            <a href="/artigos">📰 Artigos</a>
        </nav>
    </header>
    <main>
        <div class="search-box">
            <input type="text" placeholder="Pesquisar exercícios...">
            <button class="search-btn">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
                    <circle cx="11" cy="11" r="7"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
            </button>
        </div>
        {topics_html}
    </main>
{page_footer()}"""

    async def _artigos_page(self, db, current_user):
        """Página de Artigos."""
        artigos_html = ""
        
        if db and DB_AVAILABLE:
            try:
                artigos = await get_edu_contents(db, tipo='artigo', page=1, per_page=20)
                if artigos:
                    for a in artigos:
                        artigos_html += f"""
                        <div class="feed-item">
                            <div class="fi-meta">ARTIGO</div>
                            <h3 class="fi-title">{a.get('titulo', '')}</h3>
                            <p class="fi-body">{(a.get('resumo') or '')[:200]}...</p>
                        </div>"""
            except:
                pass
        
        if not artigos_html:
            artigos_html = '<div class="empty">Nenhum artigo disponível.</div>'
        
        return f"""{page_head("Gramátike Edu — Artigos")}
    <header class="site-head">
        <h1 class="logo">Gramátike Edu</h1>
        <nav class="edu-nav">
            <a href="/educacao">🏠 Início</a>
            <a href="/apostilas">📖 Apostilas</a>
            <a href="/exercicios">✏️ Exercícios</a>
            <a href="/artigos" class="active">📰 Artigos</a>
        </nav>
    </header>
    <main>
        <div class="search-box">
            <input type="text" placeholder="Pesquisar artigos...">
            <button class="search-btn">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
                    <circle cx="11" cy="11" r="7"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
            </button>
        </div>
        {artigos_html}
    </main>
{page_footer()}"""

    async def _apostilas_page(self, db, current_user):
        """Página de Apostilas."""
        apostilas_html = ""
        
        if db and DB_AVAILABLE:
            try:
                apostilas = await get_edu_contents(db, tipo='apostila', page=1, per_page=20)
                if apostilas:
                    for a in apostilas:
                        apostilas_html += f"""
                        <div class="feed-item">
                            <div class="fi-meta">📖 APOSTILA</div>
                            <h3 class="fi-title">{a.get('titulo', '')}</h3>
                            <p class="fi-body">{(a.get('resumo') or '')[:200]}...</p>
                            {'<a href="' + a.get("url", "") + '" class="btn btn-primary" style="margin-top: 0.8rem; font-size: 0.75rem;">Baixar PDF</a>' if a.get("url") else ''}
                        </div>"""
            except:
                pass
        
        if not apostilas_html:
            apostilas_html = '<div class="empty">Nenhuma apostila disponível.</div>'
        
        return f"""{page_head("Gramátike Edu — Apostilas")}
    <header class="site-head">
        <h1 class="logo">Gramátike Edu</h1>
        <nav class="edu-nav">
            <a href="/educacao">🏠 Início</a>
            <a href="/apostilas" class="active">📖 Apostilas</a>
            <a href="/exercicios">✏️ Exercícios</a>
            <a href="/artigos">📰 Artigos</a>
        </nav>
    </header>
    <main>
        <div class="search-box">
            <input type="text" placeholder="Pesquisar apostilas...">
            <button class="search-btn">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
                    <circle cx="11" cy="11" r="7"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
            </button>
        </div>
        {apostilas_html}
    </main>
{page_footer()}"""

    async def _podcasts_page(self, db, current_user):
        """Página de Podcasts."""
        podcasts_html = ""
        
        if db and DB_AVAILABLE:
            try:
                podcasts = await get_edu_contents(db, tipo='podcast', page=1, per_page=20)
                if podcasts:
                    for p in podcasts:
                        podcasts_html += f"""
                        <div class="feed-item">
                            <div class="fi-meta">🎧 PODCAST</div>
                            <h3 class="fi-title">{p.get('titulo', '')}</h3>
                            <p class="fi-body">{(p.get('resumo') or '')[:200]}...</p>
                            {'<a href="' + p.get("url", "") + '" class="btn btn-primary" style="margin-top: 0.8rem; font-size: 0.75rem;" target="_blank">Ouvir</a>' if p.get("url") else ''}
                        </div>"""
            except:
                pass
        
        if not podcasts_html:
            podcasts_html = '<div class="empty">Nenhum podcast disponível.</div>'
        
        return f"""{page_head("Gramátike Edu — Podcasts")}
    <header class="site-head">
        <h1 class="logo">Gramátike Edu</h1>
        <nav class="edu-nav">
            <a href="/educacao">🏠 Início</a>
            <a href="/apostilas">📖 Apostilas</a>
            <a href="/exercicios">✏️ Exercícios</a>
            <a href="/artigos">📰 Artigos</a>
        </nav>
    </header>
    <main>
        <div class="search-box">
            <input type="text" placeholder="Pesquisar podcasts...">
            <button class="search-btn">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
                    <circle cx="11" cy="11" r="7"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
            </button>
        </div>
        {podcasts_html}
    </main>
{page_footer()}"""

    async def _profile_page(self, db, current_user, username):
        """Página de perfil de usuário."""
        if not db or not DB_AVAILABLE:
            return self._not_found_page(f'/u/{username}')
        
        try:
            user = await get_user_by_username(db, username)
            if not user:
                return self._not_found_page(f'/u/{username}')
            
            # Buscar posts de usuárie
            posts = await get_posts(db, user_id=user['id'], per_page=20)
            
            # Buscar seguidories/seguindo
            followers = await get_followers(db, user['id'])
            following = await get_following(db, user['id'])
            
            # Verificar se usuárie logade segue
            is_following_user = False
            is_own_profile = False
            if current_user:
                is_own_profile = current_user['id'] == user['id']
                if not is_own_profile:
                    is_following_user = await is_following(db, current_user['id'], user['id'])
            
            # Gerar HTML dos posts
            posts_html = ""
            if posts:
                for p in posts:
                    posts_html += f"""
                    <div class="feed-item">
                        <p class="fi-body">{p.get('conteudo', '')}</p>
                        <div style="margin-top: 0.8rem; font-size: 0.7rem; color: var(--text-dim);">
                            ❤️ {p.get('like_count', 0)} • 💬 {p.get('comment_count', 0)}
                        </div>
                    </div>"""
            else:
                posts_html = '<div class="empty">Nenhum post ainda.</div>'
            
            # Botão de seguir/editar
            action_btn = ""
            if current_user:
                if is_own_profile:
                    action_btn = '<a href="/editar-perfil" class="btn btn-primary">Editar Perfil</a>'
                else:
                    btn_text = "Deixar de Seguir" if is_following_user else "Seguir"
                    action_btn = f'<button onclick="toggleFollow(\'{username}\')" class="btn btn-primary" id="follow-btn">{btn_text}</button>'
            
            return f"""{page_head(f"@{username} — Gramátike")}
    <header class="site-head">
        <h1 class="logo">Gramátike</h1>
    </header>
    <main>
        <div class="card" style="text-align: center; margin-bottom: 1.5rem;">
            <img src="{user.get('foto_perfil', '/static/img/perfil.png')}" 
                 alt="@{username}" 
                 style="width: 80px; height: 80px; border-radius: 50%; margin-bottom: 1rem; object-fit: cover;">
            <h2 style="color: var(--primary); margin-bottom: 0.3rem;">
                {user.get('nome') or '@' + username}
            </h2>
            <p style="color: var(--text-dim); font-size: 0.85rem; margin-bottom: 0.8rem;">@{username}</p>
            {f'<p style="margin-bottom: 1rem;">{user.get("bio", "")}</p>' if user.get('bio') else ''}
            <div style="display: flex; gap: 2rem; justify-content: center; margin-bottom: 1rem; font-size: 0.85rem;">
                <span><strong>{len(followers)}</strong> seguidories</span>
                <span><strong>{len(following)}</strong> seguindo</span>
            </div>
            {action_btn}
        </div>
        
        <h3 style="color: var(--primary); margin-bottom: 1rem;">Posts</h3>
        {posts_html}
    </main>
    <script>
    async function toggleFollow(username) {{
        const btn = document.getElementById('follow-btn');
        try {{
            const res = await fetch('/api/usuario/' + username + '/seguir', {{method: 'POST'}});
            const data = await res.json();
            btn.textContent = data.following ? 'Deixar de Seguir' : 'Seguir';
        }} catch(e) {{
            console.error(e);
        }}
    }}
    </script>
{page_footer()}"""
        except Exception as e:
            return self._not_found_page(f'/u/{username}')

    def _not_found_page(self, path):
        """Página 404."""
        return f"""{page_head("Página não encontrada — Gramátike")}
    <header class="site-head">
        <h1 class="logo">Gramátike</h1>
    </header>
    <main>
        <div class="card" style="text-align: center;">
            <h2 style="color: var(--primary);">Página não encontrada</h2>
            <p style="color: var(--text-dim); margin: 1rem 0;">
                A página <code style="background: #f1edff; padding: 2px 8px; border-radius: 6px;">{path}</code> não existe.
            </p>
            <a href="/" class="btn btn-primary">Voltar ao início</a>
        </div>
    </main>
{page_footer()}"""
