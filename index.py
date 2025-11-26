# index.py
# Cloudflare Workers Python entry point
# Uses native WorkerEntrypoint pattern
# Docs: https://developers.cloudflare.com/workers/languages/python/
#
# Este arquivo serve as páginas HTML com a mesma estética da aplicação Flask original.
# Todas as páginas são renderizadas com o visual idêntico ao Gramátike.

import json
from urllib.parse import urlparse
from workers import WorkerEntrypoint, Response


def json_response(data, status=200):
    """Create a JSON response."""
    return Response(
        json.dumps(data, ensure_ascii=False),
        status=status,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )


def html_response(content, status=200):
    """Create an HTML response."""
    return Response(
        content,
        status=status,
        headers={"Content-Type": "text/html; charset=utf-8"}
    )


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
    """Cloudflare Worker entry point."""

    async def fetch(self, request):
        """Handle incoming HTTP requests."""
        url = request.url
        path = "/"
        if url:
            parsed = urlparse(url)
            path = parsed.path or "/"

        # Route handling
        routes = {
            "/": self._index_page,
            "": self._index_page,
            "/educacao": self._educacao_page,
            "/login": self._login_page,
            "/cadastro": self._cadastro_page,
            "/dinamicas": self._dinamicas_page,
            "/exercicios": self._exercicios_page,
            "/artigos": self._artigos_page,
            "/apostilas": self._apostilas_page,
            "/podcasts": self._podcasts_page,
            "/api/health": lambda: json_response({"status": "ok", "platform": "Cloudflare Workers"}),
            "/api/info": lambda: json_response({"name": "Gramátike", "version": "1.0.0"}),
        }

        handler = routes.get(path)
        if handler:
            result = handler()
            if isinstance(result, Response):
                return result
            return html_response(result)
        
        return html_response(self._not_found_page(path), status=404)

    def _index_page(self):
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

    def _educacao_page(self):
        """Página Educação - Hub educacional."""
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
                <div class="empty">Nada encontrado.</div>
            </div>
            <aside class="side-col">
                <div class="quick-nav">
                    <a href="/dinamicas">🎮 Dinâmicas</a>
                    <a href="/">💬 Gramátike</a>
                </div>
                <div class="side-card">
                    <h3>💡 Palavras do Dia</h3>
                    <div class="placeholder">Nenhuma palavra disponível</div>
                </div>
                <div class="side-card">
                    <h3>📣 Novidades</h3>
                    <div class="placeholder">Nenhuma divulgação ativa.</div>
                </div>
            </aside>
        </div>
    </main>
{page_footer()}"""

    def _login_page(self):
        """Página de Login."""
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
            <h2>Entrar</h2>
            <form>
                <div class="form-group">
                    <label>Usuárie / Email</label>
                    <input type="text" placeholder="Usuárie ou email">
                </div>
                <div class="form-group">
                    <label>Senha</label>
                    <input type="password" placeholder="••••••••">
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

    def _cadastro_page(self):
        """Página de Cadastro."""
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
            <h2>Criar Conta</h2>
            <form>
                <div class="form-group">
                    <label>Nome de Usuárie</label>
                    <input type="text" placeholder="seu_usuario">
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" placeholder="seu@email.com">
                </div>
                <div class="form-group">
                    <label>Senha</label>
                    <input type="password" placeholder="••••••••">
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

    def _dinamicas_page(self):
        """Página de Dinâmicas."""
        return f"""{page_head("Dinâmicas — Gramátike Edu")}
    <header class="site-head">
        <h1 class="logo">Dinâmicas</h1>
    </header>
    <main>
        <div class="card">
            <p class="muted">Recurso em beta — disponível apenas para administradores no momento.</p>
        </div>
    </main>
{page_footer()}"""

    def _exercicios_page(self):
        """Página de Exercícios."""
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
            <input type="text" placeholder="Pesquisar título ou descrição...">
            <button class="search-btn">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
                    <circle cx="11" cy="11" r="7"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
            </button>
        </div>
        <p class="empty">Nenhum exercício.</p>
    </main>
{page_footer()}"""

    def _artigos_page(self):
        """Página de Artigos."""
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
        <p class="empty">Nenhum artigo.</p>
    </main>
{page_footer()}"""

    def _apostilas_page(self):
        """Página de Apostilas."""
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
        <p class="empty">Nenhuma apostila.</p>
    </main>
{page_footer()}"""

    def _podcasts_page(self):
        """Página de Podcasts."""
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
        <p class="empty">Nenhum podcast.</p>
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
