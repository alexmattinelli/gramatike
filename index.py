# index.py
# Cloudflare Workers Python entry point with D1 Database
# Uses native WorkerEntrypoint pattern + D1 SQLite
# Docs: https://developers.cloudflare.com/workers/languages/python/
#
# Este arquivo serve as páginas HTML com a mesma estética e funcionalidades
# da aplicação Flask original, usando Cloudflare D1 como banco de dados.
# Usa linguagem neutra (usuáries, seguidories, amigues).

import json
import sys
import traceback
from urllib.parse import urlparse, parse_qs, unquote

# Import JavaScript console for proper log levels in Cloudflare Workers
# console.log = info level, console.warn = warning, console.error = error
try:
    from js import console
except ImportError:
    # Fallback for local testing - create a mock console
    class MockConsole:
        def log(self, *args): print(*args)
        def info(self, *args): print(*args)
        def warn(self, *args): print(*args, file=sys.stderr)
        def error(self, *args): print(*args, file=sys.stderr)
    console = MockConsole()

# Versão do código - usado para tracking de deployment
# Atualize este valor a cada commit para verificar se o deploy foi feito
SCRIPT_VERSION = "v2025.12.03.a"

# Importar template processor para carregar templates HTML externos
# Isso separa o HTML do código Python para facilitar manutenção
try:
    from functions._template_processor import render_template, load_template, create_error_html, create_success_html
    TEMPLATES_AVAILABLE = True
except ImportError:
    TEMPLATES_AVAILABLE = False
    def render_template(name, **ctx): return f"<h1>Template {name} não disponível</h1>"
    def load_template(name): return f"<h1>Template {name} não disponível</h1>"
    def create_error_html(msg): return f'<div class="error">{msg}</div>'
    def create_success_html(msg): return f'<div class="success">{msg}</div>'

# NOTA: Este 'workers' é o módulo built-in do Cloudflare Workers Python,
# NÃO a pasta local (que foi renomeada para 'gramatike_d1').
from workers import WorkerEntrypoint, Response

# Importar módulos de banco de dados e autenticação
# NOTA: Usamos 'gramatike_d1' em vez de 'workers' para evitar conflito com o
# módulo 'workers' built-in do Cloudflare Workers Python (que fornece WorkerEntrypoint e Response)
try:
    from gramatike_d1.db import (
        # Auto-inicialização
        ensure_database_initialized,
        # Helpers
        safe_dict, sanitize_for_d1, sanitize_params,
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
        # Mensagens diretas (desativado por padrão)
        send_direct_message, get_conversations, get_messages_with_user,
        # Grupos de estudo (desativado por padrão)
        create_study_group, join_study_group, leave_study_group,
        get_study_groups, get_group_messages, send_group_message,
        # Acessibilidade
        get_accessibility_content, save_accessibility_content,
        # Validação de senha
        validate_password_strength,
        # Menções (@) e Hashtags (#)
        extract_mentions, process_mentions, get_user_mentions,
        extract_hashtags, process_hashtags, get_trending_hashtags, search_by_hashtag,
        # Emojis personalizados
        create_emoji_custom, get_emojis_custom, get_emoji_by_codigo,
        update_emoji_custom, delete_emoji_custom, get_emoji_categories, render_emojis_in_text,
        # Feature flags
        get_feature_flag, get_all_feature_flags, update_feature_flag
    )
    from gramatike_d1.auth import (
        get_current_user, login, logout, register,
        set_session_cookie, clear_session_cookie
    )
    DB_AVAILABLE = True
except ImportError as e:
    # Log the specific import error for debugging
    print(f"[D1 Import Error] {e}", file=sys.stderr)
    DB_AVAILABLE = False
    # Define placeholder for ensure_database_initialized
    async def ensure_database_initialized(db):
        return False
    # Define placeholder for safe_dict
    def safe_dict(result):
        if result is None:
            return None
        try:
            return dict(result)
        except (TypeError, ValueError):
            return None


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


def escape_html(text):
    """Escape HTML special characters to prevent XSS."""
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#x27;").replace("/", "&#x2F;")


def normalize_image_url(url, default="/static/img/perfil.png"):
    """Normalize image URL - prepend /static/ if not an absolute URL."""
    if not url or not str(url).strip():
        return default
    url = str(url).strip()
    if url.startswith('http://') or url.startswith('https://'):
        return url
    if url.startswith('/static/'):
        return url
    return f"/static/{url}"


def escape_js_string(text):
    """Escape string for safe inclusion in JavaScript."""
    if not text:
        return ""
    return str(text).replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t").replace("<", "\\u003c").replace(">", "\\u003e").replace("</", "<\\/")


# MIME type mapping for static files
STATIC_MIME_TYPES = {
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.webp': 'image/webp',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.webmanifest': 'application/manifest+json',
    '.json': 'application/json; charset=utf-8',
    '.html': 'text/html; charset=utf-8',
    '.txt': 'text/plain; charset=utf-8',
    '.xml': 'application/xml; charset=utf-8',
}


def get_mime_type(file_path):
    """Get MIME type based on file extension."""
    for ext, mime_type in STATIC_MIME_TYPES.items():
        if file_path.endswith(ext):
            return mime_type
    return 'application/octet-stream'


def is_safe_static_path(file_path):
    """
    Check if a static file path is safe (no path traversal).
    
    Returns True if the path is safe, False otherwise.
    """
    # Decode URL encoding first to catch %2e%2e -> ..
    decoded_path = unquote(file_path)
    
    # Check for path traversal attempts
    if '..' in decoded_path:
        return False
    
    # Check for null bytes (could be used to truncate paths)
    if '\x00' in decoded_path:
        return False
    
    # Check for home directory traversal on Unix systems
    if decoded_path.startswith('~'):
        return False
    
    # Check for absolute paths (starting with / or \)
    # Note: the file_path comes from path[8:] after '/static/' is removed,
    # so it should never normally start with / unless the URL was malformed
    if decoded_path.startswith('/') or decoded_path.startswith('\\'):
        return False
    
    return True


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

/* Content wrapper (área clarinha com borda curva no topo) */
.content-wrapper {
    background: var(--bg);
    flex: 1;
    border-top-left-radius: 35px;
    border-top-right-radius: 35px;
    margin-top: -30px;
    padding-top: 30px;
    position: relative;
    z-index: 1;
}

/* Header (sem curvas - apenas a área de conteúdo terá bordas arredondadas) */
header.site-head {
    background: var(--primary);
    padding: 28px clamp(16px, 4vw, 40px) 46px;
    border-radius: 0;
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

/* Footer simples (apenas texto) */
.footer-text {
    margin-top: auto;
    text-align: center;
    padding: 1rem;
    font-size: 0.8rem;
    letter-spacing: 0.4px;
    font-weight: 600;
    color: var(--text-dim);
}

/* Mobile bottom nav - floating rounded bar style from index.html */
.mobile-bottom-nav {
    display: none;
    position: fixed;
    bottom: 12px;
    left: 12px;
    right: 12px;
    background: var(--primary);
    border-radius: 24px;
    padding: 10px 8px calc(10px + env(safe-area-inset-bottom));
    box-shadow: 0 4px 20px rgba(155, 93, 229, 0.4);
    z-index: 1000;
}
.mobile-bottom-nav a, .mobile-bottom-nav button, .mobile-bottom-nav div {
    all: unset;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    padding: 6px 12px;
    cursor: pointer;
    color: #ffffff;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.3px;
    transition: opacity 0.2s;
    text-decoration: none;
}
.mobile-bottom-nav a:active, .mobile-bottom-nav button:active {
    transform: scale(0.95);
}
.mobile-bottom-nav a svg, .mobile-bottom-nav button svg {
    color: #ffffff;
    transition: opacity 0.2s;
}
.mobile-bottom-nav a:hover, .mobile-bottom-nav button:hover {
    opacity: 0.85;
}

/* Mobile */
@media (max-width: 980px) {
    header.site-head { padding: 12px clamp(12px, 3vw, 24px) 18px; }
    .logo { font-size: 1.5rem; }
    .edu-nav { display: none !important; }
    .quick-nav { display: none !important; }
    footer { display: none !important; }
    .mobile-bottom-nav {
        display: flex;
        justify-content: space-around;
        align-items: center;
    }
    main { margin-bottom: calc(80px + env(safe-area-inset-bottom)) !important; }
    .side-col { display: none; }
    /* Mostrar triângulo toggle no mobile */
    #mobile-toggle-triangle { display: block !important; }
    /* Card de ações inicialmente escondido no mobile */
    #mobile-actions-card { display: none !important; }
    #mobile-actions-card.visible { display: block !important; }
}

/* Mobile toggle triangle */
#mobile-toggle-triangle {
    display: none;
    width: 100%;
    text-align: center;
    margin-bottom: 0.5rem;
    cursor: pointer;
}
#triangle-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: var(--primary);
    width: 40px;
    height: 24px;
    border-radius: 0 0 12px 12px;
    box-shadow: 0 4px 12px rgba(155,93,229,0.3);
    transition: transform 0.2s;
}
#triangle-svg { transition: transform 0.2s; }

