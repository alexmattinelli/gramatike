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
# Para deploy: npm run deploy (ou via Cloudflare Dashboard)
# Verificar versão: GET /api/health ou /api/info
SCRIPT_VERSION = "v2025.11.28.c"  # Auto-synced CSS from index.html via scripts/sync_css.py

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
--font-base: 'Nunito', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
--font-brand: 'Mansalva', cursive; /* Fonte do título/logo */
}
body, p, label, input, button, a, span, li, td, th, div { font-family: var(--font-base) !important; }
h1, h2, h3, h4, h5, h6 { font-family: var(--font-base); font-weight:800; line-height:1.15; margin:0 0 .75em; }
.logo, h1.logo { font-family: var(--font-brand) !important; font-weight:400; letter-spacing:1px; margin:0; }
button { font-family: var(--font-base); font-weight:600; }
.nunito-font { font-family: var(--font-base) !important; }
:root {
--primary: #9B5DE5; /* unificado */
--primary-dark: #9B5DE5; /* unificado */
--text: #222;
--text-secondary: #666;
--bg: #f7f8ff;
--card: #ffffff;
--border: #e5e7eb;
--input: #ffffff;
--shadow: rgba(130, 87, 229, 0.12);
}
body.dark {
--text: #e5e7eb;
}
html, body { height:100%; overflow-x:hidden; }
body { font-family: 'Nunito', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; background: var(--bg); margin:0; display:flex; flex-direction:column; min-height:100vh; }
.content-wrapper { background: var(--bg); flex:1; border-top-left-radius:35px; border-top-right-radius:35px; margin-top:-30px; padding-top:30px; position:relative; z-index:1; }
h1,h2,h3 { font-family: var(--font-base); }
/* HEADER ROXO (sem curvas - apenas a área de conteúdo terá bordas arredondadas) */
header.site-head { background: var(--primary); padding:28px clamp(16px,4vw,40px) 46px; border-radius:0; position:relative; display:flex; flex-direction:column; align-items:center; }
.logo { font-family: var(--font-brand) !important; font-size:2.5rem; color:#fff; letter-spacing:1px; font-weight:400; }
/* Mobile: Header mais compacto */
@media (max-width: 980px){
header.site-head { padding:18px clamp(12px,3vw,24px) 28px; }
.logo { font-size:1.8rem; }
}
/* Avatar do usuário no cabeçalho (maior e mais visível) */
.profile-avatar-link { position:absolute; right:24px; top:50%; transform:translateY(-50%); display:inline-flex; align-items:center; justify-content:center; width:64px; height:64px; border-radius:50%; border:3px solid #ffffff55; box-shadow:0 4px 14px rgba(0,0,0,.25); overflow:hidden; background:#ffffff22; backdrop-filter:blur(4px); -webkit-backdrop-filter:blur(4px); cursor:pointer; text-decoration:none; transition: box-shadow .25s, transform .18s; }
.profile-avatar-link:hover { box-shadow:0 6px 20px rgba(0,0,0,.32); }
.profile-avatar-link:active { transform:translateY(-50%) scale(.95); }
.profile-avatar-link img { width:100%; height:100%; object-fit:cover; display:block; }
.profile-avatar-link span.initial { font-size:1.9rem; font-weight:800; color:#fff; letter-spacing:.5px; }
/* Tooltip simples acessível */
.profile-avatar-link[data-tooltip]:hover::after, .profile-avatar-link[data-tooltip]:focus-visible::after { content:attr(data-tooltip); position:absolute; bottom:-6px; left:50%; transform:translate(-50%,100%); background:#222; color:#fff; font-size:.6rem; font-weight:600; padding:4px 7px 5px; border-radius:8px; white-space:nowrap; box-shadow:0 4px 12px rgba(0,0,0,.35); letter-spacing:.5px; }
@media (max-width:640px){ .profile-avatar-link { width:52px; height:52px; right:16px; } .profile-avatar-link span.initial { font-size:1.5rem; } }
@media (max-width: 980px){ .profile-avatar-link { display:none !important; } }
body, p, input, textarea, select, button { font-family:'Nunito', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; }
/* Removido layout 3 colunas – voltando ao estilo anterior */
/* Form nova postagem */
#post-form { display:flex; flex-direction:column; gap:10px; margin-top:4px; }
#post-form textarea { width:100%; min-height:110px; border:1px solid #d9dbe3; border-radius:20px; padding:1rem 1.1rem 1.2rem; resize:vertical; font-family:'Nunito'; font-size:.95rem; background:#fafafa; line-height:1.45; }
#post-form textarea:focus { outline:2px solid #9B5DE5; outline-offset:2px; background:#fff; }
#post-form button { align-self:flex-end; background:#9B5DE5; color:#fff; padding:.7rem 1.9rem; border-radius:50px; border:none; font-size:.8rem; font-weight:700; letter-spacing:.65px; cursor:pointer; box-shadow:0 6px 16px rgba(155,93,229,.4); }
#post-form button:hover { filter:brightness(1.08); }
/* Feed controls (selects clássicos) */
/* (Removidos selects antigos) */
.search-wrap { position:relative; flex:1; }
.autocomplete { z-index:40; }
/* Post cards */
section#feed article.post { background:#ffffff; border:1px solid #e5e7eb; padding:1.7rem 2rem 1.4rem; border-radius:28px; margin-bottom:2.2rem; box-shadow:0 12px 26px rgba(0,0,0,.08); transition: box-shadow .25s; }
section#feed article.post:hover { box-shadow:0 18px 38px rgba(0,0,0,.14); }
/* Novo: aplicar mesmo estilo aos cards renderizados em #feed-list */
#feed-list article.post { background:#fff; border:1px solid #e5e7eb; padding:1.6rem 1.9rem 1.3rem; border-radius:26px; margin:0 0 2rem; box-shadow:0 10px 24px -6px rgba(0,0,0,.10); position:relative; overflow:hidden; }
/* Gradiente removido dos posts do feed */
#feed-list article.post::before { content:""; display:none; }
#feed-list article.post:hover { box-shadow:0 16px 40px -6px rgba(0,0,0,.18); }
body.dark #feed-list article.post { background:#1e293b; border:1px solid #334155; box-shadow:0 8px 22px -4px rgba(0,0,0,.55); }
/* Gradiente removido do dark mode */
body.dark #feed-list article.post::before { display:none; }
/* Todos os posts com fundo branco uniforme */
#feed-list article.post:nth-child(even) { background:#fff; }
body.dark #feed-list article.post:nth-child(even) { background:#1e293b; }
.post-header img.post-avatar { width:52px; height:52px; border-radius:50%; object-fit:cover; border:3px solid #fff; box-shadow:0 3px 10px rgba(0,0,0,.18); }
.post-username strong { font-weight:800; }
/* Quick menu */
.quick-menu { position:absolute; top:70px; right:10px; background:#fff; border:1px solid #e5e7eb; border-radius:20px; padding:.55rem .6rem; display:flex; flex-direction:column; gap:.3rem; min-width:170px; box-shadow:0 18px 40px -10px rgba(0,0,0,.28); animation:fadeIn .18s ease; z-index:300; }
.quick-menu a, .quick-menu button { all:unset; font-family:'Nunito'; font-size:.75rem; font-weight:700; letter-spacing:.5px; padding:.6rem .9rem; border-radius:14px; cursor:pointer; color:#333; display:block; }
.quick-menu a:hover, .quick-menu button:hover { background:#f3f4f6; }
.quick-menu .sair-btn { color:#9B5DE5; }
@keyframes fadeIn { from { opacity:0; transform: translateY(-4px);} to { opacity:1; transform:translateY(0);} }
.head-btn { font-family:'Nunito'; font-weight:700; font-size:.75rem; letter-spacing:.5px; cursor:pointer; }
/* Footer removido conforme solicitado */
@media (max-width:640px){ .card-block{padding:1.8rem 1.4rem 2.2rem;} header.site-head{padding:24px 18px 38px;} .logo{font-size:2.4rem;} }
nav a { color:#fff; text-decoration:none; margin-left:1.5rem; font-weight:600; position:relative; transition:opacity .2s; }
nav a:hover { opacity:.85; }
main { max-width:920px; margin:2rem auto 4rem; padding:0 1.2rem; flex:1 0 auto; }
.feed-controls { display:flex; gap:1.2rem; align-items:flex-end; justify-content:space-between; margin:1.2rem 0 2rem; flex-wrap:wrap; }
.filters label { font-size:.75rem; text-transform:uppercase; letter-spacing:.5px; font-weight:700; color: var(--primary-dark); margin-right:.3rem; }
.filters select, .filters button { height:42px; border:1px solid var(--border); background:var(--input); border-radius:14px; padding:0 .8rem; font-family:inherit; font-weight:600; font-size:.8rem; letter-spacing:.5px; cursor:pointer; box-shadow:0 2px 6px rgba(0,0,0,.05); }
.filters button { background:#ede7ff; color:var(--primary-dark); }
.filters button:hover { background: var(--primary); color:#fff; }
.search-wrap { flex:1; min-width:240px; position:relative; display:flex; gap:.6rem; }
.search-wrap input { flex:1; height:48px; border:1px solid var(--border); border-radius:16px; padding:0 1rem; background: var(--card); font-size:.95rem; font-weight:500; }
.search-btn { height:48px; border:none; background: var(--primary); color:#fff; padding:0 1.2rem; border-radius:16px; font-weight:700; cursor:pointer; display:flex; align-items:center; gap:.4rem; box-shadow:0 4px 12px rgba(130,87,229,.45); }
.search-btn.icon-btn { width:48px; justify-content:center; padding:0; }
.search-btn:hover { background: var(--primary-dark); }
.new-post-btn { display:flex;align-items:center;justify-content:center; width:48px; height:48px; background:#9B5DE5; color:#fff; border-radius:16px; font-size:1.55rem; font-weight:600; text-decoration:none; box-shadow:0 4px 14px rgba(155,93,229,.4); line-height:0; }
.new-post-btn:hover { filter:brightness(1.08); }
@media (max-width: 980px){ .new-post-btn { display:none !important; } }
.new-post-btn svg, .search-btn svg { display:block; }
.autocomplete { position:absolute; left:0; right:0; top:100%; margin-top:4px; background:var(--card); border:1px solid var(--border); border-radius:14px; max-height:240px; overflow-y:auto; box-shadow:0 10px 30px rgba(0,0,0,.12); padding:.4rem; display:none; }
.autocomplete .item { padding:.55rem .7rem .5rem; border-radius:10px; display:flex; align-items:center; gap:.6rem; font-size:.8rem; font-weight:600; cursor:pointer; color:var(--text); }
.autocomplete .item .tag { color: var(--primary-dark); }
.autocomplete .item .type { margin-left:auto; font-size:.65rem; text-transform:uppercase; letter-spacing:.5px; opacity:.55; }
.autocomplete .item.active, .autocomplete .item:hover { background:#9B5DE5; color:#fff; }
.autocomplete .item.active .tag, .autocomplete .item:hover .tag { color:#fff; }
.mention-suggest { z-index:30; }
article.post { position:relative; }
.post-menu-btn { border:none; background:#f1edff; color:var(--primary-dark); width:34px; height:34px; border-radius:10px; cursor:pointer; font-weight:700; box-shadow:0 4px 10px rgba(130,87,229,.25); }
.post-menu-btn:hover { background: var(--primary); color:#fff; }
.seguir-btn { background:#fff; border:1px solid var(--primary-dark); color:var(--primary-dark); padding:.38rem .9rem; font-size:.7rem; font-weight:700; border-radius:40px; letter-spacing:.5px; cursor:pointer; box-shadow:0 2px 6px rgba(0,0,0,.08); }
.seguir-btn.seguindo { background: var(--primary); color:#fff; }
.seguir-btn:hover { filter:brightness(1.05); }
.likes-line strong { font-weight:800; }
.comment .mention, .post-content .mention { font-weight:700; }
body.dark .autocomplete { background:#1e293b; border-color:#334155; }
body.dark .autocomplete .item { color:#e2e8f0; }
body.dark .autocomplete .item.active, body.dark .autocomplete .item:hover { background: var(--primary); }
section#new-post h2 { text-align:center; color:#9B5DE5; font-family:'Nunito'; font-size:2.1rem; font-weight:800; letter-spacing:.6px; margin:.3rem 0 1.2rem; text-shadow:0 2px 4px rgba(0,0,0,0.18); }
section#new-post label { display:block; margin-bottom:.6rem; font-weight:600; font-size:1rem; color: var(--primary-dark); }
section#new-post textarea { width:100%; min-height:90px; padding:1rem; font-size:1rem; border-radius:16px; border:1px solid var(--border); resize:vertical; box-shadow: inset 0 1px 3px rgba(0,0,0,0.06); transition: border-color .2s; background: var(--input); color: var(--text); }
section#new-post textarea:focus { border-color: var(--primary); outline:none; }
section#new-post button { margin-top:1rem; padding:.6rem 1.6rem; background: var(--primary); color:#fff; border:none; border-radius:50px; font-weight:600; font-size:.95rem; cursor:pointer; box-shadow: 0 5px 15px rgba(130,87,229,0.35); transition: background-color .2s, box-shadow .2s; }
section#new-post button:hover, section#new-post button:focus { background: var(--primary-dark); box-shadow: 0 8px 25px rgba(111,72,201,0.7); outline:none; }
.ta-wrap { position: relative; }
/* Reuso do estilo .autocomplete para menções no editor */
.mention-suggest { position:absolute; left: 10px; bottom: -4px; transform: translateY(100%); right: 10px; }
section#feed h2 { font-weight:800; font-size:2.2rem; margin:0 0 1.2rem; color:#9B5DE5; font-family:'Nunito'; letter-spacing:.6px; text-align:center; text-shadow:0 2px 4px rgba(0,0,0,0.18); line-height:1.15; }
.card-block form label, .card-block form textarea, .card-block form button { font-family:'Nunito'; }
body, p, input, textarea, select, button, .post-content, .comment, .likes-line { font-family:'Nunito'; }
section#feed article.post { background: var(--card); border:1px solid var(--border); padding:1.5rem 2rem; border-radius:20px; margin-bottom:2rem; box-shadow: 0 10px 20px rgba(155,93,229,0.10); transition: box-shadow .2s; }
section#feed article.post:hover { box-shadow: 0 14px 26px rgba(155,93,229,0.25); }
.post-header { display:flex; align-items:center; gap:1rem; margin-bottom:1rem; }
.post-user { font-weight:600; font-size:1.05rem; color: var(--primary); }
.post-date { font-size:.9rem; color: var(--text-secondary); margin-left:auto; font-weight:600; font-style: italic; }
/* Reduzir data/hora no mobile */
@media (max-width: 980px){
.post-username span { font-size:.7rem !important; }
}
.post-content { font-size:1.05rem; margin-bottom:1rem; line-height:1.5; color: var(--text); }
/* Rich text formatting in posts */
.post-content h1, .post-content h2, .post-content h3 { font-weight:800; color:#9B5DE5; margin:.8rem 0 .5rem; }
.post-content h1 { font-size:1.5rem; }
.post-content h2 { font-size:1.3rem; }
.post-content h3 { font-size:1.15rem; }
.post-content strong { font-weight:800; color:#9B5DE5; }
.post-content em { font-style:italic; }
.post-content u { text-decoration:underline; }
.post-content ul, .post-content ol { margin:.5rem 0 .5rem 1.5rem; padding:0; }
.post-content li { margin:.3rem 0; }
.post-content a:not(.mention):not(.hashtag) { color:#9B5DE5; text-decoration:underline; }
.post-content p { margin:.5rem 0; }
.post-media img { width:100%; display:block; border-radius:24px; margin:.6rem 0 1.1rem; object-fit:contain; background:#f3f4f6; max-height:380px; cursor:pointer; }
.post-media { position:relative; overflow:hidden; }
.post-media.multi { display:grid; gap:8px; margin:.6rem 0 1.1rem; }
.post-media.multi.grid-2 { grid-template-columns:repeat(2,1fr); }
.post-media.multi.grid-3 { grid-template-columns:repeat(3,1fr); }
.post-media.multi.grid-4 { grid-template-columns:repeat(2,1fr); }
.post-media.multi .pm-item img { margin:0; height:180px; border-radius:16px; object-fit:contain; background:#f3f4f6; cursor:pointer; }
.post-actions { display:flex; gap:1.2rem; }
.post-actions button { cursor:pointer; border:none; border-radius:28px; padding:.45rem .9rem; font-weight:600; font-size:.8rem; display:flex; align-items:center; gap:.35rem; transition: background-color .2s, transform .15s; }
.post-actions button:active { transform: translateY(1px); }
.likes-list { margin-bottom:.9rem; font-size:.9rem; color: var(--text-secondary); font-weight:500; }
.like-btn { background:#ede7ff; color: var(--primary-dark); box-shadow: 0 4px 10px rgba(130,87,229,0.25); border:1px solid #d3c5ff; }
.like-btn:hover, .like-btn.liked { background: var(--primary); color:#fff; box-shadow: 0 6px 16px rgba(130,87,229,0.45); border-color: var(--primary-dark); }
body.dark .like-btn { background:#1e293b; color:#93c5fd; border:1px solid #334155; box-shadow:none; }
body.dark .like-btn:hover, body.dark .like-btn.liked { background: var(--primary); color:#fff; border-color:#60a5fa; }
.comments-list { margin-top:1rem; }
.comment-btn { background: var(--primary); color:#fff; box-shadow: 0 5px 15px rgba(130,87,229,0.6); }
.comment-btn:hover { background: var(--primary-dark); box-shadow: 0 8px 25px rgba(111,72,201,0.9); }
.comment-box { background: var(--card); border:1px solid var(--border); border-radius:16px; box-shadow: 0 2px 8px rgba(130,87,229,0.08); padding:1rem; margin:1rem 0; display:flex; flex-direction:column; gap:.7rem; }
.comment-box { position:relative; }
.comment-box .comment-input { border-radius:12px; border:1px solid var(--border); padding:.7rem 1rem; font-size:.95rem; outline:none; transition: border-color .2s; background: var(--input); color: var(--text); }
.comment-box .comment-input:focus { border-color: var(--primary); }
.comment-box button { border-radius:50px; background: var(--primary); color:#fff; border:none; padding:.5rem 1.2rem; font-weight:600; cursor:pointer; align-self:flex-end; transition: background .2s; font-size:.85rem; letter-spacing:.3px; }
.comment-box button:hover { background: var(--primary-dark); }
/* Comentários recolhíveis e estilo */
.comments-toggle-line { margin-top:1rem; }
.toggle-comments-btn { background:#f1edff; color:var(--primary-dark); border:1px solid #d8ccff; padding:.45rem 1rem; font-size:.7rem; font-weight:700; border-radius:40px; cursor:pointer; letter-spacing:.5px; box-shadow:0 2px 6px rgba(0,0,0,.06); }
.toggle-comments-btn:hover { background:var(--primary); color:#fff; border-color:var(--primary); }
body.dark .toggle-comments-btn { background:#1e293b; border-color:#334155; color:#cbd5e1; }
body.dark .toggle-comments-btn:hover { background:var(--primary); color:#fff; }
.comments-list { margin-top:.8rem; display:none; }
.comment { background:rgba(0,0,0,0.03); padding:.55rem .75rem .6rem; border-radius:14px; font-size:.78rem; line-height:1.35; font-weight:500; color:var(--text); margin-bottom:.5rem; position:relative; }
body.dark .comment { background:#243044; color:#e2e8f0; }
.comment .c-meta { display:flex; align-items:center; gap:.4rem; margin-bottom:.2rem; font-size:.65rem; letter-spacing:.5px; text-transform:uppercase; font-weight:700; color:var(--primary-dark); }
body.dark .comment .c-meta { color:#c7b7f5; }
.comment .c-time { font-weight:600; color:#64748b; font-size:.6rem; letter-spacing:.5px; }
body.dark .comment .c-time { color:#94a3b8; }
.comment .c-body { font-size:.78rem; font-weight:500; }
/* Footer removido conforme solicitado */
/* Skeleton Loader */
.feed-skeleton { background: var(--card); border:1px solid var(--border); padding:1.5rem 2rem; border-radius:20px; margin-bottom:2rem; position:relative; overflow:hidden; }
.skeleton-line, .skeleton-avatar, .skeleton-img { position:relative; background:#e7e9f2; border-radius:8px; overflow:hidden; }
body.dark .skeleton-line, body.dark .skeleton-avatar, body.dark .skeleton-img { background:#334155; }
.skeleton-avatar { width:40px; height:40px; border-radius:50%; }
.skeleton-line { height:12px; margin:6px 0; }
.skeleton-img { height:180px; border-radius:24px; margin:14px 0 8px; }
.shimmer { position:absolute; inset:0; background:linear-gradient(110deg, transparent 0%, rgba(255,255,255,.55) 45%, transparent 90%); animation:shimmer 1.4s linear infinite; mix-blend-mode:overlay; }
@keyframes shimmer { from { transform:translateX(-100%);} to { transform:translateX(100%);} }
@media (max-width:600px) {
header, main { padding:1rem; }
nav a { margin-left:1rem; font-size:.95rem; }
.feed-controls { flex-direction: column; align-items: stretch; padding: 0 1rem; }
.filters { order: 2; flex-wrap: wrap; justify-content:center; }
}
/* Responsivo: evitar barra horizontal e espaço lateral vazio em telas menores */
@media (max-width: 1200px){
main.site-main{ padding:0 24px; gap:40px; }
}
@media (max-width: 980px){
main.site-main{ padding:0 18px; gap:28px; }
/* Ocultar sidebar lateral em mobile - não mover para baixo */
.right-col{ display:none !important; }
.feed-col{ max-width:100% !important; flex:1 1 auto !important; margin:0 auto; }
}
@media (max-width: 860px){
main.site-main{ flex-direction:column; align-items:stretch; gap:22px; padding:0 16px; }
.feed-col{ max-width:100% !important; flex:1 1 auto !important; }
}
@media (max-width: 420px){
main.site-main{ padding:0 12px; }
}
/* Barra de navegação inferior para mobile (tipo app de rede social) */
.mobile-bottom-nav {
display: none;
position: fixed;
bottom: 12px;
left: 12px;
right: 12px;
background: #9B5DE5;
border-radius: 24px;
padding: 10px 8px calc(10px + env(safe-area-inset-bottom));
box-shadow: 0 4px 20px rgba(155, 93, 229, 0.4);
z-index: 1000;
}
@media (max-width: 980px){
.mobile-bottom-nav {
display: flex;
justify-content: space-around;
align-items: center;
}
/* Ocultar o cabeçalho em mobile */
header.site-head {
display: none !important;
}
/* Mostrar card de ações rápidas no mobile */
#mobile-actions-card {
display: block !important;
padding: 1rem 1.2rem .9rem !important; /* Card com mais padding */
margin: 0 -1rem 1.4rem !important; /* Aumentar largura - mesma margem dos posts */
}
/* Botões do card de ações - mais quadrados e maiores */
#mobile-actions-card .search-btn.icon-btn {
width: 52px !important;
height: 52px !important;
}
#mobile-actions-card .search-btn.icon-btn svg {
width: 24px !important;
height: 24px !important;
}
/* Adicionar padding no main (não no body) para compensar a barra inferior flutuante */
main.site-main {
margin-bottom: calc(80px + env(safe-area-inset-bottom)) !important;
}
/* Garantir que o footer não sobreponha a barra inferior */
.footer-bar {
margin-bottom: calc(80px + env(safe-area-inset-bottom));
}
/* Barra de busca com mesma largura dos cards de post no mobile */
.feed-controls {
margin: 1.2rem -1rem 2rem !important; /* Mesma largura dos posts */
padding: 0 1rem !important; /* Padding interno para compensar */
}
/* Cards de posts mais largos no mobile (igual educação) - ENLARGUECER */
#feed-list article.post {
padding: 1.5rem 1.2rem 1.3rem !important; /* Reduzir padding interno */
margin: 0 -1rem 2.2rem !important; /* Aumentar largura - card quase encostando nas bordas */
}
/* Aumentar conteúdo do card no mobile */
.post-content {
font-size: 1.15rem !important;
line-height: 1.6 !important;
}
/* Botões de ação MAIORES no mobile (não menores) */
.post-actions button {
padding: .5rem .95rem !important;
font-size: .85rem !important;
gap: .4rem !important;
}
.post-menu-btn {
width: 34px !important;
height: 34px !important;
font-size: 1rem !important;
}
/* Post header - aumentar tamanho do username */
.post-user {
font-size: 1.1rem !important;
}
}
.mobile-bottom-nav a,
.mobile-bottom-nav button {
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
.mobile-bottom-nav a:active,
.mobile-bottom-nav button:active {
transform: scale(0.95);
}
.mobile-bottom-nav a svg,
.mobile-bottom-nav button svg {
color: #ffffff;
transition: opacity 0.2s;
}
.mobile-bottom-nav a:hover,
.mobile-bottom-nav button:hover {
opacity: 0.85;
}
.mobile-bottom-nav a:hover svg,
.mobile-bottom-nav button:hover svg {
opacity: 0.85;
}
.mobile-bottom-nav .nav-badge {
position: absolute;
top: -2px;
right: -2px;
background: #ff9800;
color: #fff;
font-size: 0.6rem;
padding: 2px 5px;
border-radius: 10px;
font-weight: 700;
min-width: 18px;
text-align: center;
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
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
            <span>Educação</span>
        </a>
        <a href="/novo-post" style="background: var(--primary); color: white; border-radius: 50%; width: 48px; height: 48px; margin: -10px 0; padding: 0; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border: 3px solid #ffffff;">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
        </a>
        <div style="color: rgba(255,255,255,0.6);">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            <span>Em breve</span>
        </div>
        <a href="/login">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
            </svg>
            <span>Perfil</span>
        </a>
    </nav>"""

def page_footer():
    return f"""
    <div class="footer-text">© 2025 Gramátike • Língua Viva e de Todes</div>
    {mobile_nav()}
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
{page_footer()}"""

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
        <div class="search-box">
            <input type="text" id="search-input" placeholder="Pesquisar..." onkeydown="if(event.key==='Enter')executarBusca()">
            <button class="search-btn" onclick="executarBusca()">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
                    <circle cx="11" cy="11" r="7"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
            </button>
            <a href="/novo-post" class="btn btn-primary" style="white-space:nowrap;">+ Novo Post</a>
        </div>
        
        <div class="layout">
            <div id="feed-list">
                {posts_html}
            </div>
            <aside class="side-col">
                <div style="display:flex;gap:0.8rem;margin:0 0 1.2rem;">
                    <a href="/educacao" class="quick-nav-btn">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                        </svg>
                        Educação
                    </a>
                    <div class="quick-nav-disabled">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                        Em breve
                    </div>
                </div>
                <div class="side-card">
                    <div style="text-align:center;margin-bottom:0.8rem;">
                        <span style="font-size:1.1rem;font-weight:800;color:var(--primary);letter-spacing:0.3px;">👤 @{user_username}</span>
                    </div>
                    <div style="display:flex;flex-direction:column;gap:0.5rem;margin-bottom:0.8rem;">
                        <a href="/perfil" class="profile-link">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                <circle cx="12" cy="7" r="4"></circle>
                            </svg>
                            Meu Perfil
                        </a>
                        <a href="/configuracoes" class="profile-link">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="3"></circle>
                                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                            </svg>
                            Configurações
                        </a>
                    </div>
                    <div style="height:1px;background:var(--border);margin:0.6rem 0 0.8rem;border-radius:1px;"></div>
                    <h3 style="margin:0 0 0.8rem;font-size:1rem;font-weight:800;letter-spacing:0.5px;color:var(--primary);text-align:center;">Amigues</h3>
                    <p style="font-size:0.7rem;opacity:0.7;line-height:1.3;text-align:center;">Sem amigues ainda. Faça amizades para aparecerem aqui.</p>
                </div>
                <div class="side-card">
                    <h3>📣 Novidades</h3>
                    {divulgacoes_html}
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
    </script>
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
{page_footer()}"""

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
{page_footer()}"""
        except Exception as e:
            return self._not_found_page(f'/u/{username}')

    async def _novo_post_page(self, db, current_user, request, method):
        """Página para criar novo post."""
        if not current_user:
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
                        post_id = await create_post(db, current_user['id'], conteudo, None)
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
{page_footer()}"""

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
{page_footer()}"""

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
{page_footer()}"""

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
