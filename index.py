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
from urllib.parse import urlparse, parse_qs

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
SCRIPT_VERSION = "v2025.12.01.a"

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
                "/novo-post": lambda: self._novo_post_page(db, current_user, request, method),
                "/perfil": lambda: self._meu_perfil_page(db, current_user),
                "/configuracoes": lambda: self._configuracoes_page(db, current_user),
                "/admin": lambda: self._admin_page(db, current_user),
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
                    conteudo = body.get('conteudo', '').strip()
                    imagem = body.get('imagem')
                    
                    if not conteudo:
                        return json_response({"error": "Conteúdo é obrigatório"}, 400)
                    
                    post_id = await create_post(db, current_user['id'], conteudo, imagem)
                    
                    # Processar menções (@username)
                    await process_mentions(db, conteudo, current_user['id'], 'post', post_id)
                    
                    # Processar hashtags (#tag)
                    await process_hashtags(db, conteudo, 'post', post_id)
                    
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
        """Página inicial - Feed/Rede Social."""
        # Se usuário não está autenticado, mostra a landing page
        if current_user is None or not current_user:
            return f"""{page_head("Gramátike")}
    <header class="site-head">
        <h1 class="logo">Gramátike</h1>
    </header>
    <div class="content-wrapper">
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
                <p>Aprenda gramática de forma inclusiva</p>
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
            <a href="/" class="module-card">
                <div class="icon">💬</div>
                <h3>Portal Gramátike</h3>
                <p>Acesse a comunidade</p>
            </a>
        </div>
    </main>
    </div>
{page_footer(False)}"""

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
        user_username = escape_html(current_user.get('username', ''))
        user_username_js = escape_js_string(current_user.get('username', ''))
        user_id = int(current_user.get('id', 0))
        user_nome = escape_html(current_user.get('nome') or '@' + current_user.get('username', ''))
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
        
        extra_css = """
        .like-btn.liked { background: var(--primary) !important; color: #fff !important; border-color: var(--primary) !important; }
        /* Quick nav gradient buttons */
        .quick-nav-btn {{
            flex: 1;
            text-decoration: none;
            background: linear-gradient(135deg, #9B5DE5 0%, #7B4BC4 100%);
            padding: 1rem 1.1rem;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 0.7rem;
            font-size: 1rem;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: 0.4px;
            transition: all 0.25s ease;
            box-shadow: 0 6px 20px rgba(155,93,229,0.35);
            border: none;
        }}
        .quick-nav-disabled {{
            flex: 1;
            background: linear-gradient(135deg, #b8a4c9 0%, #9d8ab5 100%);
            padding: 1rem 1.1rem;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 0.7rem;
            font-size: 1rem;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: 0.4px;
            box-shadow: 0 6px 20px rgba(155,93,229,0.25);
            border: none;
            opacity: 0.85;
        }}
        /* Profile links */
        .profile-link {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            text-decoration: none;
            padding: 0.5rem 0.7rem;
            border-radius: 14px;
            background: #f8f5ff;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--primary);
            transition: 0.18s;
        }}
        .profile-link:hover {{ background: #f0ebff; }}
        """
        
        return f"""{page_head("Gramátike", extra_css)}
    <header class="site-head">
        <h1 class="logo">Gramátike</h1>
        <a href="/perfil" style="position:absolute;right:24px;top:50%;transform:translateY(-50%);width:64px;height:64px;border-radius:50%;overflow:hidden;border:3px solid rgba(255,255,255,0.35);box-shadow:0 4px 14px rgba(0,0,0,0.25);">
            <img src="{user_foto}" alt="Perfil" style="width:100%;height:100%;object-fit:cover;">
        </a>
    </header>
    <div class="content-wrapper">
    <main>
        <!-- Triângulo toggle para mostrar/esconder card de ações (mobile only) -->
        <div id="mobile-toggle-triangle" onclick="toggleMobileActionsCard()">
            <div id="triangle-icon">
                <svg id="triangle-svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </div>
        </div>
        
        <!-- Card de Ações Rápidas (mobile only) -->
        <div id="mobile-actions-card">
            <div class="mobile-actions-row">
                <button onclick="location.href='/suporte'" class="action-btn" title="Suporte">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                </button>
                <button onclick="location.href='/configuracoes'" class="action-btn" title="Configurações">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                </button>
                <button onclick="toggleMobileTicTacToe()" class="action-btn" title="Jogo da Velha">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="6" width="20" height="12" rx="2"></rect><path d="M6 12h4"></path><path d="M14 12h4"></path><path d="M8 8v8"></path><path d="M16 8v8"></path></svg>
                </button>
                <button onclick="toggleMobileNotifications()" class="action-btn" title="Notificações" style="position:relative;">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
                    <span id="mobile-notif-badge" class="action-badge" style="display:none;">0</span>
                </button>
                <button onclick="toggleMobileAmigues()" class="action-btn" title="Amigues">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                </button>
            </div>
            <!-- Amigues mobile panel -->
            <div id="mobile-amigues-panel" style="display:none;">
                <h3 style="margin:0 0 0.8rem;font-size:1rem;font-weight:800;letter-spacing:0.5px;color:var(--primary);text-align:center;">Amigues</h3>
                <div id="mobile-amigues-list" style="display:flex;flex-direction:column;gap:0.65rem;min-height:20px;"></div>
                <div id="mobile-amigues-empty" style="display:none;font-size:0.7rem;opacity:0.7;line-height:1.3;text-align:center;">Sem amigues ainda. Faça amizades para aparecerem aqui.</div>
            </div>
            <!-- Tic-Tac-Toe mobile panel -->
            <div id="mobile-ttt-panel" style="display:none;">
                <h3 style="margin:0 0 0.55rem;font-size:0.95rem;letter-spacing:0.5px;font-weight:800;color:var(--primary);text-align:center;"># Jogo da Velha</h3>
                <p style="margin:0.2rem 0 0.7rem;font-size:0.7rem;color:#555;font-weight:600;text-align:center;">Jogue contra o <strong>Robo</strong>. Você é o <strong>X</strong>.</p>
                <div id="mobile_ttt_status" style="font-size:0.72rem;font-weight:800;color:var(--primary);letter-spacing:0.4px;margin:0 0 0.6rem;text-align:center;">Sua vez: você é X</div>
                <div id="mobile_ttt_board" class="ttt-board">
                    <button type="button" data-i="0" class="ttt-cell"></button>
                    <button type="button" data-i="1" class="ttt-cell"></button>
                    <button type="button" data-i="2" class="ttt-cell"></button>
                    <button type="button" data-i="3" class="ttt-cell"></button>
                    <button type="button" data-i="4" class="ttt-cell"></button>
                    <button type="button" data-i="5" class="ttt-cell"></button>
                    <button type="button" data-i="6" class="ttt-cell"></button>
                    <button type="button" data-i="7" class="ttt-cell"></button>
                    <button type="button" data-i="8" class="ttt-cell"></button>
                </div>
                <button id="mobile_ttt_reset" type="button" style="margin-top:0.8rem;background:var(--primary);color:#fff;border:none;border-radius:14px;padding:0.5rem 0.9rem;font-size:0.7rem;font-weight:800;letter-spacing:0.4px;cursor:pointer;width:100%;">Reiniciar</button>
            </div>
            <!-- Notifications mobile panel -->
            <div id="mobile-notifications-panel" style="display:none;">
                <h3 style="margin:0 0 0.8rem;font-size:1rem;font-weight:800;letter-spacing:0.5px;color:var(--primary);text-align:center;">Notificações</h3>
                <div id="mobile-notifications-list" style="display:flex;flex-direction:column;gap:0.6rem;max-height:300px;overflow-y:auto;">
                    <div style="text-align:center;color:#999;font-size:0.75rem;padding:1rem;">Nenhuma notificação</div>
                </div>
            </div>
        </div>
        
        <div class="search-box">
            <input type="text" id="search-input" placeholder="Pesquisar..." onkeydown="if(event.key==='Enter')executarBusca()">
            <button class="search-btn" onclick="executarBusca()">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
                    <circle cx="11" cy="11" r="7"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
            </button>
            <a href="/novo-post" class="search-btn" aria-label="Criar postagem" title="Criar postagem" style="text-decoration:none;">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
            </a>
        </div>
        
        <div class="layout">
            <div id="feed-list">
                {posts_html}
            </div>
            <aside class="side-col">
                <!-- Navegação rápida: Educação e Em breve -->
                <div style="display:flex;gap:0.8rem;margin:0 0 1.2rem;">
                    <a href="/educacao" style="flex:1;text-decoration:none;background:linear-gradient(135deg, #9B5DE5 0%, #7B4BC4 100%);padding:1rem 1.1rem;border-radius:20px;display:flex;align-items:center;gap:0.7rem;font-size:1rem;font-weight:800;color:#ffffff;letter-spacing:0.4px;transition:all 0.25s ease;box-shadow:0 6px 20px rgba(155,93,229,0.35);border:none;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                        </svg>
                        Educação
                    </a>
                    <div style="flex:1;background:linear-gradient(135deg, #b8a4c9 0%, #9d8ab5 100%);padding:1rem 1.1rem;border-radius:20px;display:flex;align-items:center;gap:0.7rem;font-size:1rem;font-weight:800;color:#ffffff;letter-spacing:0.4px;box-shadow:0 6px 20px rgba(155,93,229,0.25);border:none;opacity:0.85;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                        Em breve
                    </div>
                </div>
                <!-- Card Amigues (com botões de ações e lista de amigos) -->
                <div class="side-card" style="padding:1.3rem 1.3rem 1.1rem;margin-bottom:1rem;">
                    <!-- Botões de ações rápidas -->
                    <div style="display:flex;align-items:center;justify-content:center;gap:0.6rem;margin:0 0 0.8rem;">
                        <button onclick="location.href='/suporte'" class="action-btn" title="Suporte" aria-label="Suporte">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="10"></circle>
                                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                                <line x1="12" y1="17" x2="12.01" y2="17"></line>
                            </svg>
                        </button>
                        <button onclick="location.href='/configuracoes'" class="action-btn" title="Configurações" aria-label="Configurações">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="3"></circle>
                                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                            </svg>
                        </button>
                        <button onclick="toggleNotifications()" class="action-btn" title="Notificações" aria-label="Notificações" style="position:relative;">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                            </svg>
                            <span id="notifications-badge" style="display:none;position:absolute;top:-4px;right:-4px;background:#ff9800;color:#fff;font-size:0.6rem;padding:2px 5px;border-radius:10px;font-weight:700;">0</span>
                        </button>
                        {admin_btn_html}
                    </div>
                    <!-- Painel de notificações -->
                    <div id="notifications-panel" style="display:none;margin-bottom:0.8rem;border-bottom:1px solid var(--border);padding-bottom:0.8rem;">
                        <div id="notifications-list" style="display:flex;flex-direction:column;gap:0.6rem;max-height:200px;overflow-y:auto;">
                            <div style="text-align:center;color:#999;font-size:0.75rem;padding:0.5rem;">Nenhuma notificação</div>
                        </div>
                    </div>
                    <!-- Divisor -->
                    <div style="height:1px;background:var(--border);margin:0 0 0.8rem;"></div>
                    <!-- Seção Amigues -->
                    <h3 style="margin:0 0 0.8rem;font-size:1rem;font-weight:800;letter-spacing:0.5px;color:var(--primary);text-align:center;">Amigues</h3>
                    <div id="amigues-list" style="display:flex;flex-direction:column;gap:0.65rem;min-height:20px;"></div>
                    <div id="amigues-empty" style="font-size:0.7rem;opacity:0.7;line-height:1.3;text-align:center;">Sem amigues ainda. Faça amizades para aparecerem aqui.</div>
                </div>
                <div class="side-card">
                    <h3>📣 Novidades</h3>
                    {divulgacoes_html}
                </div>
                <!-- Jogo da Velha -->
                <div class="side-card">
                    <h3 style="margin:0.15rem 0 0.55rem;font-size:0.95rem;letter-spacing:0.5px;font-weight:800;color:var(--primary);"># Jogo da Velha</h3>
                    <p style="margin:0.2rem 0 0.7rem;font-size:0.7rem;color:#555;font-weight:600;">Jogue contra o <strong>Robo</strong>. Você é o <strong>X</strong>.</p>
                    <div id="ttt_status" style="font-size:0.72rem;font-weight:800;color:var(--primary);letter-spacing:0.4px;margin:0 0 0.6rem;">Sua vez: você é X</div>
                    <div id="ttt_board" class="ttt-board">
                        <button type="button" data-i="0" class="ttt-cell"></button>
                        <button type="button" data-i="1" class="ttt-cell"></button>
                        <button type="button" data-i="2" class="ttt-cell"></button>
                        <button type="button" data-i="3" class="ttt-cell"></button>
                        <button type="button" data-i="4" class="ttt-cell"></button>
                        <button type="button" data-i="5" class="ttt-cell"></button>
                        <button type="button" data-i="6" class="ttt-cell"></button>
                        <button type="button" data-i="7" class="ttt-cell"></button>
                        <button type="button" data-i="8" class="ttt-cell"></button>
                    </div>
                    <button id="ttt_reset" type="button" style="margin-top:0.8rem;background:var(--primary);color:#fff;border:none;border-radius:14px;padding:0.5rem 0.9rem;font-size:0.7rem;font-weight:800;letter-spacing:0.4px;cursor:pointer;width:100%;">Reiniciar</button>
                </div>
            </aside>
        </div>
    </main>
    </div>
    <script>
    window.currentUser = "{user_username_js}";
    window.currentUserId = {user_id};
    
    // Helper function to escape HTML in JS
    function escapeHtml(text) {{
        if (!text) return '';
        const map = {{'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;'}};
        return String(text).replace(/[&<>"']/g, c => map[c]);
    }}
    
    async function likePost(postId) {{
        try {{
            const res = await fetch('/api/posts/' + postId + '/like', {{method: 'POST'}});
            const data = await res.json();
            // Reload to update
            location.reload();
        }} catch(e) {{
            console.error(e);
        }}
    }}
    
    async function toggleComments(postId) {{
        const div = document.getElementById('comments-' + postId);
        if(div.style.display === 'none') {{
            div.style.display = 'block';
            try {{
                const res = await fetch('/api/posts/' + postId + '/comentarios');
                const data = await res.json();
                const comentarios = data.comentarios || [];
                if(comentarios.length === 0) {{
                    div.innerHTML = '<p style="font-size:0.75rem;color:var(--text-dim);">Nenhum comentário.</p>';
                }} else {{
                    div.innerHTML = comentarios.map(c => '<div style="background:#f9fafb;padding:0.5rem 0.7rem;border-radius:10px;margin-bottom:0.4rem;font-size:0.8rem;"><strong style="color:var(--primary);">@' + escapeHtml(c.usuario) + '</strong><p style="margin:0.2rem 0 0;">' + escapeHtml(c.conteudo) + '</p></div>').join('');
                }}
            }} catch(e) {{
                div.innerHTML = '<p style="font-size:0.75rem;color:#c00;">Erro ao carregar comentários.</p>';
            }}
        }} else {{
            div.style.display = 'none';
        }}
    }}
    
    function executarBusca() {{
        const termo = document.getElementById('search-input').value.trim();
        if(termo) {{
            // Recarrega com filtro
            location.href = '/?q=' + encodeURIComponent(termo);
        }}
    }}
    
    // Mobile Actions Card Toggle
    function toggleMobileActionsCard() {{
        const card = document.getElementById('mobile-actions-card');
        const triangleSvg = document.getElementById('triangle-svg');
        if (card.classList.contains('visible')) {{
            card.classList.remove('visible');
            if (triangleSvg) triangleSvg.style.transform = 'rotate(0deg)';
        }} else {{
            card.classList.add('visible');
            if (triangleSvg) triangleSvg.style.transform = 'rotate(180deg)';
        }}
    }}
    
    // Mobile Amigues Toggle
    function toggleMobileAmigues() {{
        const panel = document.getElementById('mobile-amigues-panel');
        const tttPanel = document.getElementById('mobile-ttt-panel');
        const notifPanel = document.getElementById('mobile-notifications-panel');
        if (tttPanel) tttPanel.style.display = 'none';
        if (notifPanel) notifPanel.style.display = 'none';
        if (panel.style.display === 'none') {{
            panel.style.display = 'block';
            loadMobileAmigues();
        }} else {{
            panel.style.display = 'none';
        }}
    }}
    
    // Mobile Tic-Tac-Toe Toggle
    function toggleMobileTicTacToe() {{
        const panel = document.getElementById('mobile-ttt-panel');
        const amiguesPanel = document.getElementById('mobile-amigues-panel');
        const notifPanel = document.getElementById('mobile-notifications-panel');
        if (amiguesPanel) amiguesPanel.style.display = 'none';
        if (notifPanel) notifPanel.style.display = 'none';
        if (panel.style.display === 'none') {{
            panel.style.display = 'block';
        }} else {{
            panel.style.display = 'none';
        }}
    }}
    
    // Mobile Notifications Toggle
    function toggleMobileNotifications() {{
        const panel = document.getElementById('mobile-notifications-panel');
        const amiguesPanel = document.getElementById('mobile-amigues-panel');
        const tttPanel = document.getElementById('mobile-ttt-panel');
        if (amiguesPanel) amiguesPanel.style.display = 'none';
        if (tttPanel) tttPanel.style.display = 'none';
        if (panel.style.display === 'none') {{
            panel.style.display = 'block';
            loadNotifications('mobile-notifications-list', 'mobile-notif-badge');
        }} else {{
            panel.style.display = 'none';
        }}
    }}
    
    // Desktop Notifications Toggle
    function toggleNotifications() {{
        const panel = document.getElementById('notifications-panel');
        if (panel.style.display === 'none') {{
            panel.style.display = 'block';
            loadNotifications('notifications-list', 'notifications-badge');
        }} else {{
            panel.style.display = 'none';
        }}
    }}
    
    // Load notifications
    async function loadNotifications(listId, badgeId) {{
        const list = document.getElementById(listId);
        const badge = document.getElementById(badgeId);
        try {{
            const res = await fetch('/api/notifications');
            const data = await res.json();
            const notifications = data.notifications || [];
            if (notifications.length === 0) {{
                list.innerHTML = '<div style="text-align:center;color:#999;font-size:0.75rem;padding:1rem;">Nenhuma notificação</div>';
                if (badge) badge.style.display = 'none';
            }} else {{
                list.innerHTML = notifications.map(n => 
                    '<a href="' + escapeHtml(n.link || '#') + '" class="notif-item"><div style="font-size:0.75rem;color:#333;line-height:1.4;">' + escapeHtml(n.message || n.mensagem) + '</div><div style="font-size:0.65rem;color:#999;margin-top:0.3rem;">' + escapeHtml(n.time || n.data || '') + '</div></a>'
                ).join('');
                if (badge) {{
                    badge.textContent = notifications.length;
                    badge.style.display = 'inline-block';
                }}
            }}
        }} catch (e) {{
            list.innerHTML = '<div style="text-align:center;color:#f44;font-size:0.75rem;padding:1rem;">Erro ao carregar</div>';
        }}
    }}
    
    // Load amigues for mobile
    async function loadMobileAmigues() {{
        const wrap = document.getElementById('mobile-amigues-list');
        const empty = document.getElementById('mobile-amigues-empty');
        try {{
            const res = await fetch('/api/amigues');
            if (res.status === 401) {{
                empty.style.display = 'block';
                return;
            }}
            const data = await res.json();
            const list = data.amigues || [];
            if (list.length === 0) {{
                empty.style.display = 'block';
                return;
            }}
            empty.style.display = 'none';
            wrap.innerHTML = list.slice(0, 12).map(u => {{
                const fp = (u.foto_perfil || '').trim() || '/static/img/perfil.png';
                const src = /^https?:\\/\\//i.test(fp) ? fp : ('/static/' + fp);
                return '<div style="display:flex;align-items:center;gap:0.7rem;padding:0.5rem 0.6rem;border-radius:16px;background:#f9fafb;border:1px solid #e5e7eb;"><img src="' + escapeHtml(src) + '" alt="Avatar" style="width:38px;height:38px;border-radius:50%;object-fit:cover;border:2px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,0.15);"><div style="flex:1;min-width:0;"><a href="/perfil/' + escapeHtml(u.username || u.id) + '" style="display:block;font-weight:700;font-size:0.7rem;color:var(--primary);text-decoration:none;letter-spacing:0.4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">' + escapeHtml(u.username) + '</a></div></div>';
            }}).join('');
        }} catch (e) {{
            empty.style.display = 'block';
        }}
    }}
    
    // Load amigues for desktop
    async function loadAmigues() {{
        const wrap = document.getElementById('amigues-list');
        const empty = document.getElementById('amigues-empty');
        if (!wrap) return;
        try {{
            const res = await fetch('/api/amigues');
            if (res.status === 401) {{
                empty.style.display = 'block';
                return;
            }}
            const data = await res.json();
            const list = data.amigues || [];
            if (list.length === 0) {{
                empty.style.display = 'block';
                return;
            }}
            empty.style.display = 'none';
            wrap.innerHTML = list.slice(0, 12).map(u => {{
                const fp = (u.foto_perfil || '').trim() || '/static/img/perfil.png';
                const src = /^https?:\\/\\//i.test(fp) ? fp : ('/static/' + fp);
                return '<a href="/perfil/' + escapeHtml(u.username || u.id) + '" style="display:flex;align-items:center;gap:0.6rem;text-decoration:none;padding:0.35rem 0.4rem;border-radius:14px;transition:background 0.18s;"><img src="' + escapeHtml(src) + '" alt="' + escapeHtml(u.username) + '" style="width:38px;height:38px;border-radius:50%;object-fit:cover;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.15);background:#eee;"><span style="display:flex;flex-direction:column;"><strong style="font-size:0.75rem;letter-spacing:0.4px;color:var(--text);">@' + escapeHtml(u.username) + '</strong><span style="font-size:0.6rem;opacity:0.65;max-width:160px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">' + escapeHtml(u.nome || '') + '</span></span></a>';
            }}).join('');
        }} catch (e) {{
            empty.style.display = 'block';
        }}
    }}
    
    // Tic-Tac-Toe Game (Desktop)
    (function() {{
        var boardEl = document.getElementById('ttt_board');
        var statusEl = document.getElementById('ttt_status');
        var resetEl = document.getElementById('ttt_reset');
        if(!boardEl || !statusEl || !resetEl) return;
        var board = new Array(9).fill('');
        var HUMAN = 'X', AI = 'O';
        var gameOver = false;
        function setStatus(msg){{ if(statusEl) statusEl.textContent = msg; }}
        function render(){{
            var cells = boardEl.querySelectorAll('button[data-i]');
            cells.forEach(function(btn){{
                var i = +btn.getAttribute('data-i');
                var v = board[i];
                btn.textContent = v || '';
                btn.disabled = !!v || gameOver;
            }});
        }}
        var wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
        function winner(b){{
            for(var k=0;k<wins.length;k++){{
                var a=wins[k][0], c=wins[k][1], d=wins[k][2];
                if(b[a] && b[a]===b[c] && b[c]===b[d]) return b[a];
            }}
            return null;
        }}
        function empties(b){{ var r=[]; for(var i=0;i<9;i++){{ if(!b[i]) r.push(i);}} return r; }}
        function isDraw(b){{ return empties(b).length===0 && !winner(b); }}
        function tryWinMove(b, p){{
            var e = empties(b);
            for(var i=0;i<e.length;i++){{
                var idx = e[i];
                b[idx] = p;
                var w = winner(b);
                b[idx] = '';
                if(w===p) return idx;
            }}
            return -1;
        }}
        function aiPick(){{
            var idx = tryWinMove(board, AI); if(idx!==-1) return idx;
            idx = tryWinMove(board, HUMAN); if(idx!==-1) return idx;
            if(!board[4]) return 4;
            var corners = [0,2,6,8];
            for(var i=0;i<corners.length;i++){{ if(!board[corners[i]]) return corners[i]; }}
            var sides = [1,3,5,7];
            for(var j=0;j<sides.length;j++){{ if(!board[sides[j]]) return sides[j]; }}
            return -1;
        }}
        function endIfNeeded(){{
            var w = winner(board);
            if(w){{ gameOver=true; setStatus(w===HUMAN ? 'Você venceu!' : 'Robo venceu!'); render(); return true; }}
            if(isDraw(board)){{ gameOver=true; setStatus('Empate.'); render(); return true; }}
            return false;
        }}
        function humanMove(i){{
            if(gameOver || board[i]) return;
            board[i] = HUMAN;
            render();
            if(endIfNeeded()) return;
            setStatus('Robo pensando...');
            setTimeout(function(){{
                var m = aiPick();
                if(m>=0){{ board[m] = AI; }}
                render();
                if(!endIfNeeded()) setStatus('Sua vez: você é X');
            }}, 220);
        }}
        boardEl.addEventListener('click', function(ev){{
            var t = ev.target;
            if(!(t && t.matches('button[data-i]'))) return;
            var i = +t.getAttribute('data-i');
            humanMove(i);
        }});
        resetEl.addEventListener('click', function(){{
            board = new Array(9).fill('');
            gameOver=false;
            setStatus('Sua vez: você é X');
            render();
        }});
        setStatus('Sua vez: você é X');
        render();
    }})();
    
    // Tic-Tac-Toe Game (Mobile)
    (function() {{
        var boardEl = document.getElementById('mobile_ttt_board');
        var statusEl = document.getElementById('mobile_ttt_status');
        var resetEl = document.getElementById('mobile_ttt_reset');
        if(!boardEl || !statusEl || !resetEl) return;
        var board = new Array(9).fill('');
        var HUMAN = 'X', AI = 'O';
        var gameOver = false;
        function setStatus(msg){{ if(statusEl) statusEl.textContent = msg; }}
        function render(){{
            var cells = boardEl.querySelectorAll('button[data-i]');
            cells.forEach(function(btn){{
                var i = +btn.getAttribute('data-i');
                var v = board[i];
                btn.textContent = v || '';
                btn.disabled = !!v || gameOver;
            }});
        }}
        var wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
        function winner(b){{
            for(var k=0;k<wins.length;k++){{
                var a=wins[k][0], c=wins[k][1], d=wins[k][2];
                if(b[a] && b[a]===b[c] && b[c]===b[d]) return b[a];
            }}
            return null;
        }}
        function empties(b){{ var r=[]; for(var i=0;i<9;i++){{ if(!b[i]) r.push(i);}} return r; }}
        function isDraw(b){{ return empties(b).length===0 && !winner(b); }}
        function tryWinMove(b, p){{
            var e = empties(b);
            for(var i=0;i<e.length;i++){{
                var idx = e[i];
                b[idx] = p;
                var w = winner(b);
                b[idx] = '';
                if(w===p) return idx;
            }}
            return -1;
        }}
        function aiPick(){{
            var idx = tryWinMove(board, AI); if(idx!==-1) return idx;
            idx = tryWinMove(board, HUMAN); if(idx!==-1) return idx;
            if(!board[4]) return 4;
            var corners = [0,2,6,8];
            for(var i=0;i<corners.length;i++){{ if(!board[corners[i]]) return corners[i]; }}
            var sides = [1,3,5,7];
            for(var j=0;j<sides.length;j++){{ if(!board[sides[j]]) return sides[j]; }}
            return -1;
        }}
        function endIfNeeded(){{
            var w = winner(board);
            if(w){{ gameOver=true; setStatus(w===HUMAN ? 'Você venceu!' : 'Robo venceu!'); render(); return true; }}
            if(isDraw(board)){{ gameOver=true; setStatus('Empate.'); render(); return true; }}
            return false;
        }}
        function humanMove(i){{
            if(gameOver || board[i]) return;
            board[i] = HUMAN;
            render();
            if(endIfNeeded()) return;
            setStatus('Robo pensando...');
            setTimeout(function(){{
                var m = aiPick();
                if(m>=0){{ board[m] = AI; }}
                render();
                if(!endIfNeeded()) setStatus('Sua vez: você é X');
            }}, 220);
        }}
        boardEl.addEventListener('click', function(ev){{
            var t = ev.target;
            if(!(t && t.matches('button[data-i]'))) return;
            var i = +t.getAttribute('data-i');
            humanMove(i);
        }});
        resetEl.addEventListener('click', function(){{
            board = new Array(9).fill('');
            gameOver=false;
            setStatus('Sua vez: você é X');
            render();
        }});
        setStatus('Sua vez: você é X');
        render();
    }})();
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {{
        loadAmigues();
        loadNotifications('notifications-list', 'notifications-badge');
    }});
    </script>
{page_footer(True)}"""

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
    <div class="content-wrapper">
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
    </div>
{page_footer(current_user is not None)}"""

    async def _login_page(self, db, current_user, request, method):
        """Página de Login."""
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
            <p style="font-size: 0.6rem; color: #999; text-align: center; margin-top: 1.5rem;">{SCRIPT_VERSION}</p>
        </div>
    </div>
    {mobile_nav(False)}
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
    {mobile_nav(False)}
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
{page_footer(current_user is not None)}"""

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
{page_footer(current_user is not None)}"""

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
{page_footer(current_user is not None)}"""

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
{page_footer(current_user is not None)}"""

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
{page_footer(current_user is not None)}"""

    async def _profile_page(self, db, current_user, username):
        """Página de perfil de usuárie."""
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
{page_footer(current_user is not None)}"""
        except Exception as e:
            return self._not_found_page(f'/u/{username}')

    async def _novo_post_page(self, db, current_user, request, method):
        """Página para criar novo post."""
        if not current_user:
            return redirect('/login')
        
        # Validate current_user has required 'id' field
        user_id = current_user.get('id') if isinstance(current_user, dict) else None
        if user_id is None:
            console.error("[NovoPost] current_user.id is None")
            return redirect('/login')
        
        error_msg = ""
        success_msg = ""
        
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
        
        error_html = f'<div class="error-msg" style="background:#ffebee;color:#c62828;padding:0.8rem;border-radius:10px;margin-bottom:1rem;font-size:0.85rem;">{error_msg}</div>' if error_msg else ""
        
        return f"""{page_head("Novo Post — Gramátike")}
    <header class="site-head">
        <h1 class="logo">Gramátike</h1>
    </header>
    <main>
        <div class="card" style="max-width: 600px; margin: 0 auto;">
            <h2 style="color: var(--primary); margin-bottom: 1rem;">Criar Post</h2>
            {error_html}
            <form method="POST" action="/novo-post">
                <div class="form-group">
                    <label>O que você está pensando?</label>
                    <textarea name="conteudo" rows="5" style="width:100%;padding:0.8rem;border:1.5px solid #d9e1ea;border-radius:12px;font-family:'Nunito',sans-serif;font-size:0.95rem;resize:vertical;" placeholder="Escreva algo..." required></textarea>
                </div>
                <div style="display:flex;gap:1rem;justify-content:flex-end;margin-top:1rem;">
                    <a href="/" class="btn" style="background:#f1edff;color:var(--primary);">Cancelar</a>
                    <button type="submit" class="button-primary" style="width:auto;padding:0.7rem 1.5rem;">Publicar</button>
                </div>
            </form>
        </div>
    </main>
{page_footer(True)}"""

    async def _meu_perfil_page(self, db, current_user):
        """Página do perfil do usuário logado."""
        if not current_user:
            return redirect('/login')
        
        user = current_user
        username = user.get('username', '')
        
        posts = []
        followers = []
        following = []
        
        if db and DB_AVAILABLE:
            try:
                posts = await get_posts(db, user_id=user['id'], per_page=20)
                followers = await get_followers(db, user['id'])
                following = await get_following(db, user['id'])
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
        
        # Usar helper para URL da foto
        foto_perfil = normalize_image_url(user.get('foto_perfil'))
        username_escaped = escape_html(username)
        user_nome = escape_html(user.get('nome') or '@' + username)
        user_bio = escape_html(user.get('bio', ''))
        
        return f"""{page_head(f"Meu Perfil — Gramátike")}
    <header class="site-head">
        <h1 class="logo">Gramátike</h1>
    </header>
    <main>
        <div class="card" style="text-align: center; margin-bottom: 1.5rem;">
            <img src="{foto_perfil}" 
                 alt="@{username_escaped}" 
                 style="width: 80px; height: 80px; border-radius: 50%; margin-bottom: 1rem; object-fit: cover;">
            <h2 style="color: var(--primary); margin-bottom: 0.3rem;">
                {user_nome}
            </h2>
            <p style="color: var(--text-dim); font-size: 0.85rem; margin-bottom: 0.8rem;">@{username_escaped}</p>
            {f'<p style="margin-bottom: 1rem;">{user_bio}</p>' if user_bio else ''}
            <div style="display: flex; gap: 2rem; justify-content: center; margin-bottom: 1rem; font-size: 0.85rem;">
                <span><strong>{len(followers)}</strong> seguidores</span>
                <span><strong>{len(following)}</strong> seguindo</span>
            </div>
            <a href="/configuracoes" class="btn btn-primary">Editar Perfil</a>
        </div>
        
        <h3 style="color: var(--primary); margin-bottom: 1rem;">Meus Posts</h3>
        {posts_html}
        
        <div style="text-align:center;margin-top:2rem;">
            <a href="/logout" style="font-size:0.85rem;color:#c00;text-decoration:none;font-weight:700;">Sair da Conta</a>
        </div>
    </main>
{page_footer(True)}"""

    async def _configuracoes_page(self, db, current_user):
        """Página de configurações do usuário."""
        if not current_user:
            return redirect('/login')
        
        user = current_user
        # Escape user data for safe display
        username = escape_html(user.get('username', ''))
        email = escape_html(user.get('email', ''))
        nome = escape_html(user.get('nome', 'Não informado'))
        
        return f"""{page_head("Configurações — Gramátike")}
    <header class="site-head">
        <h1 class="logo">Gramátike</h1>
    </header>
    <main>
        <div class="card" style="max-width: 500px; margin: 0 auto;">
            <h2 style="color: var(--primary); margin-bottom: 1.5rem;">Configurações</h2>
            
            <div style="margin-bottom: 2rem;">
                <h3 style="font-size: 1rem; margin-bottom: 0.8rem;">Informações da Conta</h3>
                <p style="font-size: 0.85rem; margin-bottom: 0.5rem;"><strong>Usuárie:</strong> @{username}</p>
                <p style="font-size: 0.85rem; margin-bottom: 0.5rem;"><strong>Email:</strong> {email}</p>
                <p style="font-size: 0.85rem;"><strong>Nome:</strong> {nome}</p>
            </div>
            
            <div style="border-top: 1px solid var(--border); padding-top: 1.5rem;">
                <h3 style="font-size: 1rem; margin-bottom: 0.8rem;">Ações</h3>
                <div style="display: flex; flex-direction: column; gap: 0.8rem;">
                    <a href="/perfil" class="btn" style="background:#f1edff;color:var(--primary);text-align:center;">← Voltar ao Perfil</a>
                    <a href="/" class="btn" style="background:#f1edff;color:var(--primary);text-align:center;">Ir para o Feed</a>
                    <a href="/logout" class="btn" style="background:#ffebee;color:#c00;text-align:center;">Sair da Conta</a>
                </div>
            </div>
        </div>
    </main>
{page_footer(True)}"""

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
{page_footer(False)}"""

    async def _admin_page(self, db, current_user):
        """Admin Dashboard page."""
        # Check if user is admin
        if not current_user:
            return f"""{page_head("Acesso Restrito — Gramátike")}
    <header class="site-head">
        <h1 class="logo">Gramátike</h1>
    </header>
    <main>
        <div class="card" style="text-align: center;">
            <h2 style="color: var(--primary);">Acesso Restrito</h2>
            <p style="color: var(--text-dim); margin: 1rem 0;">
                Você precisa estar logado para acessar esta página.
            </p>
            <a href="/login" class="btn btn-primary">Fazer Login</a>
        </div>
    </main>
{page_footer(False)}"""
        
        is_admin = current_user.get('is_admin', False) or current_user.get('is_superadmin', False)
        if not is_admin:
            return f"""{page_head("Acesso Restrito — Gramátike")}
    <header class="site-head">
        <h1 class="logo">Gramátike</h1>
    </header>
    <main>
        <div class="card" style="text-align: center;">
            <h2 style="color: var(--primary);">Acesso Restrito</h2>
            <p style="color: var(--text-dim); margin: 1rem 0;">
                Você não tem permissão para acessar o painel de administração.
            </p>
            <a href="/" class="btn btn-primary">Voltar ao início</a>
        </div>
    </main>
{page_footer(False)}"""
        
        # Get admin stats
        stats = await get_admin_stats(db) if db else {}
        total_users = stats.get('total_users', 0)
        total_posts = stats.get('total_posts', 0)
        total_comments = stats.get('total_comments', 0)
        
        return f"""{page_head("Painel de Controle — Gramátike", """
        .admin-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin: 2rem 0; }}
        .admin-stat {{ background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 1.5rem; text-align: center; }}
        .admin-stat h3 {{ color: var(--primary); font-size: 2rem; margin: 0; }}
        .admin-stat p {{ color: var(--text-dim); margin: 0.5rem 0 0; font-size: 0.9rem; }}
        .admin-section {{ background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 1.5rem; margin: 1.5rem 0; }}
        .admin-section h2 {{ color: var(--primary); margin: 0 0 1rem; font-size: 1.2rem; }}
        """)}
    <header class="site-head">
        <h1 class="logo">Gramátike</h1>
        <a href="/" style="position:absolute;right:24px;top:50%;transform:translateY(-50%);color:#fff;text-decoration:none;font-weight:700;">← Voltar</a>
    </header>
    <div class="content-wrapper">
    <main style="max-width: 1000px; margin: 0 auto; padding: 2rem;">
        <h1 style="color: var(--primary); margin-bottom: 1rem;">Painel de Controle</h1>
        <p style="color: var(--text-dim); margin-bottom: 2rem;">Bem-vindo, {escape_html(current_user.get('username', 'Admin'))}!</p>
        
        <div class="admin-grid">
            <div class="admin-stat">
                <h3>{total_users}</h3>
                <p>Usuáries</p>
            </div>
            <div class="admin-stat">
                <h3>{total_posts}</h3>
                <p>Posts</p>
            </div>
            <div class="admin-stat">
                <h3>{total_comments}</h3>
                <p>Comentários</p>
            </div>
        </div>
        
        <div class="admin-section">
            <h2>Ações Rápidas</h2>
            <div style="display: flex; flex-wrap: wrap; gap: 1rem;">
                <a href="/educacao" class="btn btn-primary">Educação</a>
                <a href="/" class="btn btn-primary">Feed</a>
            </div>
        </div>
    </main>
    </div>
{page_footer(False)}"""