/* Mobile actions card - hidden by default, only shown on mobile */
#mobile-actions-card {
    display: none;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 1.3rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    margin-bottom: 1rem;
}
.mobile-actions-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.6rem;
}
.action-btn {
    width: 48px;
    height: 48px;
    border: none;
    background: var(--primary);
    color: #fff;
    border-radius: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(130,87,229,0.45);
    position: relative;
}
.action-btn:hover { background: var(--primary-dark); }
.action-badge {
    position: absolute;
    top: -4px;
    right: -4px;
    background: #ff9800;
    color: #fff;
    font-size: 0.6rem;
    padding: 2px 5px;
    border-radius: 10px;
    font-weight: 700;
}

/* Notifications panel */
#notifications-panel {
    margin-top: 0.8rem;
    border-top: 1px solid var(--border);
    padding-top: 0.8rem;
}
.notif-item {
    display: block;
    padding: 0.7rem;
    background: #f9fbfd;
    border: 1px solid #e3e9f0;
    border-radius: 12px;
    text-decoration: none;
    margin-bottom: 0.5rem;
    transition: 0.2s;
}
.notif-item:hover { background: #f1edff; }

/* Mobile panels */
#mobile-amigues-panel, #mobile-ttt-panel {
    margin-top: 0.8rem;
    border-top: 1px solid var(--border);
    padding-top: 0.8rem;
}

/* Tic-tac-toe */
.ttt-board {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
}
.ttt-cell {
    height: 56px;
    border: 1px solid var(--border);
    border-radius: 14px;
    background: #fff;
    color: var(--primary);
    font-weight: 900;
    font-size: 1.1rem;
    cursor: pointer;
    box-shadow: 0 4px 10px rgba(0,0,0,0.06);
}
.ttt-cell:hover { background: #f8f5ff; }
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
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    <link rel="icon" type="image/png" href="/static/favicon.png">
    <link href="https://fonts.googleapis.com/css2?family=Mansalva&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>{BASE_CSS}{extra_css}</style>
</head>
<body>"""

def mobile_nav(is_authenticated=False):
    """Generate mobile bottom navigation bar - matching index.html style."""
    profile_link = """
        <a href="/perfil" aria-label="Perfil" title="Perfil">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
            </svg>
            <span>Perfil</span>
        </a>""" if is_authenticated else """
        <a href="/login" aria-label="Entrar" title="Entrar">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
                <polyline points="10 17 15 12 10 7"></polyline>
                <line x1="15" y1="12" x2="3" y2="12"></line>
            </svg>
            <span>Entrar</span>
        </a>"""
    
    return f"""
    <nav class="mobile-bottom-nav" aria-label="Navegação principal mobile">
        <a href="/" aria-label="Feed" title="Feed">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            <span>Início</span>
        </a>
        <a href="/educacao" aria-label="Educação" title="Educação">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
            <span>Educação</span>
        </a>
        <a href="/novo-post" aria-label="Criar post" title="Criar post" style="background: var(--primary); color: #ffffff; border-radius: 50%; width: 48px; height: 48px; margin: -10px 0; padding: 0; display: flex; align-items: center; justify-content: center; flex-direction: row; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border: 3px solid #ffffff;">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
        </a>
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; padding: 6px 12px; color: rgba(255,255,255,0.6); font-size: 0.65rem; font-weight: 600; letter-spacing: 0.3px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            <span>Em breve</span>
        </div>
        {profile_link}
    </nav>"""

def page_footer(is_authenticated=False):
    """Generate page footer with mobile navigation."""
    return f"""
    <div class="footer-text">© 2025 Gramátike • Língua Viva e de Todes</div>
    {mobile_nav(is_authenticated)}
</body>
</html>"""


class Default(WorkerEntrypoint):
    """Cloudflare Worker entry point with D1 Database support."""

    async def fetch(self, request):
        """Handle incoming HTTP requests."""
        # Log da versão do script no início para tracking
        # Use console.log for informational logs (appears as "log" level, not "error")
        console.log(f"[Gramátike] Script Version: {SCRIPT_VERSION}")
        
        url = request.url
        path = "/"
        query_params = {}
        
        try:
            if url:
                parsed = urlparse(url)
                path = parsed.path or "/"
                query_params = parse_qs(parsed.query)
            
            method = request.method
            
            # Obter banco de dados D1
            db = getattr(self.env, 'DB', None)
            
            # Auto-inicializar banco de dados (cria tabelas e superadmin se necessário)
            if db and DB_AVAILABLE:
                try:
                    await ensure_database_initialized(db)
                except Exception as e:
                    # Warnings use console.warn
                    console.warn(f"[D1 Init Warning] {e}")
            
            # Obter usuárie atual se DB disponível
            current_user = None
            if db and DB_AVAILABLE:
                try:
                    current_user = await get_current_user(db, request)
                except Exception as e:
                    # Warnings use console.warn
                    console.warn(f"[Auth Warning] get_current_user failed: {e}")
            
            # ====================================================================
            # STATIC FILES ROUTES
            # ====================================================================
            
            if path.startswith('/static/'):
                # Serve static files from the ASSETS binding
                assets = getattr(self.env, 'ASSETS', None)
                if assets:
                    # Strip the /static/ prefix to get the actual file path
                    file_path = path[8:]  # Remove '/static/'
                    
                    # Security: prevent path traversal attacks
                    if not is_safe_static_path(file_path):
                        return Response("Forbidden", status=403, headers={"Content-Type": "text/plain"})
                    
                    try:
                        # Fetch the asset using the ASSETS binding
                        asset_response = await assets.fetch(f"https://assets/{file_path}")
                        if asset_response.status == 200:
                            # Get content from the response
                            content = await asset_response.arrayBuffer()
                            
                            # Determine content type based on file extension
                            content_type = get_mime_type(file_path)
                            
                            return Response(
                                content,
                                status=200,
                                headers={
                                    "Content-Type": content_type,
                                    "Cache-Control": "public, max-age=31536000, immutable"
                                }
                            )
                    except Exception as e:
                        console.warn(f"[Static] Error serving {file_path}: {e}")
                
                # Return 404 if asset not found or ASSETS binding not available
                return Response("Not Found", status=404, headers={"Content-Type": "text/plain"})
            
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
                "/dinamicas/admin": lambda: self._dinamica_admin_page(db, current_user),
                "/exercicios": lambda: self._exercicios_page(db, current_user),
                "/artigos": lambda: self._artigos_page(db, current_user),
                "/apostilas": lambda: self._apostilas_page(db, current_user),
                "/podcasts": lambda: self._podcasts_page(db, current_user),
                "/logout": lambda: self._logout(db, request),
                "/novo-post": lambda: self._novo_post_page(db, current_user, request, method),
                "/novo_post": lambda: self._novo_post_page(db, current_user, request, method),
                "/perfil": lambda: self._meu_perfil_page(db, current_user),
                "/configuracoes": lambda: self._configuracoes_page(db, current_user),
                "/admin": lambda: self._admin_page(db, current_user),
                "/admin/usuarios": lambda: self._gerenciar_usuarios_page(db, current_user),
                "/esqueci-senha": lambda: self._esqueci_senha_page(db, current_user, request, method),
                "/reset-senha": lambda: self._reset_senha_page(db, current_user, request, method),
                "/suporte": lambda: self._suporte_page(db, current_user),
                "/videos": lambda: self._videos_page(db, current_user),
                "/redacao": lambda: self._redacao_page(db, current_user),
                "/manutencao": lambda: self._manutencao_page(),
            }

            handler = page_routes.get(path)
            if handler:
                result = await self._safe_call(handler)
                if isinstance(result, Response):
                    return result
                return html_response(result)
            
            # Rotas dinâmicas (perfil de usuárie)
            if path.startswith('/u/'):
                username = path[3:]
                result = await self._profile_page(db, current_user, username)
                return html_response(result) if not isinstance(result, Response) else result
            
            # Rota dinâmica para post detail
            if path.startswith('/post/'):
                post_id = path[6:]
                result = await self._post_detail_page(db, current_user, post_id)
                return html_response(result) if not isinstance(result, Response) else result
            
            # Rota dinâmica para novidade detail
            if path.startswith('/novidade/'):
                novidade_id = path[10:]
                result = await self._novidade_detail_page(db, current_user, novidade_id)
                return html_response(result) if not isinstance(result, Response) else result
            
            # Rota dinâmica para visualizar dinâmica
            if path.startswith('/dinamica/') and '/editar' not in path:
                dinamica_id = path[10:]
                result = await self._dinamica_view_page(db, current_user, dinamica_id)
                return html_response(result) if not isinstance(result, Response) else result
            
            # Rota dinâmica para editar dinâmica
            if path.startswith('/dinamica/') and path.endswith('/editar'):
                dinamica_id = path[10:-7]  # Remove '/dinamica/' e '/editar'
                result = await self._dinamica_edit_page(db, current_user, dinamica_id)
                return html_response(result) if not isinstance(result, Response) else result
            
            return html_response(self._not_found_page(path), status=404)
            
        except Exception as e:
            # Log detalhado de qualquer erro não capturado - use console.error for actual errors
            console.error(f"[Fetch Error] {type(e).__name__}: {e}")
            console.error(f"[Fetch Traceback] {traceback.format_exc()}")
            error_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><title>Erro — Gramátike</title><meta charset="UTF-8"></head>
<body style="font-family: sans-serif; padding: 2rem; text-align: center;">
<h1 style="color: #9B5DE5;">Erro Interno</h1>
<p>Ocorreu um erro ao processar sua requisição.</p>
<p style="font-size: 0.8rem; color: #666;">Versão: {SCRIPT_VERSION}</p>
<a href="/" style="color: #9B5DE5;">Voltar ao início</a>
</body>
</html>"""
            return html_response(error_html, status=500)

    async def _safe_call(self, handler):
        """Chama handler de forma segura com logging detalhado."""
        try:
            result = handler()
            if hasattr(result, '__await__'):
                result = await result
            return result
        except Exception as e:
            # Log detalhado do erro - use console.error for actual errors
            console.error(f"[SafeCall Error] {type(e).__name__}: {e}")
            console.error(f"[SafeCall Traceback] {traceback.format_exc()}")
            return f"<h1>Erro</h1><p>{str(e)}</p><p style='font-size:0.7rem;color:#666;'>Versão: {SCRIPT_VERSION}</p>"

    async def _handle_api(self, request, path, method, params, db, current_user):
        """Handle API routes."""
        
        # Health check (não precisa de DB)
        if path == '/api/health':
            return json_response({
                "status": "ok",
                "platform": "Cloudflare Workers + D1",
                "db_available": db is not None and DB_AVAILABLE,
                "script_version": SCRIPT_VERSION
            })
        
        if path == '/api/info':
            return json_response({
                "name": "Gramátike",
                "version": "2.0.0",
                "script_version": SCRIPT_VERSION,
                "features": ["D1 Database", "Auth", "Posts", "Education"]
            })
        
        # Endpoint de diagnóstico do banco de dados
        if path == '/api/db-status':
            if not db or not DB_AVAILABLE:
                return json_response({
                    "status": "unavailable",
                    "db_available": False,
                    "script_version": SCRIPT_VERSION
                }, 503)
            
            try:
                # Contar usuários
                user_count_result = await db.prepare("SELECT COUNT(*) as count FROM user").first()
                user_count = user_count_result['count'] if user_count_result else 0
                
                # Verificar se superadmin existe
                superadmin = await db.prepare(
                    "SELECT id, username FROM user WHERE is_superadmin = 1 LIMIT 1"
                ).first()
                
                # Verificar se usuário 'gramatike' existe
                gramatike_user = await db.prepare(
                    "SELECT id, username, is_admin, is_superadmin FROM user WHERE username = 'gramatike' LIMIT 1"
                ).first()
                
                return json_response({
                    "status": "ok",
                    "db_available": True,
                    "script_version": SCRIPT_VERSION,
                    "user_count": user_count,
                    "superadmin_exists": superadmin is not None,
                    "superadmin_username": dict(superadmin)['username'] if superadmin else None,
                    "gramatike_user": dict(gramatike_user) if gramatike_user else None
                })
            except Exception as e:
                return json_response({
                    "status": "error",
                    "error": str(e),
                    "script_version": SCRIPT_VERSION
                }, 500)
        
        # Se DB não disponível, retorna erro
        if not db or not DB_AVAILABLE:
            return json_response({
                "error": "Database D1 não disponível",
                "help": "Verifique se o banco D1 está configurado no wrangler.toml e se as tabelas foram criadas. Consulte CLOUDFLARE_D1_SETUP.md"
            }, 503)
        
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
                    
                    # Verifica likes de usuárie atual
                    if current_user:
                        for post in posts:
                            post['liked'] = await has_liked(db, current_user['id'], post['id'])
                    
                    return json_response({"posts": posts, "page": page})
                
                elif method == 'POST':
                    if not current_user:
                        return json_response({"error": "Não autenticado"}, 401)
                    
                    body = await request.json()
                    # Handle JsProxy body - convert to Python dict
                    if hasattr(body, 'to_py'):
                        body = body.to_py()
                    
                    # Safely get and sanitize values to prevent D1_TYPE_ERROR
                    conteudo = body.get('conteudo', '') if isinstance(body, dict) else ''
                    conteudo = sanitize_for_d1(conteudo)
                    conteudo = conteudo.strip() if conteudo else ''
                    
                    imagem = body.get('imagem') if isinstance(body, dict) else None
                    imagem = sanitize_for_d1(imagem)
                    
                    if not conteudo:
                        return json_response({"error": "Conteúdo é obrigatório"}, 400)
                    
                    # Sanitize current_user['id'] to ensure it's a proper Python value
                    user_id = sanitize_for_d1(current_user.get('id'))
                    if user_id is None:
                        return json_response({"error": "Usuárie inválide"}, 400)
                    
                    post_id = await create_post(db, user_id, conteudo, imagem)
                    
                    # Processar menções (@username)
                    await process_mentions(db, conteudo, user_id, 'post', post_id)
                    
                    # Processar hashtags (#tag)
                    await process_hashtags(db, conteudo, 'post', post_id)
                    
                    post = await get_post_by_id(db, post_id)
                    return json_response({"post": post}, 201)
            
            # Posts Multi (FormData with multiple images)
            if path == '/api/posts_multi' and method == 'POST':
                if not current_user:
                    return json_response({"error": "Não autenticado", "success": False}, 401)
                
                try:
                    # Get user ID with validation - handle JsProxy for current_user
                    if hasattr(current_user, 'to_py'):
                        current_user_dict = current_user.to_py()
                    elif isinstance(current_user, dict):
                        current_user_dict = current_user
                    else:
                        current_user_dict = safe_dict(current_user)
                    
                    user_id = current_user_dict.get('id') if current_user_dict else None
                    if user_id is None:
                        console.error("[posts_multi] current_user.id is None")
                        return json_response({"error": "Usuárie inválide", "success": False}, 400)
                    
                    # Get content-type header to determine parsing method
                    # In Cloudflare Workers, body can only be consumed ONCE
                    content_type = ''
                    try:
                        headers = request.headers
                        if hasattr(headers, 'get'):
                            content_type = headers.get('content-type', '') or ''
                        elif hasattr(headers, '__getitem__'):
                            try:
                                content_type = headers['content-type'] or ''
                            except (KeyError, TypeError):
                                content_type = ''
                        # Handle JsProxy
                        if hasattr(content_type, 'to_py'):
                            content_type = content_type.to_py()
                        content_type = str(content_type).lower() if content_type else ''
                    except Exception as ct_err:
                        console.warn(f"[posts_multi] Error getting content-type: {ct_err}")
                        content_type = ''
                    
                    console.log(f"[posts_multi] Content-Type: {content_type}")
                    
                    # Parse request body based on content-type
                    # IMPORTANT: Only use ONE parsing method to avoid "body already used" error
                    conteudo = None
                    
                    if 'multipart/form-data' in content_type:
                        # Parse multipart/form-data using text() since arrayBuffer() is not available
                        try:
                            # Use text() which is available in Cloudflare Workers Python
                            body_text = await request.text()
                            if hasattr(body_text, 'to_py'):
                                body_text = body_text.to_py()
                            
                            # Extract boundary from content-type header
                            boundary = None
                            if 'boundary=' in content_type:
                                boundary = content_type.split('boundary=')[1].split(';')[0].strip()
                                if boundary.startswith('"') and boundary.endswith('"'):
                                    boundary = boundary[1:-1]
                            
                            console.log(f"[posts_multi] Boundary: {boundary}")
                            
                            if not boundary:
                                console.warn("[posts_multi] No boundary found in content-type")
                                return json_response({"error": "Erro ao processar formulário: boundary não encontrado", "success": False}, 400)
                            
                            # Split by boundary and find the 'conteudo' field
                            parts = body_text.split('--' + boundary)
                            console.log(f"[posts_multi] Found {len(parts)} parts")
                            
                            for part in parts:
                                # Skip empty parts and closing boundary
                                if not part or part.strip() == '--':
                                    continue
                                
                                if 'name="conteudo"' in part or "name='conteudo'" in part:
                                    # This is the conteudo field - extract the value
                                    if '\r\n\r\n' in part:
                                        value = part.split('\r\n\r\n', 1)[1]
                                    elif '\n\n' in part:
                                        value = part.split('\n\n', 1)[1]
                                    else:
                                        continue
                                    
                                    # Clean up trailing characters
                                    value = value.rstrip('\r\n')
                                    if value.endswith('--'):
                                        value = value[:-2]
                                    value = value.rstrip('\r\n')
                                    
                                    conteudo = value.strip()
                                    console.log(f"[posts_multi] Found conteudo: {conteudo[:50]}..." if len(conteudo) > 50 else f"[posts_multi] Found conteudo: {conteudo}")
                                    break
                            
                            if conteudo is None:
                                console.warn("[posts_multi] Could not find 'conteudo' field in multipart data")
                                
                        except Exception as form_err:
                            console.error(f"[posts_multi] multipart parsing failed: {type(form_err).__name__}: {form_err}")
                            console.error(f"[posts_multi] Traceback: {traceback.format_exc()}")
                            return json_response({"error": "Erro ao processar formulário", "success": False}, 400)
                    
                    elif 'application/json' in content_type:
                        # Use json() for application/json
                        try:
                            body = await request.json()
                            if hasattr(body, 'to_py'):
                                body = body.to_py()
                            conteudo = body.get('conteudo') if isinstance(body, dict) else None
                        except Exception as json_err:
                            console.warn(f"[posts_multi] JSON parse failed: {json_err}")
                            return json_response({"error": "Erro ao processar JSON", "success": False}, 400)
                    
                    elif 'application/x-www-form-urlencoded' in content_type:
                        # Use text() and parse as form-urlencoded
                        try:
                            body_text = await request.text()
                            if hasattr(body_text, 'to_py'):
                                body_text = body_text.to_py()
                            if body_text and isinstance(body_text, str):
                                parsed = parse_qs(body_text)
                                conteudo_list = parsed.get('conteudo', [])
                                if conteudo_list:
                                    conteudo = conteudo_list[0]
                        except Exception as text_err:
                            console.warn(f"[posts_multi] Text parse failed: {text_err}")
                            return json_response({"error": "Erro ao processar formulário", "success": False}, 400)
                    
                    else:
                        # Default: try to parse as text and extract data
                        console.warn(f"[posts_multi] Unknown content-type: {content_type}, trying text parsing")
                        try:
                            body_text = await request.text()
                            if hasattr(body_text, 'to_py'):
                                body_text = body_text.to_py()
                            if body_text and isinstance(body_text, str):
                                # Try to parse as form-urlencoded
                                parsed = parse_qs(body_text)
                                conteudo_list = parsed.get('conteudo', [])
                                if conteudo_list:
                                    conteudo = conteudo_list[0]
                                # If that fails, check if it's JSON
                                elif body_text.strip().startswith('{'):
                                    try:
                                        body_json = json.loads(body_text)
                                        conteudo = body_json.get('conteudo')
                                    except json.JSONDecodeError:
                                        pass
                        except Exception as text_err:
                            console.warn(f"[posts_multi] text parsing failed for unknown content-type: {text_err}")
                            return json_response({"error": "Tipo de conteúdo não suportado", "success": False}, 400)
                    
                    # Handle JavaScript undefined represented as string 'undefined'
                    if conteudo is None or conteudo == 'undefined' or conteudo == '':
                        return json_response({"error": "Conteúdo é obrigatório", "success": False}, 400)
                    
                    conteudo = conteudo.strip() if isinstance(conteudo, str) else ''
                    
                    if not conteudo:
                        return json_response({"error": "Conteúdo é obrigatório", "success": False}, 400)
                    
                    # Ensure user_id is a proper Python int before passing to D1
                    # (dict access might still return JsProxy in Pyodide environment)
                    if hasattr(user_id, 'to_py'):
                        user_id = user_id.to_py()
                    user_id = int(user_id) if user_id is not None else None
                    
                    if user_id is None:
                        return json_response({"error": "Usuárie inválide", "success": False}, 400)
                    
                    # For now, we don't handle image uploads in Cloudflare Workers
                    # (would need R2 storage integration)
                    # Just create the post with text content
                    post_id = await create_post(db, user_id, conteudo, None)
                    
                    if not post_id:
                        return json_response({"error": "Erro ao criar post", "success": False}, 500)
                    
                    # Process mentions (@username)
                    await process_mentions(db, conteudo, user_id, 'post', post_id)
                    
                    # Process hashtags (#tag)
                    await process_hashtags(db, conteudo, 'post', post_id)
                    
                    return json_response({"success": True, "id": post_id, "imagens": []}, 201)
                    
                except Exception as e:
                    console.error(f"[posts_multi Error] {type(e).__name__}: {e}")
                    console.error(f"[posts_multi Traceback] {traceback.format_exc()}")
                    return json_response({"error": str(e), "success": False}, 500)
            
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
                    
                    # Processar menções (@username) no comentário
                    await process_mentions(db, conteudo, current_user['id'], 'comentario', comment_id)
                    
                    # Processar hashtags (#tag) no comentário
                    await process_hashtags(db, conteudo, 'comentario', comment_id)
                    
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
            # MENÇÕES (@) E HASHTAGS (#)
            # ================================================================
            
            # Hashtags em tendência
            if path == '/api/hashtags/trending':
                limit = int(params.get('limit', ['10'])[0])
                tags = await get_trending_hashtags(db, limit)
                return json_response({"hashtags": tags})
            
            # Buscar por hashtag
            if path.startswith('/api/hashtags/') and '/search' not in path:
                tag = path.split('/')[3]
                page = int(params.get('page', ['1'])[0])
                limit = 20
                offset = (page - 1) * limit
                posts = await search_by_hashtag(db, tag, 'post', limit, offset)
                return json_response({"posts": posts, "tag": tag})
            
            # Menções do usuárie
            if path == '/api/mencoes':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                page = int(params.get('page', ['1'])[0])
                limit = 20
                offset = (page - 1) * limit
                mencoes = await get_user_mentions(db, current_user['id'], limit, offset)
                return json_response({"mencoes": mencoes})
            
            # ================================================================
            # EMOJIS PERSONALIZADOS NÃO-BINÁRIOS
            # ================================================================
            
            # Listar emojis
            if path == '/api/emojis' and method == 'GET':
                categoria = params.get('categoria', [None])[0]
                emojis = await get_emojis_custom(db, categoria)
                return json_response({"emojis": emojis})
            
            # Categorias de emojis
            if path == '/api/emojis/categorias':
                categorias = await get_emoji_categories(db)
                return json_response({"categorias": categorias})
            
            # Admin: criar emoji
            if path == '/api/admin/emojis' and method == 'POST':
                if not current_user or not current_user.get('is_admin'):
                    return json_response({"error": "Admin apenas"}, 403)
                
                body = await request.json()
                emoji_id = await create_emoji_custom(
                    db, body.get('codigo'),
                    body.get('nome'),
                    body.get('imagem_url'),
                    body.get('descricao'),
                    body.get('categoria', 'geral'),
                    current_user['id']
                )
                if emoji_id:
                    return json_response({"id": emoji_id}, 201)
                return json_response({"error": "Código já existe"}, 400)
            
            # Admin: atualizar emoji
            if path.startswith('/api/admin/emojis/') and method in ['PUT', 'PATCH']:
                if not current_user or not current_user.get('is_admin'):
                    return json_response({"error": "Admin apenas"}, 403)
                
                emoji_id = path.split('/')[4]
                try:
                    emoji_id = int(emoji_id)
                except ValueError:
                    return json_response({"error": "ID inválido"}, 400)
                
                body = await request.json()
                await update_emoji_custom(db, emoji_id, **body)
                return json_response({"success": True})
            
            # Admin: deletar emoji
            if path.startswith('/api/admin/emojis/') and method == 'DELETE':
                if not current_user or not current_user.get('is_admin'):
                    return json_response({"error": "Admin apenas"}, 403)
                
                emoji_id = path.split('/')[4]
                try:
                    emoji_id = int(emoji_id)
                except ValueError:
                    return json_response({"error": "ID inválido"}, 400)
                
                await delete_emoji_custom(db, emoji_id)
                return json_response({"success": True})
            
            # ================================================================
            # FEATURE FLAGS (Admin)
            # ================================================================
            
            if path == '/api/admin/features':
                if not current_user or not current_user.get('is_admin'):
                    return json_response({"error": "Admin apenas"}, 403)
                
                if method == 'GET':
                    flags = await get_all_feature_flags(db)
                    return json_response({"features": flags})
                
                if method == 'PUT':
                    body = await request.json()
                    await update_feature_flag(
                        db, body.get('nome'),
                        body.get('ativo'),
                        current_user['id']
                    )
                    return json_response({"success": True})
            
            # ================================================================
            # MENSAGENS DIRETAS (desativado por padrão - verificar feature flag)
            # ================================================================
            
            if path == '/api/mensagens':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                # Verificar se funcionalidade está ativa
                is_active = await get_feature_flag(db, 'mensagens_diretas')
                if not is_active:
                    return json_response({
                        "error": "Esta funcionalidade será lançada em breve!",
                        "disabled": True
                    }, 503)
                
                conversations = await get_conversations(db, current_user['id'])
                return json_response({"conversations": conversations})
            
            if path.startswith('/api/mensagens/') and method == 'GET':
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                # Verificar se funcionalidade está ativa
                is_active = await get_feature_flag(db, 'mensagens_diretas')
                if not is_active:
                    return json_response({
                        "error": "Esta funcionalidade será lançada em breve!",
                        "disabled": True
                    }, 503)
                
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
                
                # Verificar se funcionalidade está ativa
                is_active = await get_feature_flag(db, 'mensagens_diretas')
                if not is_active:
                    return json_response({
                        "error": "Esta funcionalidade será lançada em breve!",
                        "disabled": True
                    }, 503)
                
                body = await request.json()
                msg_id = await send_direct_message(
                    db, current_user['id'],
                    body.get('destinatarie_id'),
                    body.get('conteudo')
                )
                return json_response({"id": msg_id}, 201)
            
            # ================================================================
            # GRUPOS DE ESTUDO (desativado por padrão - verificar feature flag)
            # ================================================================
            
            if path == '/api/grupos':
                # Verificar se funcionalidade está ativa
                is_active = await get_feature_flag(db, 'grupos_estudo')
                if not is_active:
                    return json_response({
                        "error": "Esta funcionalidade será lançada em breve!",
                        "disabled": True
                    }, 503)
                
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
                        body.get('max_membres', 50)
                    )
                    return json_response({"id": grupo_id}, 201)
            
            if path.startswith('/api/grupos/') and '/entrar' in path:
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                # Verificar se funcionalidade está ativa
                is_active = await get_feature_flag(db, 'grupos_estudo')
                if not is_active:
                    return json_response({
                        "error": "Esta funcionalidade será lançada em breve!",
                        "disabled": True
                    }, 503)
                
                grupo_id = path.split('/')[3]
                success, error = await join_study_group(db, grupo_id, current_user['id'])
                if error:
                    return json_response({"error": error}, 400)
                return json_response({"success": True})
            
            if path.startswith('/api/grupos/') and '/sair' in path:
                if not current_user:
                    return json_response({"error": "Autenticação necessária"}, 401)
                
                # Verificar se funcionalidade está ativa
                is_active = await get_feature_flag(db, 'grupos_estudo')
                if not is_active:
                    return json_response({
                        "error": "Esta funcionalidade será lançada em breve!",
                        "disabled": True
                    }, 503)
                
                grupo_id = path.split('/')[3]
                await leave_study_group(db, grupo_id, current_user['id'])
                return json_response({"success": True})
            
            if path.startswith('/api/grupos/') and '/mensagens' in path:
                # Verificar se funcionalidade está ativa
                is_active = await get_feature_flag(db, 'grupos_estudo')
                if not is_active:
                    return json_response({
                        "error": "Esta funcionalidade será lançada em breve!",
                        "disabled": True
                    }, 503)
                
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
        """Página inicial - Feed/Rede Social - usando template externo."""
        # Se usuário não está autenticado, mostra a landing page usando template externo
        if current_user is None or not current_user:
            return render_template('landing.html')

        # Usuário está autenticado - mostra o feed com posts
        posts = []
        divulgacoes = []
        if db and DB_AVAILABLE:
            try:
                posts = await get_posts(db, page=1, per_page=20)
                divulgacoes = await get_divulgacoes(db, area='edu')
            except Exception as e:
                console.warn(f"[Index] Error loading posts: {e}")
        
        # Renderizar posts
        posts_html = ""
        if posts:
            for p in posts:
                # Buscar dados do autor - escaped para segurança
                autor_username = escape_html(p.get('usuario', 'Usuárie'))
                autor_foto = normalize_image_url(p.get('foto_perfil'))
                
                data_str = ""
                if p.get('data'):
                    try:
                        data_str = escape_html(str(p.get('data'))[:16])  # Simplificar formato
                    except:
                        pass
                
                # Verificar se o usuário atual curtiu
                liked_class = "liked" if p.get('liked') else ""
                liked_icon = "❤️" if p.get('liked') else "🤍"
                
                # Imagem do post
                img_html = ""
                if p.get('imagem'):
                    img_src = normalize_image_url(p.get('imagem'))
                    img_html = f'<img src="{escape_html(img_src)}" alt="Imagem do post" style="width:100%;border-radius:16px;margin:0.8rem 0;max-height:400px;object-fit:cover;">'
                
                # Escapar conteúdo do post
                post_conteudo = escape_html(p.get('conteudo', ''))
                post_id = int(p.get('id', 0))
                
                posts_html += f"""
                <div class="feed-item" data-post-id="{post_id}">
                    <div style="display:flex;align-items:center;gap:0.7rem;margin-bottom:0.8rem;">
                        <img src="{autor_foto}" alt="@{autor_username}" style="width:42px;height:42px;border-radius:50%;object-fit:cover;border:2px solid #eee;">
                        <div>
                            <strong style="color:var(--primary);font-size:0.9rem;">@{autor_username}</strong>
                            <span style="color:var(--text-dim);font-size:0.7rem;margin-left:0.5rem;">{data_str}</span>
                        </div>
                    </div>
                    <p style="font-size:0.95rem;line-height:1.5;white-space:pre-wrap;">{post_conteudo}</p>
                    {img_html}
                    <div style="display:flex;gap:1rem;margin-top:0.8rem;font-size:0.8rem;">
                        <button onclick="likePost({post_id})" class="like-btn {liked_class}" style="background:#f1edff;border:1px solid #d3c5ff;padding:0.4rem 0.8rem;border-radius:20px;cursor:pointer;font-weight:600;color:var(--primary);">
                            {liked_icon} {p.get('like_count', 0)}
                        </button>
                        <button onclick="toggleComments({post_id})" style="background:#f1edff;border:1px solid #d3c5ff;padding:0.4rem 0.8rem;border-radius:20px;cursor:pointer;font-weight:600;color:var(--primary);">
                            💬 {p.get('comment_count', 0)}
                        </button>
                    </div>
                    <div id="comments-{post_id}" style="display:none;margin-top:0.8rem;"></div>
                </div>"""
        else:
            posts_html = '<div class="empty">Nenhum post ainda. Seja ê primeire a postar!</div>'
        
        # Divulgações para sidebar
        divulgacoes_html = ""
        if divulgacoes:
            for d in divulgacoes[:3]:
                div_titulo = escape_html(d.get('titulo', ''))
                div_texto = escape_html((d.get('texto') or '')[:80])
                divulgacoes_html += f"""
                <div style="padding:0.5rem 0;border-bottom:1px solid var(--border);">
                    <strong style="font-size:0.75rem;color:var(--primary);">{div_titulo}</strong>
                    <p style="font-size:0.65rem;color:var(--text-dim);margin:0.2rem 0 0;">{div_texto}...</p>
                </div>"""
        else:
            divulgacoes_html = '<div class="placeholder">Nenhuma divulgação.</div>'
        
        # Info do usuário para JS - escaped para segurança
        user_username_js = escape_js_string(current_user.get('username', ''))
        user_id = int(current_user.get('id', 0))
        user_foto = normalize_image_url(current_user.get('foto_perfil'))
        
        # Admin button (only for admin/superadmin)
        is_admin = current_user.get('is_admin', False) or current_user.get('is_superadmin', False)
        admin_btn_html = ''
        if is_admin:
            admin_btn_html = '''<button onclick="location.href='/admin'" class="action-btn" title="Painel de Controle" aria-label="Painel de Controle">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="3" y="3" width="7" height="7"></rect>
                                <rect x="14" y="3" width="7" height="7"></rect>
                                <rect x="14" y="14" width="7" height="7"></rect>
                                <rect x="3" y="14" width="7" height="7"></rect>
                            </svg>
                        </button>'''
        
        # Auth profile link for header (authenticated user)
        user_initial = escape_html((current_user.get('username', '?')[:1]).upper())
        auth_profile_link_html = f'''<a href="/perfil" class="profile-avatar-link" aria-label="Meu Perfil" data-tooltip="Meu Perfil">
    <img src="{user_foto}" alt="Avatar" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';">
    <span class="initial" style="display:none;">{user_initial}</span>
</a>'''
        
        # Mobile nav auth section (profile link for authenticated users)
        mobile_nav_auth_html = f'''<a href="/perfil" aria-label="Perfil" title="Perfil">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
      <circle cx="12" cy="7" r="4"></circle>
    </svg>
    <span>Perfil</span>
</a>'''
        
        # Usar template externo com placeholders
        return render_template('feed.html',
            feed_html=posts_html,
            divulgacoes_html=divulgacoes_html,
            user_foto=user_foto,
            user_username_js=user_username_js,
            user_id=user_id,
            admin_btn_html=admin_btn_html,
            auth_profile_link_html=auth_profile_link_html,
            mobile_nav_auth_html=mobile_nav_auth_html,
            footer_html=page_footer(True))

    async def _educacao_page(self, db, current_user):
        """Página Educação - Hub educacional - usando template externo."""
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
                    <div class="fi-meta">{escape_html(c.get('tipo', 'artigo')).upper()}</div>
                    <h3 class="fi-title">{escape_html(c.get('titulo', ''))}</h3>
                    <p class="fi-body">{escape_html((c.get('resumo') or '')[:200])}...</p>
                </div>"""
        else:
            contents_html = '<div class="empty">Nenhum conteúdo encontrado.</div>'
        
        return render_template('gramatike_edu.html', content_html=contents_html)

    async def _login_page(self, db, current_user, request, method):
        """Página de Login - usando template externo."""
        # Se já logado, redireciona
        if current_user:
            return redirect('/')
        
        error_msg = ""
        
        # Processar form de login
        if method == 'POST':
            if not db or not DB_AVAILABLE:
                error_msg = "Banco de dados não disponível. Verifique a configuração do Cloudflare D1."
            else:
                try:
                    # Ler form data
                    body_text = await request.text()
                    form_data = parse_qs(body_text)
                    
                    email = form_data.get('email', [''])[0].strip()
                    password = form_data.get('password', [''])[0]
                    
                    # Log login attempt (without sensitive password info) - use console.log for info
                    console.log(f"[Login] Tentativa: {email}")
                    
                    if email and password:
                        token, err = await login(db, request, email, password)
                        if token:
                            console.log(f"[Login] Login bem-sucedido: {email}")
                            return redirect('/', headers={"Set-Cookie": set_session_cookie(token)})
                        else:
                            # Failed auth is a warning, use console.warn
                            console.warn(f"[Login] Falha na autenticação: {email} - {err}")
                            error_msg = err or "Credenciais inválidas"
                    else:
                        # Warning: incomplete fields
                        console.warn(f"[Login] Campos incompletos")
                        error_msg = "Preencha todos os campos"
                except Exception as e:
                    # Log error details for debugging (without sensitive info) - use console.error
                    console.error(f"[Login Error] {type(e).__name__}: {e}")
                    console.error(f"[Login Traceback] {traceback.format_exc()}")
                    # Show more specific error message to user
                    error_str = str(e).lower()
                    if 'no such table' in error_str or 'database' in error_str:
                        error_msg = "Erro de banco de dados. Contate o suporte."
                    elif 'timeout' in error_str or 'connection' in error_str:
                        error_msg = "Erro de conexão. Tente novamente em instantes."
                    else:
                        error_msg = "Erro ao processar login. Tente novamente."
        
        # Usar template externo
        flash_html = create_error_html(error_msg) if error_msg else ""
        return render_template('login.html', flash_html=flash_html)

    async def _cadastro_page(self, db, current_user, request, method):
        """Página de Cadastro - usando template externo."""
        # Se já logado, redireciona
        if current_user:
            return redirect('/')
        
        error_msg = ""
        success_msg = ""
        
        # Processar form de cadastro
        if method == 'POST':
            if not db or not DB_AVAILABLE:
                error_msg = "Banco de dados não disponível. Verifique a configuração do Cloudflare D1."
            else:
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
                    # Log error details for debugging - use console.error
                    console.error(f"[Registration Error] {type(e).__name__}: {e}")
                    console.error(f"[Registration Traceback] {traceback.format_exc()}")
                    # Show more specific error message to user
                    error_str = str(e).lower()
                    if 'unique' in error_str or 'duplicate' in error_str:
                        error_msg = "Estu usuárie ou email já está cadastrade."
                    elif 'no such table' in error_str or 'database' in error_str:
                        error_msg = "Erro de banco de dados. Contate o suporte."
                    elif 'timeout' in error_str or 'connection' in error_str:
                        error_msg = "Erro de conexão. Tente novamente em instantes."
                    else:
                        error_msg = "Erro ao processar cadastro. Tente novamente."
        
        # Usar template externo
        flash_html = ""
        if error_msg:
            flash_html = create_error_html(error_msg)
        elif success_msg:
            flash_html = create_success_html(success_msg)
        return render_template('cadastro.html', flash_html=flash_html)

    async def _dinamicas_page(self, db, current_user):
        """Página de Dinâmicas - usando template externo."""
        dynamics_html = ""
        
        if db and DB_AVAILABLE:
            try:
                dynamics = await get_dynamics(db)
                if dynamics:
                    for d in dynamics:
                        tipo_emoji = {"poll": "📊", "form": "📝", "oneword": "💬"}.get(d.get('tipo'), '🎮')
                        dynamics_html += f"""
                        <div class="feed-item">
                            <div class="fi-meta">{tipo_emoji} {escape_html(d.get('tipo', 'dinâmica')).upper()}</div>
                            <h3 class="fi-title">{escape_html(d.get('titulo', ''))}</h3>
                            <p class="fi-body">{escape_html(d.get('descricao') or 'Participe desta dinâmica!')}</p>
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
        
        return render_template('dinamicas.html', content_html=dynamics_html)

    async def _exercicios_page(self, db, current_user):
        """Página de Exercícios - usando template externo."""
        topics_html = ""
        
        if db and DB_AVAILABLE:
            try:
                topics = await get_exercise_topics(db)
                if topics:
                    for t in topics:
                        topics_html += f"""
                        <div class="feed-item">
                            <h3 class="fi-title">{escape_html(t.get('nome', ''))}</h3>
                            <p class="fi-body">{escape_html(t.get('descricao') or 'Tópico de exercícios')}</p>
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
        
        return render_template('exercicios.html', content_html=topics_html)

    async def _artigos_page(self, db, current_user):
        """Página de Artigos - usando template externo."""
        artigos_html = ""
        
        if db and DB_AVAILABLE:
            try:
                artigos = await get_edu_contents(db, tipo='artigo', page=1, per_page=20)
                if artigos:
                    for a in artigos:
                        artigos_html += f"""
                        <div class="feed-item">
                            <div class="fi-meta">ARTIGO</div>
                            <h3 class="fi-title">{escape_html(a.get('titulo', ''))}</h3>
                            <p class="fi-body">{escape_html((a.get('resumo') or '')[:200])}...</p>
                        </div>"""
            except:
                pass
        
        if not artigos_html:
            artigos_html = '<div class="empty">Nenhum artigo disponível.</div>'
        
        return render_template('artigos.html', content_html=artigos_html)

    async def _apostilas_page(self, db, current_user):
        """Página de Apostilas - usando template externo."""
        apostilas_html = ""
        
        if db and DB_AVAILABLE:
            try:
                apostilas = await get_edu_contents(db, tipo='apostila', page=1, per_page=20)
                if apostilas:
                    for a in apostilas:
                        url = escape_html(a.get("url", ""))
                        apostilas_html += f"""
                        <div class="feed-item">
                            <div class="fi-meta">📖 APOSTILA</div>
                            <h3 class="fi-title">{escape_html(a.get('titulo', ''))}</h3>
                            <p class="fi-body">{escape_html((a.get('resumo') or '')[:200])}...</p>
                            {'<a href="' + url + '" class="btn btn-primary" style="margin-top: 0.8rem; font-size: 0.75rem;">Baixar PDF</a>' if url else ''}
                        </div>"""
            except:
                pass
        
        if not apostilas_html:
            apostilas_html = '<div class="empty">Nenhuma apostila disponível.</div>'
        
        return render_template('apostilas.html', content_html=apostilas_html)

    async def _podcasts_page(self, db, current_user):
        """Página de Podcasts - usando template externo."""
        podcasts_html = ""
        
        if db and DB_AVAILABLE:
            try:
                podcasts = await get_edu_contents(db, tipo='podcast', page=1, per_page=20)
                if podcasts:
                    for p in podcasts:
                        url = escape_html(p.get("url", ""))
                        podcasts_html += f"""
                        <div class="feed-item">
                            <div class="fi-meta">🎧 PODCAST</div>
                            <h3 class="fi-title">{escape_html(p.get('titulo', ''))}</h3>
                            <p class="fi-body">{escape_html((p.get('resumo') or '')[:200])}...</p>
                            {'<a href="' + url + '" class="btn btn-primary" style="margin-top: 0.8rem; font-size: 0.75rem;" target="_blank">Ouvir</a>' if url else ''}
                        </div>"""
            except:
                pass
        
        if not podcasts_html:
            podcasts_html = '<div class="empty">Nenhum podcast disponível.</div>'
        
        return render_template('podcasts.html', content_html=podcasts_html)

    async def _suporte_page(self, db, current_user):
        """Página de Suporte - usando template externo."""
        return render_template('suporte.html')

    async def _videos_page(self, db, current_user):
        """Página de Vídeos - usando template externo."""
        return render_template('videos.html')

    async def _redacao_page(self, db, current_user):
        """Página de Redação - usando template externo."""
        return render_template('redacao.html')

    async def _post_detail_page(self, db, current_user, post_id):
        """Página de detalhes do post - usando template externo."""
        if not db or not DB_AVAILABLE:
            return self._not_found_page(f'/post/{post_id}')
        
        try:
            post_id_int = int(post_id)
            post = await get_post_by_id(db, post_id_int)
            if not post:
                return self._not_found_page(f'/post/{post_id}')
            
            # Gerar HTML do post
            post_html = f"""
            <div class="feed-item">
                <div style="display:flex;align-items:center;gap:0.7rem;margin-bottom:0.8rem;">
                    <img src="{normalize_image_url(post.get('foto_perfil'))}" alt="@{escape_html(post.get('usuario', ''))}" style="width:42px;height:42px;border-radius:50%;object-fit:cover;">
                    <strong style="color:var(--primary);">@{escape_html(post.get('usuario', ''))}</strong>
                </div>
                <p class="fi-body">{escape_html(post.get('conteudo', ''))}</p>
                <div style="margin-top: 0.8rem; font-size: 0.7rem; color: var(--text-dim);">
                    ❤️ {post.get('like_count', 0)} • 💬 {post.get('comment_count', 0)}
                </div>
            </div>"""
            
            return render_template('post_detail.html', content_html=post_html)
        except (ValueError, Exception) as e:
            return self._not_found_page(f'/post/{post_id}')

    async def _novidade_detail_page(self, db, current_user, novidade_id):
        """Novidade detail page - using external template."""
        # TODO: Implement get_novidade_by_id in _database.py to enable dynamic content
        return render_template('novidade_detail.html', content_html='<div class="empty">Novidade não encontrada.</div>')

    async def _dinamica_admin_page(self, db, current_user):
        """Página de administração de dinâmicas - usando template externo."""
        if not current_user:
            return redirect('/login')
        
        is_admin = current_user.get('is_admin', False) or current_user.get('is_superadmin', False)
        if not is_admin:
            return render_template('acesso_restrito.html',
                message='Você não tem permissão para acessar esta página.',
                button_url='/dinamicas',
                button_text='Voltar para Dinâmicas')
        
        return render_template('dinamica_admin.html')

    async def _dinamica_view_page(self, db, current_user, dinamica_id):
        """Página de visualização de dinâmica - usando template externo."""
        if not db or not DB_AVAILABLE:
            return self._not_found_page(f'/dinamica/{dinamica_id}')
        
        try:
            dinamica_id_int = int(dinamica_id)
            dinamica = await get_dynamic_by_id(db, dinamica_id_int)
            if not dinamica:
                return self._not_found_page(f'/dinamica/{dinamica_id}')
            
            return render_template('dinamica_view.html', dinamica=dinamica)
        except (ValueError, Exception) as e:
            return self._not_found_page(f'/dinamica/{dinamica_id}')

    async def _dinamica_edit_page(self, db, current_user, dinamica_id):
        """Página de edição de dinâmica - usando template externo."""
        if not current_user:
            return redirect('/login')
        
        is_admin = current_user.get('is_admin', False) or current_user.get('is_superadmin', False)
        if not is_admin:
            return render_template('acesso_restrito.html',
                message='Você não tem permissão para editar dinâmicas.',
                button_url='/dinamicas',
                button_text='Voltar para Dinâmicas')
        
        return render_template('dinamica_edit.html')

    async def _gerenciar_usuarios_page(self, db, current_user):
        """Página de gerenciamento de usuários - usando template externo."""
        if not current_user:
            return redirect('/login')
        
        is_admin = current_user.get('is_admin', False) or current_user.get('is_superadmin', False)
        if not is_admin:
            return render_template('acesso_restrito.html',
                message='Você não tem permissão para gerenciar usuários.',
                button_url='/',
                button_text='Voltar ao início')
        
        return render_template('gerenciar_usuarios.html')

    async def _manutencao_page(self):
        """Maintenance page - using external template."""
        return render_template('maintenance.html')

    async def _profile_page(self, db, current_user, username):
        """Página de perfil de usuárie - usando template externo."""
        if not db or not DB_AVAILABLE:
            return self._not_found_page(f'/u/{username}')
        
        try:
            user = await get_user_by_username(db, username)
            if not user:
                return self._not_found_page(f'/u/{username}')
            
            # Buscar posts de usuárie
            posts = await get_posts(db, user_id=user['id'], per_page=20)
            
            # Gerar HTML dos posts
            posts_html = ""
            if posts:
                for p in posts:
                    posts_html += f"""
                    <div class="feed-item">
                        <p class="fi-body">{escape_html(p.get('conteudo', ''))}</p>
                        <div style="margin-top: 0.8rem; font-size: 0.7rem; color: var(--text-dim);">
                            ❤️ {p.get('like_count', 0)} • 💬 {p.get('comment_count', 0)}
                        </div>
                    </div>"""
            else:
                posts_html = '<div class="empty">Nenhum post ainda.</div>'
            
            return render_template('perfil.html', content_html=posts_html, user=user)
        except Exception as e:
            return self._not_found_page(f'/u/{username}')

    async def _novo_post_page(self, db, current_user, request, method):
        """Página para criar novo post - usando template externo."""
        if not current_user:
            return redirect('/login')
        
        # Validate current_user has required 'id' field
        user_id = current_user.get('id') if isinstance(current_user, dict) else None
        if user_id is None:
            console.error("[NovoPost] current_user.id is None")
            return redirect('/login')
        
        error_msg = ""
        
        if method == 'POST':
            if not db or not DB_AVAILABLE:
                error_msg = "Banco de dados não disponível."
            else:
                try:
                    body_text = await request.text()
                    form_data = parse_qs(body_text)
                    
                    conteudo = form_data.get('conteudo', [''])[0].strip()
                    
                    if conteudo:
                        # Pass user_id (already validated) instead of accessing dict again
                        post_id = await create_post(db, user_id, conteudo, None)
                        if post_id:
                            return redirect('/')
                        else:
                            error_msg = "Erro ao criar post"
                    else:
                        error_msg = "O conteúdo não pode estar vazio"
                except Exception as e:
                    console.error(f"[NovoPost Error] {e}")
                    error_msg = "Erro ao processar post"
        
        flash_html = create_error_html(error_msg) if error_msg else ""
        return render_template('criar_post.html', flash_html=flash_html)

    async def _meu_perfil_page(self, db, current_user):
        """Página do perfil do usuário logado - usando template externo."""
        if not current_user:
            return redirect('/login')
        
        user = current_user
        
        posts = []
        if db and DB_AVAILABLE:
            try:
                posts = await get_posts(db, user_id=user['id'], per_page=20)
            except:
                pass
        
        # Gerar HTML dos posts com escape
        posts_html = ""
        if posts:
            for p in posts:
                post_conteudo = escape_html(p.get('conteudo', ''))
                posts_html += f"""
                <div class="feed-item">
                    <p class="fi-body">{post_conteudo}</p>
                    <div style="margin-top: 0.8rem; font-size: 0.7rem; color: var(--text-dim);">
                        ❤️ {p.get('like_count', 0)} • 💬 {p.get('comment_count', 0)}
                    </div>
                </div>"""
        else:
            posts_html = '<div class="empty">Você ainda não fez nenhum post.</div>'
        
        return render_template('meu_perfil.html', content_html=posts_html, current_user=current_user)

    async def _configuracoes_page(self, db, current_user):
        """Página de configurações do usuário - usando template externo."""
        if not current_user:
            return redirect('/login')
        
        # Generate email status HTML based on email_confirmed flag
        email_confirmed = current_user.get('email_confirmed', False)
        if email_confirmed:
            email_status_html = '<div class="muted" style="margin-top:6px;">E-mail confirmado ✅</div>'
        else:
            email_status_html = '''<div class="muted" style="margin-top:6px; display:flex; align-items:center; gap:8px;">
                            <span style="color:#b45309; background:#fef3c7; border:1px solid #fde68a; padding:4px 8px; border-radius:999px; font-weight:600;">E-mail não confirmado</span>
                            <button type="button" id="btn-resend-verify" class="btn" style="background:#9B5DE5;">Reenviar verificação</button>
                        </div>'''
        
        # Passar dados do usuário para o template
        return render_template('configuracoes.html', current_user=current_user, email_status_html=email_status_html)

    def _not_found_page(self, path):
        """Página 404 - usando template externo."""
        return render_template('404.html', path=escape_html(path))

    async def _admin_page(self, db, current_user):
        """Admin Dashboard page - usando template externo."""
        # Check if user is admin
        if not current_user:
            return render_template('acesso_restrito.html', 
                message='Você precisa estar logado para acessar esta página.',
                button_url='/login',
                button_text='Fazer Login')
        
        is_admin = current_user.get('is_admin', False) or current_user.get('is_superadmin', False)
        if not is_admin:
            return render_template('acesso_restrito.html',
                message='Você não tem permissão para acessar o painel de administração.',
                button_url='/',
                button_text='Voltar ao início')
        
        # Get admin stats
        stats = await get_admin_stats(db) if db else {}
        total_users = stats.get('total_users', 0)
        total_posts = stats.get('total_posts', 0)
        total_comments = stats.get('total_comments', 0)
        
        # Get all users for admin panel
        all_users = await get_all_usuaries(db) if db else []
        
        # Build users table
        users_html = ""
        for user in (all_users[:10] if len(all_users) > 10 else all_users):
            username = escape_html(user.get('username', ''))
            email = escape_html(user.get('email', ''))
            is_user_admin = user.get('is_admin', False)
            is_superadmin = user.get('is_superadmin', False)
            
            badge = ""
            if is_superadmin:
                badge = '<span class="badge badge-superadmin">SUPERADMIN</span>'
            elif is_user_admin:
                badge = '<span class="badge badge-admin">ADMIN</span>'
                
            users_html += f'''
            <tr>
                <td>{username}</td>
                <td>{email}</td>
                <td>{badge}</td>
                <td>
                    <button class="action-btn">Ver Perfil</button>
                    <button class="action-btn danger">Banir</button>
                </td>
            </tr>'''
        
        # Usar template externo com placeholders
        return render_template('admin_panel.html',
            total_users=total_users,
            total_posts=total_posts,
            total_comments=total_comments,
            users_table_html=users_html,
            footer_html=page_footer(False))

    async def _esqueci_senha_page(self, db, current_user, request, method):
        """Página Esqueci Minha Senha - usando template externo."""
        # Se já logado, redireciona para a página inicial
        if current_user:
            return redirect('/')
        
        message = ""
        message_type = ""
        
        if method == 'POST':
            try:
                body_text = await request.text()
                form_data = parse_qs(body_text)
                email = form_data.get('email', [''])[0].strip()
                
                if email:
                    # Check if user exists
                    if db and DB_AVAILABLE:
                        from gramatike_d1.db import get_user_by_email
                        user = await get_user_by_email(db, email)
                        
                        if user:
                            # Create reset token
                            user_id = user.get('id')
                            token = await create_email_token(db, user_id, 'reset', expires_hours=1)
                            if token:
                                # Token created successfully
                                # Note: In Cloudflare Workers, email sending requires an external service
                                # The token is stored in the database for verification
                                message = "Se o e-mail estiver cadastrado, você receberá um link de recuperação."
                                message_type = "success"
                            else:
                                message = "Se o e-mail estiver cadastrado, você receberá um link de recuperação."
                                message_type = "success"
                        else:
                            # Don't reveal if email exists
                            message = "Se o e-mail estiver cadastrado, você receberá um link de recuperação."
                            message_type = "success"
                    else:
                        message = "Serviço temporariamente indisponível."
                        message_type = "error"
                else:
                    message = "Por favor, informe seu e-mail."
                    message_type = "error"
            except Exception as e:
                console.error(f"[Esqueci Senha Error] {type(e).__name__}: {e}")
                message = "Erro ao processar solicitação. Tente novamente."
                message_type = "error"
        
        # Usar template externo
        flash_html = ""
        if message:
            if message_type == "success":
                flash_html = create_success_html(message)
            else:
                flash_html = create_error_html(message)
        return render_template('esqueci_senha.html', flash_html=flash_html)

    async def _reset_senha_page(self, db, current_user, request, method):
        """Página Redefinir Senha - usando template externo."""
        # Se já logado, redireciona para a página inicial
        if current_user:
            return redirect('/')
        
        # Get token from URL using proper URL parsing
        parsed_url = urlparse(str(request.url))
        query_params = parse_qs(parsed_url.query)
        url_token = query_params.get('token', [''])[0]
        
        # Initialize token from URL
        token = url_token
        password = ""
        password2 = ""
        
        if method == 'POST':
            try:
                body_text = await request.text()
                form_data = parse_qs(body_text)
                # Prefer token from form, fallback to URL token
                form_token = form_data.get('token', [''])[0]
                token = form_token if form_token else url_token
                password = form_data.get('password', [''])[0]
                password2 = form_data.get('password2', [''])[0]
            except Exception as e:
                console.error(f"[Reset Senha Error] Error parsing form: {e}")
        
        message = ""
        message_type = ""
        token_data = None
        
        if not token:
            message = "Token inválido ou expirado."
            message_type = "error"
        elif db and DB_AVAILABLE:
            # Verify token
            token_data = await verify_email_token(db, token, 'reset')
            if not token_data:
                message = "Token inválido ou expirado."
                message_type = "error"
            elif method == 'POST':
                if not password:
                    message = "Por favor, informe a nova senha."
                    message_type = "error"
                elif password != password2:
                    message = "As senhas não coincidem."
                    message_type = "error"
                else:
                    # Validate password strength
                    is_valid, password_error = validate_password_strength(password)
                    if not is_valid:
                        message = password_error
                        message_type = "error"
                    else:
                        # Update password
                        try:
                            user_id = token_data.get('usuario_id')
                            await update_user_password(db, user_id, password)
                            await use_email_token(db, token)
                            # Redirect to login with success message
                            return redirect('/login')
                        except Exception as e:
                            console.error(f"[Reset Senha Error] {type(e).__name__}: {e}")
                            message = "Erro ao atualizar a senha. Tente novamente."
                            message_type = "error"
        else:
            message = "Serviço temporariamente indisponível."
            message_type = "error"
        
        # Usar template externo
        flash_html = ""
        if message:
            if message_type == "success":
                flash_html = create_success_html(message)
            else:
                flash_html = create_error_html(message)
        return render_template('reset_senha.html', flash_html=flash_html)
