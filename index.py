# index.py
# FastAPI entrypoint for Cloudflare Workers Python (Pyodide)
# Uses WorkerEntrypoint pattern with ASGI and Cloudflare D1 database.
#
# Migração do Flask para FastAPI para compatibilidade com Cloudflare Workers.
# Docs: https://developers.cloudflare.com/workers/languages/python/

import os
import json
import hashlib
import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple

from fastapi import FastAPI, Request, Form, Depends, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from workers import WorkerEntrypoint

# Setup logging
logger = logging.getLogger(__name__)

# ============================================================================
# FastAPI App Setup
# ============================================================================

app = FastAPI(
    title="Gramátike",
    description="Plataforma educacional de gramática portuguesa",
    version="1.0.0"
)

# Jinja2 setup - templates are in gramatike_app/templates
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "gramatike_app", "templates")
STATIC_DIR = os.path.join(SCRIPT_DIR, "gramatike_app", "static")

jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(['html', 'xml']),
    enable_async=True
)

# NOTE: In-memory session store - not persistent across Worker invocations.
# For production, migrate to Cloudflare KV or D1 for session storage.
# Format: {session_id: {"user_id": int, "username": str, "expires": datetime}}
sessions = {}

# Flash messages storage (per-session)
# Format: {session_id: [(category, message), ...]}
flash_messages = {}

# Route name to URL mapping for url_for compatibility
ROUTE_MAP = {
    'main.index': '/',
    'main.login': '/login',
    'main.logout': '/logout',
    'main.cadastro': '/cadastro',
    'main.educacao': '/educacao',
    'main.perfil': '/perfil',
    'main.meu_perfil': '/perfil',
    'main.esqueci_senha': '/esqueci-senha',
    'main.exercicios': '/exercicios',
    'main.artigos': '/artigos',
    'main.apostilas': '/apostilas',
    'main.podcasts': '/podcasts',
    'main.videos': '/videos',
    'main.redacao': '/redacao',
    'main.variacoes': '/variacoes',
    'main.dinamicas_home': '/dinamicas',
    'main.dinamica_view': '/dinamica/<int:dyn_id>',
    'main.suporte': '/suporte',
    'main.configuracoes': '/configuracoes',
    'main.novo_post': '/novo_post',
    'main.post_detail': '/post/<int:post_id>',
    'main.perfil_publico': '/perfil/<username>',
    'main.novidade_detail': '/novidade/<int:novidade_id>',
    'admin.dashboard': '/admin',
    'admin.denuncias': '/admin/denuncias',
    'admin.suporte': '/admin/suporte',
    'static': '/static',
}

# ============================================================================
# Helper Functions
# ============================================================================

def url_for(endpoint: str, **kwargs) -> str:
    """Flask-compatible url_for function for templates."""
    if endpoint == 'static':
        filename = kwargs.get('filename', '')
        return f"/static/{filename}"
    
    base_url = ROUTE_MAP.get(endpoint, '/')
    
    # Handle dynamic route parameters
    if '<' in base_url or kwargs:
        for key, value in kwargs.items():
            if key != '_external':
                # Replace placeholder or append as query param
                placeholder = f"<{key}>" 
                if placeholder in base_url:
                    base_url = base_url.replace(placeholder, str(value))
                elif f"<int:{key}>" in base_url:
                    base_url = base_url.replace(f"<int:{key}>", str(value))
    
    return base_url

def flash(message: str, category: str = "info", session_id: Optional[str] = None):
    """Add a flash message (Flask-compatible)."""
    if session_id:
        if session_id not in flash_messages:
            flash_messages[session_id] = []
        flash_messages[session_id].append((category, message))

def get_flashed_messages(with_categories: bool = False, session_id: Optional[str] = None) -> List:
    """Get and clear flash messages (Flask-compatible)."""
    if not session_id or session_id not in flash_messages:
        return []
    messages = flash_messages.pop(session_id, [])
    if with_categories:
        return messages
    return [msg for _, msg in messages]

def csrf_token() -> str:
    """Generate a CSRF token (simplified for Workers)."""
    return secrets.token_urlsafe(32)

def hash_password(password: str) -> str:
    """Hash password using SHA256 with salt.
    
    NOTE: For production, use a proper password hashing library like bcrypt.
    SHA256 is used here for Pyodide compatibility where bcrypt is not available.
    A random salt is prepended to provide some protection against rainbow tables.
    """
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash with salt."""
    if ':' not in stored_hash:
        # Legacy hash without salt - simple comparison
        return hashlib.sha256(password.encode()).hexdigest() == stored_hash
    salt, hashed = stored_hash.split(':', 1)
    return hashlib.sha256((salt + password).encode()).hexdigest() == hashed

def create_session(user_id: int, username: str, is_admin: bool = False) -> str:
    """Create a new session and return session ID."""
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {
        "user_id": user_id,
        "username": username,
        "is_admin": is_admin,
        "is_authenticated": True,
        "expires": datetime.now(timezone.utc) + timedelta(days=7)
    }
    return session_id

def get_current_user(session_id: Optional[str] = Cookie(None, alias="session")) -> Optional[dict]:
    """Get current user from session cookie."""
    if not session_id or session_id not in sessions:
        return None
    session = sessions[session_id]
    if datetime.now(timezone.utc) > session["expires"]:
        del sessions[session_id]
        return None
    return session

# Simple request mock for templates
class MockRequest:
    def __init__(self):
        self.form = {}

def render_template(template_name: str, session_id: Optional[str] = None, **context) -> str:
    """Render a Jinja2 template with Flask-compatible context."""
    # Add Flask-compatible functions to context
    context['url_for'] = url_for
    context['csrf_token'] = csrf_token
    context['request'] = context.get('request', MockRequest())
    
    # Add get_flashed_messages as a callable
    def _get_flashed_messages(with_categories=False):
        return get_flashed_messages(with_categories=with_categories, session_id=session_id)
    context['get_flashed_messages'] = _get_flashed_messages
    
    template = jinja_env.get_template(template_name)
    return template.render(**context)

# ============================================================================
# Database Helper (D1)
# ============================================================================

class D1Database:
    """Wrapper for Cloudflare D1 database operations.
    
    NOTE: The global _db instance is set per-request in the Worker entry point.
    This is acceptable for Cloudflare Workers where each request runs in isolation.
    """
    
    def __init__(self, env):
        self.db = getattr(env, 'DB', None)
    
    async def execute(self, query: str, params: tuple = ()):
        """Execute a query and return results."""
        if not self.db:
            return None
        try:
            result = await self.db.prepare(query).bind(*params).all()
            return result.results if hasattr(result, 'results') else result
        except Exception as e:
            logger.error(f"D1 execute error: {e}")
            return None
    
    async def run(self, query: str, params: tuple = ()):
        """Execute a write query."""
        if not self.db:
            return None
        try:
            return await self.db.prepare(query).bind(*params).run()
        except Exception as e:
            logger.error(f"D1 run error: {e}")
            return None

# Global database instance (set per-request in Worker)
_db: Optional[D1Database] = None

# ============================================================================
# Routes
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, session: Optional[str] = Cookie(None)):
    """Home page - requires login."""
    user = get_current_user(session)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    html = render_template("index.html", 
        session_id=session,
        admin=user.get('is_admin', False),
        current_user=user,
        div_edu=[],
        delu_trending=[],
        delu_commented=[]
    )
    return HTMLResponse(content=html)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, session: Optional[str] = Cookie(None)):
    """Login page."""
    user = get_current_user(session)
    if user:
        return RedirectResponse(url="/", status_code=302)
    
    html = render_template("login.html", session_id=session)
    return HTMLResponse(content=html)


@app.post("/login")
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """Handle login form submission."""
    global _db
    
    if not _db:
        # Fallback: demo user for testing without D1
        if email == "demo@gramatike.com" and password == "demo123":
            session_id = create_session(1, "demo", is_admin=True)
            response = RedirectResponse(url="/", status_code=302)
            response.set_cookie(key="session", value=session_id, httponly=True, secure=True, samesite="lax", max_age=604800)
            return response
        return RedirectResponse(url="/login?error=invalid", status_code=302)
    
    # Query user from D1
    users = await _db.execute(
        "SELECT id, username, password, is_admin FROM user WHERE email = ? OR username = ?",
        (email, email)
    )
    
    if not users or len(users) == 0:
        return RedirectResponse(url="/login?error=invalid", status_code=302)
    
    user = users[0]
    if not verify_password(password, user['password']):
        return RedirectResponse(url="/login?error=invalid", status_code=302)
    
    # Create session
    session_id = create_session(user['id'], user['username'], is_admin=user.get('is_admin', False))
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="session", value=session_id, httponly=True, secure=True, samesite="lax", max_age=604800)
    return response


@app.get("/logout")
async def logout(session: Optional[str] = Cookie(None)):
    """Logout and clear session."""
    if session and session in sessions:
        del sessions[session]
    if session and session in flash_messages:
        del flash_messages[session]
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="session")
    return response


@app.get("/cadastro", response_class=HTMLResponse)
async def cadastro_page(session: Optional[str] = Cookie(None)):
    """Registration page."""
    html = render_template("cadastro.html", session_id=session)
    return HTMLResponse(content=html)


@app.post("/cadastro")
async def cadastro_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    genero: str = Form(""),
    pronome: str = Form(""),
    data_nascimento: str = Form("")
):
    """Handle registration form submission."""
    global _db
    
    if not _db:
        return RedirectResponse(url="/cadastro?error=db", status_code=302)
    
    # Check if user exists
    existing = await _db.execute(
        "SELECT id FROM user WHERE email = ? OR username = ?",
        (email, username)
    )
    if existing and len(existing) > 0:
        return RedirectResponse(url="/cadastro?error=exists", status_code=302)
    
    # Create user
    hashed = hash_password(password)
    await _db.run(
        """INSERT INTO user (username, email, password, genero, pronome, created_at) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (username, email, hashed, genero, pronome, datetime.now(timezone.utc).isoformat())
    )
    
    return RedirectResponse(url="/login?success=registered", status_code=302)


@app.get("/educacao", response_class=HTMLResponse)
async def educacao(session: Optional[str] = Cookie(None)):
    """Education hub page."""
    user = get_current_user(session)
    html = render_template("gramatike_edu.html",
        session_id=session,
        current_user=user,
        generated_at=datetime.now(timezone.utc),
        novidades=[],
        divulgacoes=[]
    )
    return HTMLResponse(content=html)


@app.get("/perfil", response_class=HTMLResponse)
async def meu_perfil(session: Optional[str] = Cookie(None)):
    """User profile page."""
    user = get_current_user(session)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    html = render_template("meu_perfil.html", session_id=session, usuario=user, current_user=user)
    return HTMLResponse(content=html)


@app.get("/esqueci-senha", response_class=HTMLResponse)
async def esqueci_senha(session: Optional[str] = Cookie(None)):
    """Password recovery page."""
    html = render_template("esqueci_senha.html", session_id=session)
    return HTMLResponse(content=html)


@app.get("/configuracoes", response_class=HTMLResponse)
async def configuracoes(session: Optional[str] = Cookie(None)):
    """User settings page."""
    user = get_current_user(session)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    html = render_template("configuracoes.html", session_id=session, user=user, current_user=user)
    return HTMLResponse(content=html)


@app.get("/suporte", response_class=HTMLResponse)
async def suporte(session: Optional[str] = Cookie(None)):
    """Support page."""
    user = get_current_user(session)
    html = render_template("suporte.html", session_id=session, current_user=user)
    return HTMLResponse(content=html)


@app.get("/novo_post", response_class=HTMLResponse)
async def novo_post(session: Optional[str] = Cookie(None)):
    """Create new post page."""
    user = get_current_user(session)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    html = render_template("criar_post.html", session_id=session, current_user=user)
    return HTMLResponse(content=html)


@app.post("/novo_post")
async def criar_post_submit(
    request: Request,
    conteudo: str = Form(...),
    session: Optional[str] = Cookie(None)
):
    """Handle new post submission."""
    global _db
    user = get_current_user(session)
    
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    if not _db:
        flash("Erro de banco de dados", "error", session)
        return RedirectResponse(url="/", status_code=302)
    
    # Create post
    await _db.run(
        """INSERT INTO post (usuario, usuario_id, conteudo, data, is_deleted) 
           VALUES (?, ?, ?, ?, 0)""",
        (user['username'], user['user_id'], conteudo, datetime.now(timezone.utc).isoformat())
    )
    
    flash("Post publicado com sucesso!", "success", session)
    return RedirectResponse(url="/", status_code=302)


@app.get("/post/{post_id}", response_class=HTMLResponse)
async def view_post(post_id: int, session: Optional[str] = Cookie(None)):
    """View a single post with comments."""
    global _db
    user = get_current_user(session)
    
    if not _db:
        return HTMLResponse(content="<h1>Database not available</h1>", status_code=500)
    
    # Get post
    posts = await _db.execute(
        """SELECT p.*, u.foto_perfil, u.username as author_username
           FROM post p
           LEFT JOIN user u ON p.usuario_id = u.id
           WHERE p.id = ? AND (p.is_deleted = 0 OR p.is_deleted IS NULL)""",
        (post_id,)
    )
    
    if not posts or len(posts) == 0:
        return HTMLResponse(content="<h1>Post não encontrado</h1>", status_code=404)
    
    post = posts[0]
    
    # Get comments
    comments = await _db.execute(
        """SELECT c.*, u.username, u.foto_perfil
           FROM comentario c
           LEFT JOIN user u ON c.usuario_id = u.id
           WHERE c.post_id = ?
           ORDER BY c.data ASC""",
        (post_id,)
    )
    
    # Check if user liked this post
    liked = False
    if user:
        likes = await _db.execute(
            "SELECT 1 FROM post_likes WHERE user_id = ? AND post_id = ?",
            (user['user_id'], post_id)
        )
        liked = likes and len(likes) > 0
    
    # Get like count
    like_count_result = await _db.execute(
        "SELECT COUNT(*) as count FROM post_likes WHERE post_id = ?",
        (post_id,)
    )
    like_count = like_count_result[0]['count'] if like_count_result else 0
    
    html = render_template("post_detail.html",
        session_id=session,
        current_user=user,
        post=post,
        comments=comments or [],
        liked=liked,
        like_count=like_count
    )
    return HTMLResponse(content=html)


@app.post("/post/{post_id}/comment")
async def add_comment(
    post_id: int,
    conteudo: str = Form(...),
    session: Optional[str] = Cookie(None)
):
    """Add a comment to a post."""
    global _db
    user = get_current_user(session)
    
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    if not _db:
        return RedirectResponse(url=f"/post/{post_id}", status_code=302)
    
    await _db.run(
        """INSERT INTO comentario (usuario_id, conteudo, post_id, data) 
           VALUES (?, ?, ?, ?)""",
        (user['user_id'], conteudo, post_id, datetime.now(timezone.utc).isoformat())
    )
    
    return RedirectResponse(url=f"/post/{post_id}", status_code=302)


@app.post("/post/{post_id}/delete")
async def delete_post(post_id: int, session: Optional[str] = Cookie(None)):
    """Delete a post (soft delete)."""
    global _db
    user = get_current_user(session)
    
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    if not _db:
        return RedirectResponse(url="/", status_code=302)
    
    # Check if user owns the post or is admin
    posts = await _db.execute(
        "SELECT usuario_id FROM post WHERE id = ?",
        (post_id,)
    )
    
    if not posts or len(posts) == 0:
        return RedirectResponse(url="/", status_code=302)
    
    post = posts[0]
    if post['usuario_id'] != user['user_id'] and not user.get('is_admin', False):
        flash("Você não tem permissão para excluir este post", "error", session)
        return RedirectResponse(url="/", status_code=302)
    
    # Soft delete
    await _db.run(
        "UPDATE post SET is_deleted = 1, deleted_at = ?, deleted_by = ? WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), user['user_id'], post_id)
    )
    
    flash("Post excluído com sucesso", "success", session)
    return RedirectResponse(url="/", status_code=302)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "framework": "FastAPI", "platform": "Cloudflare Workers Python"}


@app.get("/api/info")
async def info():
    """Application information."""
    return {
        "name": "Gramátike",
        "framework": "FastAPI",
        "platform": "Cloudflare Workers Python (Pyodide)",
        "database": "Cloudflare D1",
        "description": "Plataforma educacional de gramática portuguesa"
    }


@app.get("/api/posts")
async def get_posts(session: Optional[str] = Cookie(None)):
    """Get posts for feed."""
    global _db
    user = get_current_user(session)
    
    if not _db:
        return {"posts": [], "error": "Database not available"}
    
    posts = await _db.execute(
        """SELECT p.id, p.usuario, p.usuario_id, p.conteudo, p.imagem, p.data, u.foto_perfil
           FROM post p
           LEFT JOIN user u ON p.usuario_id = u.id
           WHERE p.is_deleted = 0 OR p.is_deleted IS NULL
           ORDER BY p.data DESC
           LIMIT 50"""
    )
    
    result = []
    for p in (posts or []):
        # Check if user liked this post
        liked = False
        if user and _db:
            likes = await _db.execute(
                "SELECT 1 FROM post_likes WHERE user_id = ? AND post_id = ?",
                (user['user_id'], p.get('id'))
            )
            liked = likes and len(likes) > 0
        
        # Get like count
        like_count = 0
        if _db:
            like_result = await _db.execute(
                "SELECT COUNT(*) as count FROM post_likes WHERE post_id = ?",
                (p.get('id'),)
            )
            like_count = like_result[0]['count'] if like_result else 0
        
        # Get comment count
        comment_count = 0
        if _db:
            comment_result = await _db.execute(
                "SELECT COUNT(*) as count FROM comentario WHERE post_id = ?",
                (p.get('id'),)
            )
            comment_count = comment_result[0]['count'] if comment_result else 0
        
        result.append({
            "id": p.get("id"),
            "usuario": p.get("usuario", "Usuárie"),
            "usuario_id": p.get("usuario_id"),
            "conteudo": p.get("conteudo", ""),
            "imagem": p.get("imagem", ""),
            "data": p.get("data", ""),
            "foto_perfil": p.get("foto_perfil", "img/perfil.png"),
            "liked": liked,
            "like_count": like_count,
            "comment_count": comment_count
        })
    
    return {"posts": result}


@app.post("/api/posts/{post_id}/like")
async def like_post(post_id: int, session: Optional[str] = Cookie(None)):
    """Like or unlike a post."""
    global _db
    user = get_current_user(session)
    
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    
    if not _db:
        return JSONResponse({"error": "Database not available"}, status_code=500)
    
    # Check if already liked
    existing = await _db.execute(
        "SELECT 1 FROM post_likes WHERE user_id = ? AND post_id = ?",
        (user['user_id'], post_id)
    )
    
    if existing and len(existing) > 0:
        # Unlike
        await _db.run(
            "DELETE FROM post_likes WHERE user_id = ? AND post_id = ?",
            (user['user_id'], post_id)
        )
        liked = False
    else:
        # Like
        await _db.run(
            "INSERT INTO post_likes (user_id, post_id) VALUES (?, ?)",
            (user['user_id'], post_id)
        )
        liked = True
    
    # Get new count
    count_result = await _db.execute(
        "SELECT COUNT(*) as count FROM post_likes WHERE post_id = ?",
        (post_id,)
    )
    count = count_result[0]['count'] if count_result else 0
    
    return {"liked": liked, "count": count}


@app.get("/api/posts/{post_id}/comments")
async def get_comments(post_id: int, session: Optional[str] = Cookie(None)):
    """Get comments for a post."""
    global _db
    
    if not _db:
        return {"comments": [], "error": "Database not available"}
    
    comments = await _db.execute(
        """SELECT c.id, c.conteudo, c.data, u.username, u.foto_perfil
           FROM comentario c
           LEFT JOIN user u ON c.usuario_id = u.id
           WHERE c.post_id = ?
           ORDER BY c.data ASC""",
        (post_id,)
    )
    
    result = []
    for c in (comments or []):
        result.append({
            "id": c.get("id"),
            "conteudo": c.get("conteudo", ""),
            "data": c.get("data", ""),
            "username": c.get("username", "Usuárie"),
            "foto_perfil": c.get("foto_perfil", "img/perfil.png")
        })
    
    return {"comments": result}


@app.post("/api/posts/{post_id}/comments")
async def create_comment_api(
    post_id: int,
    request: Request,
    session: Optional[str] = Cookie(None)
):
    """Create a comment via API."""
    global _db
    user = get_current_user(session)
    
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    
    if not _db:
        return JSONResponse({"error": "Database not available"}, status_code=500)
    
    body = await request.json()
    conteudo = body.get("conteudo", "").strip()
    
    if not conteudo:
        return JSONResponse({"error": "Comment content required"}, status_code=400)
    
    await _db.run(
        """INSERT INTO comentario (usuario_id, conteudo, post_id, data) 
           VALUES (?, ?, ?, ?)""",
        (user['user_id'], conteudo, post_id, datetime.now(timezone.utc).isoformat())
    )
    
    return {"success": True, "message": "Comment created"}


@app.post("/api/posts")
async def create_post_api(request: Request, session: Optional[str] = Cookie(None)):
    """Create a post via API."""
    global _db
    user = get_current_user(session)
    
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    
    if not _db:
        return JSONResponse({"error": "Database not available"}, status_code=500)
    
    body = await request.json()
    conteudo = body.get("conteudo", "").strip()
    
    if not conteudo:
        return JSONResponse({"error": "Post content required"}, status_code=400)
    
    await _db.run(
        """INSERT INTO post (usuario, usuario_id, conteudo, data, is_deleted) 
           VALUES (?, ?, ?, ?, 0)""",
        (user['username'], user['user_id'], conteudo, datetime.now(timezone.utc).isoformat())
    )
    
    return {"success": True, "message": "Post created"}


@app.delete("/api/posts/{post_id}")
async def delete_post_api(post_id: int, session: Optional[str] = Cookie(None)):
    """Delete a post via API."""
    global _db
    user = get_current_user(session)
    
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    
    if not _db:
        return JSONResponse({"error": "Database not available"}, status_code=500)
    
    # Check ownership
    posts = await _db.execute(
        "SELECT usuario_id FROM post WHERE id = ?",
        (post_id,)
    )
    
    if not posts or len(posts) == 0:
        return JSONResponse({"error": "Post not found"}, status_code=404)
    
    post = posts[0]
    if post['usuario_id'] != user['user_id'] and not user.get('is_admin', False):
        return JSONResponse({"error": "Not authorized"}, status_code=403)
    
    # Soft delete
    await _db.run(
        "UPDATE post SET is_deleted = 1, deleted_at = ?, deleted_by = ? WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), user['user_id'], post_id)
    )
    
    return {"success": True, "message": "Post deleted"}


# ============================================================================
# Phase 3: Public Profiles & Followers (Seguidories)
# ============================================================================

@app.get("/perfil/{username}", response_class=HTMLResponse)
async def perfil_publico(username: str, session: Optional[str] = Cookie(None)):
    """View a user's public profile."""
    global _db
    current_user = get_current_user(session)
    
    if not _db:
        return HTMLResponse(content="<h1>Banco de dados indisponível</h1>", status_code=500)
    
    # Get profile user
    users = await _db.execute(
        """SELECT id, username, nome, bio, foto_perfil, genero, pronome, created_at
           FROM user WHERE username = ?""",
        (username,)
    )
    
    if not users or len(users) == 0:
        return HTMLResponse(content="<h1>Usuárie não encontrade</h1>", status_code=404)
    
    profile_user = users[0]
    
    # Get follower count (seguidories)
    seguidories_result = await _db.execute(
        "SELECT COUNT(*) as count FROM seguidores WHERE seguido_id = ?",
        (profile_user['id'],)
    )
    seguidories_count = seguidories_result[0]['count'] if seguidories_result else 0
    
    # Get following count (seguindo)
    seguindo_result = await _db.execute(
        "SELECT COUNT(*) as count FROM seguidores WHERE seguidor_id = ?",
        (profile_user['id'],)
    )
    seguindo_count = seguindo_result[0]['count'] if seguindo_result else 0
    
    # Check if current user follows this profile
    is_following = False
    if current_user:
        follow_check = await _db.execute(
            "SELECT 1 FROM seguidores WHERE seguidor_id = ? AND seguido_id = ?",
            (current_user['user_id'], profile_user['id'])
        )
        is_following = follow_check and len(follow_check) > 0
    
    # Get user's posts
    posts = await _db.execute(
        """SELECT p.id, p.usuario, p.conteudo, p.imagem, p.data
           FROM post p
           WHERE p.usuario_id = ? AND (p.is_deleted = 0 OR p.is_deleted IS NULL)
           ORDER BY p.data DESC
           LIMIT 20""",
        (profile_user['id'],)
    )
    
    # Get post count
    post_count_result = await _db.execute(
        "SELECT COUNT(*) as count FROM post WHERE usuario_id = ? AND (is_deleted = 0 OR is_deleted IS NULL)",
        (profile_user['id'],)
    )
    post_count = post_count_result[0]['count'] if post_count_result else 0
    
    # Check if viewing own profile
    is_own_profile = current_user and current_user['user_id'] == profile_user['id']
    
    html = render_template("perfil.html",
        session_id=session,
        current_user=current_user,
        usuario=profile_user,
        posts=posts or [],
        seguidories_count=seguidories_count,
        seguindo_count=seguindo_count,
        post_count=post_count,
        is_following=is_following,
        is_own_profile=is_own_profile
    )
    return HTMLResponse(content=html)


@app.post("/api/users/{username}/follow")
async def toggle_follow(username: str, session: Optional[str] = Cookie(None)):
    """Follow or unfollow a user (seguir/deixar de seguir)."""
    global _db
    current_user = get_current_user(session)
    
    if not current_user:
        return JSONResponse({"error": "Não autenticade"}, status_code=401)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    # Get target user
    users = await _db.execute(
        "SELECT id FROM user WHERE username = ?",
        (username,)
    )
    
    if not users or len(users) == 0:
        return JSONResponse({"error": "Usuárie não encontrade"}, status_code=404)
    
    target_user_id = users[0]['id']
    
    # Can't follow yourself
    if target_user_id == current_user['user_id']:
        return JSONResponse({"error": "Você não pode seguir a si mesme"}, status_code=400)
    
    # Check if already following
    existing = await _db.execute(
        "SELECT 1 FROM seguidores WHERE seguidor_id = ? AND seguido_id = ?",
        (current_user['user_id'], target_user_id)
    )
    
    if existing and len(existing) > 0:
        # Unfollow
        await _db.run(
            "DELETE FROM seguidores WHERE seguidor_id = ? AND seguido_id = ?",
            (current_user['user_id'], target_user_id)
        )
        is_following = False
    else:
        # Follow
        await _db.run(
            "INSERT INTO seguidores (seguidor_id, seguido_id) VALUES (?, ?)",
            (current_user['user_id'], target_user_id)
        )
        is_following = True
    
    # Get new follower count
    count_result = await _db.execute(
        "SELECT COUNT(*) as count FROM seguidores WHERE seguido_id = ?",
        (target_user_id,)
    )
    count = count_result[0]['count'] if count_result else 0
    
    return {"is_following": is_following, "seguidories_count": count}


@app.get("/api/users/{username}/seguidories")
async def get_seguidories(username: str, session: Optional[str] = Cookie(None)):
    """Get list of followers (seguidories) for a user."""
    global _db
    
    if not _db:
        return {"seguidories": [], "error": "Banco de dados indisponível"}
    
    # Get user
    users = await _db.execute(
        "SELECT id FROM user WHERE username = ?",
        (username,)
    )
    
    if not users or len(users) == 0:
        return JSONResponse({"error": "Usuárie não encontrade"}, status_code=404)
    
    user_id = users[0]['id']
    
    # Get followers
    seguidories = await _db.execute(
        """SELECT u.id, u.username, u.nome, u.foto_perfil
           FROM seguidores s
           JOIN user u ON s.seguidor_id = u.id
           WHERE s.seguido_id = ?
           ORDER BY u.username ASC""",
        (user_id,)
    )
    
    result = []
    for s in (seguidories or []):
        result.append({
            "id": s.get("id"),
            "username": s.get("username", ""),
            "nome": s.get("nome", ""),
            "foto_perfil": s.get("foto_perfil", "img/perfil.png")
        })
    
    return {"seguidories": result}


@app.get("/api/users/{username}/seguindo")
async def get_seguindo(username: str, session: Optional[str] = Cookie(None)):
    """Get list of users that this user follows (seguindo)."""
    global _db
    
    if not _db:
        return {"seguindo": [], "error": "Banco de dados indisponível"}
    
    # Get user
    users = await _db.execute(
        "SELECT id FROM user WHERE username = ?",
        (username,)
    )
    
    if not users or len(users) == 0:
        return JSONResponse({"error": "Usuárie não encontrade"}, status_code=404)
    
    user_id = users[0]['id']
    
    # Get following
    seguindo = await _db.execute(
        """SELECT u.id, u.username, u.nome, u.foto_perfil
           FROM seguidores s
           JOIN user u ON s.seguido_id = u.id
           WHERE s.seguidor_id = ?
           ORDER BY u.username ASC""",
        (user_id,)
    )
    
    result = []
    for s in (seguindo or []):
        result.append({
            "id": s.get("id"),
            "username": s.get("username", ""),
            "nome": s.get("nome", ""),
            "foto_perfil": s.get("foto_perfil", "img/perfil.png")
        })
    
    return {"seguindo": result}


@app.get("/api/users/{username}")
async def get_user_profile(username: str, session: Optional[str] = Cookie(None)):
    """Get user profile data via API."""
    global _db
    current_user = get_current_user(session)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    # Get user
    users = await _db.execute(
        """SELECT id, username, nome, bio, foto_perfil, genero, pronome, created_at
           FROM user WHERE username = ?""",
        (username,)
    )
    
    if not users or len(users) == 0:
        return JSONResponse({"error": "Usuárie não encontrade"}, status_code=404)
    
    profile = users[0]
    
    # Get counts
    seguidories_result = await _db.execute(
        "SELECT COUNT(*) as count FROM seguidores WHERE seguido_id = ?",
        (profile['id'],)
    )
    seguidories_count = seguidories_result[0]['count'] if seguidories_result else 0
    
    seguindo_result = await _db.execute(
        "SELECT COUNT(*) as count FROM seguidores WHERE seguidor_id = ?",
        (profile['id'],)
    )
    seguindo_count = seguindo_result[0]['count'] if seguindo_result else 0
    
    post_count_result = await _db.execute(
        "SELECT COUNT(*) as count FROM post WHERE usuario_id = ? AND (is_deleted = 0 OR is_deleted IS NULL)",
        (profile['id'],)
    )
    post_count = post_count_result[0]['count'] if post_count_result else 0
    
    # Check if current user follows
    is_following = False
    if current_user:
        follow_check = await _db.execute(
            "SELECT 1 FROM seguidores WHERE seguidor_id = ? AND seguido_id = ?",
            (current_user['user_id'], profile['id'])
        )
        is_following = follow_check and len(follow_check) > 0
    
    return {
        "id": profile['id'],
        "username": profile['username'],
        "nome": profile.get('nome', ''),
        "bio": profile.get('bio', ''),
        "foto_perfil": profile.get('foto_perfil', 'img/perfil.png'),
        "genero": profile.get('genero', ''),
        "pronome": profile.get('pronome', ''),
        "created_at": profile.get('created_at', ''),
        "seguidories_count": seguidories_count,
        "seguindo_count": seguindo_count,
        "post_count": post_count,
        "is_following": is_following
    }


@app.get("/api/users/search")
async def search_users(q: str = "", session: Optional[str] = Cookie(None)):
    """Search for users by username or name."""
    global _db
    
    if not _db:
        return {"users": [], "error": "Banco de dados indisponível"}
    
    if not q or len(q) < 2:
        return {"users": [], "message": "Informe ao menos 2 caracteres"}
    
    # Search users
    users = await _db.execute(
        """SELECT id, username, nome, foto_perfil
           FROM user
           WHERE username LIKE ? OR nome LIKE ?
           ORDER BY username ASC
           LIMIT 20""",
        (f"%{q}%", f"%{q}%")
    )
    
    result = []
    for u in (users or []):
        result.append({
            "id": u.get("id"),
            "username": u.get("username", ""),
            "nome": u.get("nome", ""),
            "foto_perfil": u.get("foto_perfil", "img/perfil.png")
        })
    
    return {"users": result}


# ============================================================================
# Phase 4: Admin Panel
# ============================================================================

def require_admin(user: Optional[dict]) -> bool:
    """Check if user is admin."""
    return user and user.get('is_admin', False)


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(session: Optional[str] = Cookie(None)):
    """Admin dashboard - requires admin access."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        flash("Acesso restrito a administradories", "error", session)
        return RedirectResponse(url="/", status_code=302)
    
    if not _db:
        return HTMLResponse(content="<h1>Banco de dados indisponível</h1>", status_code=500)
    
    # Get stats
    user_count_result = await _db.execute("SELECT COUNT(*) as count FROM user")
    user_count = user_count_result[0]['count'] if user_count_result else 0
    
    post_count_result = await _db.execute(
        "SELECT COUNT(*) as count FROM post WHERE is_deleted = 0 OR is_deleted IS NULL"
    )
    post_count = post_count_result[0]['count'] if post_count_result else 0
    
    comment_count_result = await _db.execute("SELECT COUNT(*) as count FROM comentario")
    comment_count = comment_count_result[0]['count'] if comment_count_result else 0
    
    edu_count_result = await _db.execute("SELECT COUNT(*) as count FROM edu_content")
    edu_count = edu_count_result[0]['count'] if edu_count_result else 0
    
    # Get recent users
    recent_users = await _db.execute(
        """SELECT id, username, email, nome, is_admin, is_banned, created_at
           FROM user
           ORDER BY created_at DESC
           LIMIT 10"""
    )
    
    # Get pending reports
    reports = await _db.execute(
        """SELECT r.id, r.post_id, r.motivo, r.category, r.data, r.resolved,
                  u.username as reporter_username
           FROM report r
           LEFT JOIN user u ON r.usuario_id = u.id
           WHERE r.resolved = 0
           ORDER BY r.data DESC
           LIMIT 20"""
    )
    
    # Get recent edu content
    edu_latest = await _db.execute(
        """SELECT id, tipo, titulo, created_at
           FROM edu_content
           ORDER BY created_at DESC
           LIMIT 10"""
    )
    
    html = render_template("admin/dashboard.html",
        session_id=session,
        current_user=user,
        admin=True,
        user_count=user_count,
        post_count=post_count,
        comment_count=comment_count,
        edu_count=edu_count,
        usuaries=recent_users or [],
        reports=reports or [],
        edu_latest=edu_latest or [],
        now=datetime.now(timezone.utc),
        current_year=datetime.now(timezone.utc).year
    )
    return HTMLResponse(content=html)


@app.get("/api/admin/stats")
async def admin_stats(session: Optional[str] = Cookie(None)):
    """Get admin statistics."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    # Get various stats
    user_count = (await _db.execute("SELECT COUNT(*) as count FROM user"))[0]['count']
    post_count = (await _db.execute("SELECT COUNT(*) as count FROM post WHERE is_deleted = 0 OR is_deleted IS NULL"))[0]['count']
    comment_count = (await _db.execute("SELECT COUNT(*) as count FROM comentario"))[0]['count']
    edu_count = (await _db.execute("SELECT COUNT(*) as count FROM edu_content"))[0]['count']
    report_count = (await _db.execute("SELECT COUNT(*) as count FROM report WHERE resolved = 0"))[0]['count']
    
    return {
        "users": user_count,
        "posts": post_count,
        "comments": comment_count,
        "edu_content": edu_count,
        "pending_reports": report_count
    }


@app.get("/api/admin/users")
async def admin_list_users(
    page: int = 1,
    per_page: int = 20,
    session: Optional[str] = Cookie(None)
):
    """List all users for admin."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    offset = (page - 1) * per_page
    
    users = await _db.execute(
        """SELECT id, username, email, nome, is_admin, is_superadmin, is_banned, 
                  banned_at, ban_reason, suspended_until, created_at
           FROM user
           ORDER BY created_at DESC
           LIMIT ? OFFSET ?""",
        (per_page, offset)
    )
    
    total_result = await _db.execute("SELECT COUNT(*) as count FROM user")
    total = total_result[0]['count'] if total_result else 0
    
    return {
        "users": users or [],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    }


@app.post("/api/admin/users/{user_id}/promote")
async def admin_promote_user(user_id: int, session: Optional[str] = Cookie(None)):
    """Promote a user to admin."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    # Check target user exists
    target = await _db.execute("SELECT id, is_superadmin FROM user WHERE id = ?", (user_id,))
    if not target or len(target) == 0:
        return JSONResponse({"error": "Usuárie não encontrade"}, status_code=404)
    
    if target[0].get('is_superadmin'):
        return JSONResponse({"error": "Não é possível alterar superadmin"}, status_code=400)
    
    await _db.run("UPDATE user SET is_admin = 1 WHERE id = ?", (user_id,))
    
    return {"success": True, "message": "Usuárie promovide a admin"}


@app.post("/api/admin/users/{user_id}/demote")
async def admin_demote_user(user_id: int, session: Optional[str] = Cookie(None)):
    """Remove admin from a user."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    # Check target user exists
    target = await _db.execute("SELECT id, is_superadmin FROM user WHERE id = ?", (user_id,))
    if not target or len(target) == 0:
        return JSONResponse({"error": "Usuárie não encontrade"}, status_code=404)
    
    if target[0].get('is_superadmin'):
        return JSONResponse({"error": "Não é possível alterar superadmin"}, status_code=400)
    
    await _db.run("UPDATE user SET is_admin = 0 WHERE id = ?", (user_id,))
    
    return {"success": True, "message": "Admin removide de usuárie"}


@app.post("/api/admin/users/{user_id}/ban")
async def admin_ban_user(user_id: int, request: Request, session: Optional[str] = Cookie(None)):
    """Ban a user."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    # Get ban reason from body
    try:
        body = await request.json()
        reason = body.get("reason", "")
    except Exception:
        reason = ""
    
    # Check target user exists
    target = await _db.execute("SELECT id, is_superadmin FROM user WHERE id = ?", (user_id,))
    if not target or len(target) == 0:
        return JSONResponse({"error": "Usuárie não encontrade"}, status_code=404)
    
    if target[0].get('is_superadmin'):
        return JSONResponse({"error": "Não é possível banir superadmin"}, status_code=400)
    
    await _db.run(
        "UPDATE user SET is_banned = 1, banned_at = ?, ban_reason = ? WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), reason, user_id)
    )
    
    return {"success": True, "message": "Usuárie banide"}


@app.post("/api/admin/users/{user_id}/unban")
async def admin_unban_user(user_id: int, session: Optional[str] = Cookie(None)):
    """Unban a user."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    await _db.run(
        "UPDATE user SET is_banned = 0, banned_at = NULL, ban_reason = NULL WHERE id = ?",
        (user_id,)
    )
    
    return {"success": True, "message": "Ban removide"}


@app.post("/api/admin/users/{user_id}/suspend")
async def admin_suspend_user(user_id: int, request: Request, session: Optional[str] = Cookie(None)):
    """Suspend a user for a specified number of hours."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    try:
        body = await request.json()
        hours = int(body.get("hours", 24))
    except Exception:
        hours = 24
    
    if hours <= 0:
        return JSONResponse({"error": "Horas devem ser > 0"}, status_code=400)
    
    # Check target user exists
    target = await _db.execute("SELECT id, is_superadmin FROM user WHERE id = ?", (user_id,))
    if not target or len(target) == 0:
        return JSONResponse({"error": "Usuárie não encontrade"}, status_code=404)
    
    if target[0].get('is_superadmin'):
        return JSONResponse({"error": "Não é possível suspender superadmin"}, status_code=400)
    
    suspended_until = datetime.now(timezone.utc) + timedelta(hours=hours)
    
    await _db.run(
        "UPDATE user SET suspended_until = ? WHERE id = ?",
        (suspended_until.isoformat(), user_id)
    )
    
    return {"success": True, "message": f"Usuárie suspense por {hours} horas"}


@app.post("/api/admin/users/{user_id}/unsuspend")
async def admin_unsuspend_user(user_id: int, session: Optional[str] = Cookie(None)):
    """Remove suspension from a user."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    await _db.run("UPDATE user SET suspended_until = NULL WHERE id = ?", (user_id,))
    
    return {"success": True, "message": "Suspensão removida"}


@app.delete("/api/admin/users/{user_id}")
async def admin_delete_user(user_id: int, session: Optional[str] = Cookie(None)):
    """Delete a user (permanent)."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    # Check target user exists
    target = await _db.execute("SELECT id, is_superadmin FROM user WHERE id = ?", (user_id,))
    if not target or len(target) == 0:
        return JSONResponse({"error": "Usuárie não encontrade"}, status_code=404)
    
    if target[0].get('is_superadmin'):
        return JSONResponse({"error": "Não é possível excluir superadmin"}, status_code=400)
    
    # Can't delete yourself
    if user_id == user['user_id']:
        return JSONResponse({"error": "Você não pode excluir a si mesme"}, status_code=400)
    
    # Delete user's data first
    await _db.run("DELETE FROM seguidores WHERE seguidor_id = ? OR seguido_id = ?", (user_id, user_id))
    await _db.run("DELETE FROM post_likes WHERE user_id = ?", (user_id,))
    await _db.run("DELETE FROM comentario WHERE usuario_id = ?", (user_id,))
    await _db.run("UPDATE post SET is_deleted = 1 WHERE usuario_id = ?", (user_id,))
    await _db.run("DELETE FROM user WHERE id = ?", (user_id,))
    
    return {"success": True, "message": "Usuárie excluíde"}


# --- Reports Management ---

@app.get("/api/admin/reports")
async def admin_list_reports(
    resolved: bool = False,
    page: int = 1,
    per_page: int = 20,
    session: Optional[str] = Cookie(None)
):
    """List reports for admin review."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    offset = (page - 1) * per_page
    resolved_int = 1 if resolved else 0
    
    reports = await _db.execute(
        """SELECT r.id, r.post_id, r.motivo, r.category, r.data, r.resolved, r.resolved_at,
                  u.username as reporter_username,
                  p.conteudo as post_conteudo, p.usuario as post_author
           FROM report r
           LEFT JOIN user u ON r.usuario_id = u.id
           LEFT JOIN post p ON r.post_id = p.id
           WHERE r.resolved = ?
           ORDER BY r.data DESC
           LIMIT ? OFFSET ?""",
        (resolved_int, per_page, offset)
    )
    
    return {"reports": reports or []}


@app.post("/api/admin/reports/{report_id}/resolve")
async def admin_resolve_report(report_id: int, session: Optional[str] = Cookie(None)):
    """Mark a report as resolved."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    await _db.run(
        "UPDATE report SET resolved = 1, resolved_at = ? WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), report_id)
    )
    
    return {"success": True, "message": "Denúncia resolvida"}


@app.post("/api/admin/reports/{report_id}/delete-post")
async def admin_delete_reported_post(report_id: int, session: Optional[str] = Cookie(None)):
    """Delete the post associated with a report and resolve the report."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    # Get report
    reports = await _db.execute("SELECT post_id FROM report WHERE id = ?", (report_id,))
    if not reports or len(reports) == 0:
        return JSONResponse({"error": "Denúncia não encontrada"}, status_code=404)
    
    post_id = reports[0]['post_id']
    
    # Soft delete the post
    await _db.run(
        "UPDATE post SET is_deleted = 1, deleted_at = ?, deleted_by = ? WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), user['user_id'], post_id)
    )
    
    # Resolve the report
    await _db.run(
        "UPDATE report SET resolved = 1, resolved_at = ? WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), report_id)
    )
    
    return {"success": True, "message": "Post excluíde e denúncia resolvida"}


# --- Edu Content Management ---

@app.get("/api/admin/edu")
async def admin_list_edu_content(
    tipo: str = "",
    page: int = 1,
    per_page: int = 20,
    session: Optional[str] = Cookie(None)
):
    """List educational content for admin."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    offset = (page - 1) * per_page
    
    if tipo:
        content = await _db.execute(
            """SELECT id, tipo, titulo, resumo, url, created_at
               FROM edu_content
               WHERE tipo = ?
               ORDER BY created_at DESC
               LIMIT ? OFFSET ?""",
            (tipo, per_page, offset)
        )
    else:
        content = await _db.execute(
            """SELECT id, tipo, titulo, resumo, url, created_at
               FROM edu_content
               ORDER BY created_at DESC
               LIMIT ? OFFSET ?""",
            (per_page, offset)
        )
    
    return {"content": content or []}


@app.post("/api/admin/edu")
async def admin_create_edu_content(request: Request, session: Optional[str] = Cookie(None)):
    """Create new educational content."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    body = await request.json()
    
    tipo = body.get("tipo", "").strip()
    titulo = body.get("titulo", "").strip()
    resumo = body.get("resumo", "").strip()
    corpo = body.get("corpo", "").strip()
    url = body.get("url", "").strip()
    
    if not tipo or not titulo:
        return JSONResponse({"error": "Tipo e título são obrigatórios"}, status_code=400)
    
    await _db.run(
        """INSERT INTO edu_content (tipo, titulo, resumo, corpo, url, author_id, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (tipo, titulo, resumo, corpo, url, user['user_id'], datetime.now(timezone.utc).isoformat())
    )
    
    return {"success": True, "message": "Conteúdo educacional criade"}


@app.put("/api/admin/edu/{content_id}")
async def admin_update_edu_content(content_id: int, request: Request, session: Optional[str] = Cookie(None)):
    """Update educational content."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    body = await request.json()
    
    titulo = body.get("titulo", "").strip()
    resumo = body.get("resumo", "").strip()
    corpo = body.get("corpo", "").strip()
    url = body.get("url", "").strip()
    
    if not titulo:
        return JSONResponse({"error": "Título é obrigatório"}, status_code=400)
    
    await _db.run(
        "UPDATE edu_content SET titulo = ?, resumo = ?, corpo = ?, url = ? WHERE id = ?",
        (titulo, resumo, corpo, url, content_id)
    )
    
    return {"success": True, "message": "Conteúdo atualizade"}


@app.delete("/api/admin/edu/{content_id}")
async def admin_delete_edu_content(content_id: int, session: Optional[str] = Cookie(None)):
    """Delete educational content."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    await _db.run("DELETE FROM edu_content WHERE id = ?", (content_id,))
    
    return {"success": True, "message": "Conteúdo excluíde"}


# ============================================================================
# Phase 5: Dinâmicas (Polls, Forms, Word Games)
# ============================================================================

@app.get("/dinamicas", response_class=HTMLResponse)
async def dinamicas_home(session: Optional[str] = Cookie(None)):
    """Dynamics hub page - polls, forms, games."""
    global _db
    user = get_current_user(session)
    
    if not _db:
        return HTMLResponse(content="<h1>Banco de dados indisponível</h1>", status_code=500)
    
    # Get active dynamics
    dynamics = await _db.execute(
        """SELECT id, tipo, titulo, descricao, created_at
           FROM dynamic
           WHERE active = 1
           ORDER BY created_at DESC
           LIMIT 20"""
    )
    
    # Get word of the day
    palavra_do_dia = await _db.execute(
        """SELECT id, palavra, significado
           FROM palavra_do_dia
           WHERE ativo = 1
           ORDER BY ordem DESC
           LIMIT 1"""
    )
    
    html = render_template("dinamicas.html",
        session_id=session,
        current_user=user,
        dynamics=dynamics or [],
        palavra_do_dia=palavra_do_dia[0] if palavra_do_dia else None
    )
    return HTMLResponse(content=html)


@app.get("/dinamica/{dynamic_id}", response_class=HTMLResponse)
async def view_dynamic(dynamic_id: int, session: Optional[str] = Cookie(None)):
    """View and participate in a dynamic activity."""
    global _db
    user = get_current_user(session)
    
    if not _db:
        return HTMLResponse(content="<h1>Banco de dados indisponível</h1>", status_code=500)
    
    # Get dynamic
    dynamics = await _db.execute(
        "SELECT * FROM dynamic WHERE id = ? AND active = 1",
        (dynamic_id,)
    )
    
    if not dynamics or len(dynamics) == 0:
        return HTMLResponse(content="<h1>Dinâmica não encontrada</h1>", status_code=404)
    
    dynamic = dynamics[0]
    
    # Parse config JSON
    config = {}
    if dynamic.get('config'):
        try:
            config = json.loads(dynamic['config'])
        except Exception:
            pass
    
    # Check if user already responded
    user_response = None
    if user:
        responses = await _db.execute(
            "SELECT * FROM dynamic_response WHERE dynamic_id = ? AND usuario_id = ?",
            (dynamic_id, user['user_id'])
        )
        if responses and len(responses) > 0:
            user_response = responses[0]
            if user_response.get('payload'):
                try:
                    user_response['payload'] = json.loads(user_response['payload'])
                except Exception:
                    pass
    
    # Get response stats for polls
    stats = None
    if dynamic.get('tipo') == 'enquete':
        all_responses = await _db.execute(
            "SELECT payload FROM dynamic_response WHERE dynamic_id = ?",
            (dynamic_id,)
        )
        if all_responses:
            stats = {}
            for resp in all_responses:
                try:
                    payload = json.loads(resp['payload']) if resp.get('payload') else {}
                    choice = payload.get('choice', '')
                    if choice:
                        stats[choice] = stats.get(choice, 0) + 1
                except Exception:
                    pass
    
    html = render_template("dinamica_view.html",
        session_id=session,
        current_user=user,
        dynamic=dynamic,
        config=config,
        user_response=user_response,
        stats=stats
    )
    return HTMLResponse(content=html)


@app.post("/api/dinamicas/{dynamic_id}/respond")
async def respond_to_dynamic(dynamic_id: int, request: Request, session: Optional[str] = Cookie(None)):
    """Submit a response to a dynamic activity."""
    global _db
    user = get_current_user(session)
    
    if not user:
        return JSONResponse({"error": "Não autenticade"}, status_code=401)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    # Check dynamic exists
    dynamics = await _db.execute(
        "SELECT * FROM dynamic WHERE id = ? AND active = 1",
        (dynamic_id,)
    )
    
    if not dynamics or len(dynamics) == 0:
        return JSONResponse({"error": "Dinâmica não encontrada"}, status_code=404)
    
    # Check if already responded
    existing = await _db.execute(
        "SELECT id FROM dynamic_response WHERE dynamic_id = ? AND usuario_id = ?",
        (dynamic_id, user['user_id'])
    )
    
    if existing and len(existing) > 0:
        return JSONResponse({"error": "Você já respondeu a esta dinâmica"}, status_code=400)
    
    body = await request.json()
    payload = json.dumps(body)
    
    await _db.run(
        """INSERT INTO dynamic_response (dynamic_id, usuario_id, payload, created_at)
           VALUES (?, ?, ?, ?)""",
        (dynamic_id, user['user_id'], payload, datetime.now(timezone.utc).isoformat())
    )
    
    return {"success": True, "message": "Resposta enviada"}


@app.get("/api/dinamicas")
async def list_dynamics(
    tipo: str = "",
    page: int = 1,
    per_page: int = 20,
    session: Optional[str] = Cookie(None)
):
    """List active dynamic activities."""
    global _db
    
    if not _db:
        return {"dynamics": [], "error": "Banco de dados indisponível"}
    
    offset = (page - 1) * per_page
    
    if tipo:
        dynamics = await _db.execute(
            """SELECT id, tipo, titulo, descricao, created_at
               FROM dynamic
               WHERE active = 1 AND tipo = ?
               ORDER BY created_at DESC
               LIMIT ? OFFSET ?""",
            (tipo, per_page, offset)
        )
    else:
        dynamics = await _db.execute(
            """SELECT id, tipo, titulo, descricao, created_at
               FROM dynamic
               WHERE active = 1
               ORDER BY created_at DESC
               LIMIT ? OFFSET ?""",
            (per_page, offset)
        )
    
    return {"dynamics": dynamics or []}


@app.get("/api/dinamicas/{dynamic_id}")
async def get_dynamic(dynamic_id: int, session: Optional[str] = Cookie(None)):
    """Get a specific dynamic activity."""
    global _db
    user = get_current_user(session)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    dynamics = await _db.execute(
        "SELECT * FROM dynamic WHERE id = ?",
        (dynamic_id,)
    )
    
    if not dynamics or len(dynamics) == 0:
        return JSONResponse({"error": "Dinâmica não encontrada"}, status_code=404)
    
    dynamic = dynamics[0]
    
    # Parse config
    config = {}
    if dynamic.get('config'):
        try:
            config = json.loads(dynamic['config'])
        except Exception:
            pass
    
    # Get response count
    count_result = await _db.execute(
        "SELECT COUNT(*) as count FROM dynamic_response WHERE dynamic_id = ?",
        (dynamic_id,)
    )
    response_count = count_result[0]['count'] if count_result else 0
    
    # Check if user responded
    user_responded = False
    if user:
        existing = await _db.execute(
            "SELECT 1 FROM dynamic_response WHERE dynamic_id = ? AND usuario_id = ?",
            (dynamic_id, user['user_id'])
        )
        user_responded = existing and len(existing) > 0
    
    return {
        "id": dynamic['id'],
        "tipo": dynamic.get('tipo', ''),
        "titulo": dynamic.get('titulo', ''),
        "descricao": dynamic.get('descricao', ''),
        "config": config,
        "active": dynamic.get('active', 1),
        "response_count": response_count,
        "user_responded": user_responded,
        "created_at": dynamic.get('created_at', '')
    }


@app.get("/api/dinamicas/{dynamic_id}/results")
async def get_dynamic_results(dynamic_id: int, session: Optional[str] = Cookie(None)):
    """Get results/stats for a dynamic activity."""
    global _db
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    # Get dynamic
    dynamics = await _db.execute(
        "SELECT tipo FROM dynamic WHERE id = ?",
        (dynamic_id,)
    )
    
    if not dynamics or len(dynamics) == 0:
        return JSONResponse({"error": "Dinâmica não encontrada"}, status_code=404)
    
    dynamic = dynamics[0]
    
    # Get all responses
    responses = await _db.execute(
        "SELECT payload, created_at FROM dynamic_response WHERE dynamic_id = ? ORDER BY created_at ASC",
        (dynamic_id,)
    )
    
    # Calculate stats based on type
    stats = {}
    total = len(responses) if responses else 0
    
    if dynamic.get('tipo') == 'enquete':
        # Count votes per option
        for resp in (responses or []):
            try:
                payload = json.loads(resp['payload']) if resp.get('payload') else {}
                choice = payload.get('choice', '')
                if choice:
                    stats[choice] = stats.get(choice, 0) + 1
            except Exception:
                pass
    
    return {
        "total_responses": total,
        "stats": stats,
        "tipo": dynamic.get('tipo', '')
    }


# --- Palavra do Dia (Word of the Day) ---

@app.get("/api/palavra-do-dia")
async def get_palavra_do_dia(session: Optional[str] = Cookie(None)):
    """Get current word of the day."""
    global _db
    user = get_current_user(session)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    palavra = await _db.execute(
        """SELECT id, palavra, significado
           FROM palavra_do_dia
           WHERE ativo = 1
           ORDER BY ordem DESC
           LIMIT 1"""
    )
    
    if not palavra or len(palavra) == 0:
        return {"palavra": None}
    
    p = palavra[0]
    
    # Check user interactions
    conhecia = False
    frase = None
    if user:
        interactions = await _db.execute(
            "SELECT tipo, frase FROM palavra_do_dia_interacao WHERE palavra_id = ? AND usuario_id = ?",
            (p['id'], user['user_id'])
        )
        if interactions:
            for i in interactions:
                if i.get('tipo') == 'conhecia':
                    conhecia = True
                if i.get('tipo') == 'frase':
                    frase = i.get('frase')
    
    return {
        "id": p['id'],
        "palavra": p['palavra'],
        "significado": p['significado'],
        "conhecia": conhecia,
        "frase": frase
    }


@app.post("/api/palavra-do-dia/{palavra_id}/conhecia")
async def mark_palavra_conhecida(palavra_id: int, session: Optional[str] = Cookie(None)):
    """Mark that user already knew the word."""
    global _db
    user = get_current_user(session)
    
    if not user:
        return JSONResponse({"error": "Não autenticade"}, status_code=401)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    # Check if already marked
    existing = await _db.execute(
        "SELECT id FROM palavra_do_dia_interacao WHERE palavra_id = ? AND usuario_id = ? AND tipo = 'conhecia'",
        (palavra_id, user['user_id'])
    )
    
    if existing and len(existing) > 0:
        return {"success": True, "message": "Já marcade"}
    
    await _db.run(
        """INSERT INTO palavra_do_dia_interacao (palavra_id, usuario_id, tipo, created_at)
           VALUES (?, ?, 'conhecia', ?)""",
        (palavra_id, user['user_id'], datetime.now(timezone.utc).isoformat())
    )
    
    return {"success": True, "message": "Palavra marcada como conhecida"}


@app.post("/api/palavra-do-dia/{palavra_id}/frase")
async def submit_frase_palavra(palavra_id: int, request: Request, session: Optional[str] = Cookie(None)):
    """Submit a sentence using the word of the day."""
    global _db
    user = get_current_user(session)
    
    if not user:
        return JSONResponse({"error": "Não autenticade"}, status_code=401)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    body = await request.json()
    frase = body.get("frase", "").strip()
    
    if not frase:
        return JSONResponse({"error": "Frase é obrigatória"}, status_code=400)
    
    # Check if already submitted
    existing = await _db.execute(
        "SELECT id FROM palavra_do_dia_interacao WHERE palavra_id = ? AND usuario_id = ? AND tipo = 'frase'",
        (palavra_id, user['user_id'])
    )
    
    if existing and len(existing) > 0:
        # Update existing
        await _db.run(
            "UPDATE palavra_do_dia_interacao SET frase = ? WHERE id = ?",
            (frase, existing[0]['id'])
        )
    else:
        await _db.run(
            """INSERT INTO palavra_do_dia_interacao (palavra_id, usuario_id, tipo, frase, created_at)
               VALUES (?, ?, 'frase', ?, ?)""",
            (palavra_id, user['user_id'], frase, datetime.now(timezone.utc).isoformat())
        )
    
    return {"success": True, "message": "Frase enviada"}


@app.get("/api/palavra-do-dia/{palavra_id}/frases")
async def get_frases_palavra(palavra_id: int, session: Optional[str] = Cookie(None)):
    """Get sentences submitted for a word."""
    global _db
    
    if not _db:
        return {"frases": [], "error": "Banco de dados indisponível"}
    
    frases = await _db.execute(
        """SELECT i.frase, i.created_at, u.username, u.foto_perfil
           FROM palavra_do_dia_interacao i
           LEFT JOIN user u ON i.usuario_id = u.id
           WHERE i.palavra_id = ? AND i.tipo = 'frase' AND i.frase IS NOT NULL
           ORDER BY i.created_at DESC
           LIMIT 50""",
        (palavra_id,)
    )
    
    result = []
    for f in (frases or []):
        result.append({
            "frase": f.get('frase', ''),
            "username": f.get('username', 'Anônime'),
            "foto_perfil": f.get('foto_perfil', 'img/perfil.png'),
            "created_at": f.get('created_at', '')
        })
    
    return {"frases": result}


# --- Admin: Dynamic Management ---

@app.post("/api/admin/dinamicas")
async def admin_create_dynamic(request: Request, session: Optional[str] = Cookie(None)):
    """Create a new dynamic activity (admin only)."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    body = await request.json()
    
    tipo = body.get("tipo", "").strip()
    titulo = body.get("titulo", "").strip()
    descricao = body.get("descricao", "").strip()
    config = body.get("config", {})
    
    if not tipo or not titulo:
        return JSONResponse({"error": "Tipo e título são obrigatórios"}, status_code=400)
    
    config_json = json.dumps(config) if config else "{}"
    
    await _db.run(
        """INSERT INTO dynamic (tipo, titulo, descricao, config, active, created_at, created_by)
           VALUES (?, ?, ?, ?, 1, ?, ?)""",
        (tipo, titulo, descricao, config_json, datetime.now(timezone.utc).isoformat(), user['user_id'])
    )
    
    return {"success": True, "message": "Dinâmica criada"}


@app.put("/api/admin/dinamicas/{dynamic_id}")
async def admin_update_dynamic(dynamic_id: int, request: Request, session: Optional[str] = Cookie(None)):
    """Update a dynamic activity (admin only)."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    body = await request.json()
    
    titulo = body.get("titulo", "").strip()
    descricao = body.get("descricao", "").strip()
    config = body.get("config", {})
    active = body.get("active", 1)
    
    config_json = json.dumps(config) if config else "{}"
    
    await _db.run(
        "UPDATE dynamic SET titulo = ?, descricao = ?, config = ?, active = ? WHERE id = ?",
        (titulo, descricao, config_json, active, dynamic_id)
    )
    
    return {"success": True, "message": "Dinâmica atualizada"}


@app.delete("/api/admin/dinamicas/{dynamic_id}")
async def admin_delete_dynamic(dynamic_id: int, session: Optional[str] = Cookie(None)):
    """Delete a dynamic activity (admin only)."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    # Delete responses first
    await _db.run("DELETE FROM dynamic_response WHERE dynamic_id = ?", (dynamic_id,))
    await _db.run("DELETE FROM dynamic WHERE id = ?", (dynamic_id,))
    
    return {"success": True, "message": "Dinâmica excluída"}


@app.post("/api/admin/palavra-do-dia")
async def admin_create_palavra(request: Request, session: Optional[str] = Cookie(None)):
    """Create a new word of the day (admin only)."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    body = await request.json()
    
    palavra = body.get("palavra", "").strip()
    significado = body.get("significado", "").strip()
    ordem = body.get("ordem", 0)
    
    if not palavra or not significado:
        return JSONResponse({"error": "Palavra e significado são obrigatórios"}, status_code=400)
    
    await _db.run(
        """INSERT INTO palavra_do_dia (palavra, significado, ordem, ativo, created_at, created_by)
           VALUES (?, ?, ?, 1, ?, ?)""",
        (palavra, significado, ordem, datetime.now(timezone.utc).isoformat(), user['user_id'])
    )
    
    return {"success": True, "message": "Palavra criada"}


@app.put("/api/admin/palavra-do-dia/{palavra_id}")
async def admin_update_palavra(palavra_id: int, request: Request, session: Optional[str] = Cookie(None)):
    """Update a word of the day (admin only)."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    body = await request.json()
    
    palavra = body.get("palavra", "").strip()
    significado = body.get("significado", "").strip()
    ordem = body.get("ordem", 0)
    ativo = body.get("ativo", 1)
    
    await _db.run(
        "UPDATE palavra_do_dia SET palavra = ?, significado = ?, ordem = ?, ativo = ? WHERE id = ?",
        (palavra, significado, ordem, ativo, palavra_id)
    )
    
    return {"success": True, "message": "Palavra atualizada"}


@app.delete("/api/admin/palavra-do-dia/{palavra_id}")
async def admin_delete_palavra(palavra_id: int, session: Optional[str] = Cookie(None)):
    """Delete a word of the day (admin only)."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    # Delete interactions first
    await _db.run("DELETE FROM palavra_do_dia_interacao WHERE palavra_id = ?", (palavra_id,))
    await _db.run("DELETE FROM palavra_do_dia WHERE id = ?", (palavra_id,))
    
    return {"success": True, "message": "Palavra excluída"}


# ============================================================================
# Additional Routes (Educational Content, Support, etc.)
# ============================================================================

@app.get("/artigos", response_class=HTMLResponse)
async def artigos(session: Optional[str] = Cookie(None)):
    """Articles page."""
    global _db
    user = get_current_user(session)
    
    articles = []
    if _db:
        articles = await _db.execute(
            """SELECT id, titulo, resumo, url, created_at
               FROM edu_content
               WHERE tipo = 'artigo'
               ORDER BY created_at DESC
               LIMIT 50"""
        )
    
    html = render_template("artigos.html",
        session_id=session,
        current_user=user,
        artigos=articles or []
    )
    return HTMLResponse(content=html)


@app.get("/apostilas", response_class=HTMLResponse)
async def apostilas(session: Optional[str] = Cookie(None)):
    """Study materials page."""
    global _db
    user = get_current_user(session)
    
    apostilas_list = []
    if _db:
        apostilas_list = await _db.execute(
            """SELECT id, titulo, resumo, url, file_path, created_at
               FROM edu_content
               WHERE tipo = 'apostila'
               ORDER BY created_at DESC
               LIMIT 50"""
        )
    
    html = render_template("apostilas.html",
        session_id=session,
        current_user=user,
        apostilas=apostilas_list or []
    )
    return HTMLResponse(content=html)


@app.get("/podcasts", response_class=HTMLResponse)
async def podcasts(session: Optional[str] = Cookie(None)):
    """Podcasts page."""
    global _db
    user = get_current_user(session)
    
    podcasts_list = []
    if _db:
        podcasts_list = await _db.execute(
            """SELECT id, titulo, resumo, url, created_at
               FROM edu_content
               WHERE tipo = 'podcast'
               ORDER BY created_at DESC
               LIMIT 50"""
        )
    
    html = render_template("podcasts.html",
        session_id=session,
        current_user=user,
        podcasts=podcasts_list or []
    )
    return HTMLResponse(content=html)


@app.get("/videos", response_class=HTMLResponse)
async def videos(session: Optional[str] = Cookie(None)):
    """Videos page."""
    global _db
    user = get_current_user(session)
    
    videos_list = []
    if _db:
        videos_list = await _db.execute(
            """SELECT id, titulo, resumo, url, created_at
               FROM edu_content
               WHERE tipo = 'video'
               ORDER BY created_at DESC
               LIMIT 50"""
        )
    
    html = render_template("videos.html",
        session_id=session,
        current_user=user,
        videos=videos_list or []
    )
    return HTMLResponse(content=html)


@app.get("/exercicios", response_class=HTMLResponse)
async def exercicios(session: Optional[str] = Cookie(None)):
    """Exercises page."""
    global _db
    user = get_current_user(session)
    
    topics = []
    if _db:
        topics = await _db.execute(
            """SELECT id, nome, descricao, created_at
               FROM exercise_topic
               ORDER BY nome ASC"""
        )
    
    html = render_template("exercicios.html",
        session_id=session,
        current_user=user,
        topics=topics or []
    )
    return HTMLResponse(content=html)


@app.get("/redacao", response_class=HTMLResponse)
async def redacao(session: Optional[str] = Cookie(None)):
    """Essay/writing page."""
    global _db
    user = get_current_user(session)
    
    temas = []
    if _db:
        temas = await _db.execute(
            """SELECT id, titulo, resumo, created_at
               FROM edu_content
               WHERE tipo = 'redacao_tema'
               ORDER BY created_at DESC
               LIMIT 20"""
        )
    
    html = render_template("redacao.html",
        session_id=session,
        current_user=user,
        temas=temas or []
    )
    return HTMLResponse(content=html)


@app.get("/variacoes", response_class=HTMLResponse)
async def variacoes(session: Optional[str] = Cookie(None)):
    """Linguistic variations page."""
    global _db
    user = get_current_user(session)
    
    variacoes_list = []
    if _db:
        variacoes_list = await _db.execute(
            """SELECT id, titulo, resumo, corpo, created_at
               FROM edu_content
               WHERE tipo = 'variacao'
               ORDER BY created_at DESC
               LIMIT 50"""
        )
    
    html = render_template("variacoes.html",
        session_id=session,
        current_user=user,
        variacoes=variacoes_list or []
    )
    return HTMLResponse(content=html)


# --- Support Tickets ---

@app.post("/suporte")
async def suporte_submit(
    request: Request,
    mensagem: str = Form(...),
    nome: str = Form(""),
    email: str = Form(""),
    session: Optional[str] = Cookie(None)
):
    """Submit a support ticket."""
    global _db
    user = get_current_user(session)
    
    if not _db:
        flash("Erro de banco de dados", "error", session)
        return RedirectResponse(url="/suporte", status_code=302)
    
    user_id = user['user_id'] if user else None
    
    await _db.run(
        """INSERT INTO support_ticket (usuario_id, nome, email, mensagem, status, created_at)
           VALUES (?, ?, ?, ?, 'aberto', ?)""",
        (user_id, nome, email, mensagem, datetime.now(timezone.utc).isoformat())
    )
    
    flash("Mensagem enviada! Responderemos em breve.", "success", session)
    return RedirectResponse(url="/suporte", status_code=302)


@app.get("/api/admin/suporte")
async def admin_list_tickets(
    status: str = "aberto",
    page: int = 1,
    per_page: int = 20,
    session: Optional[str] = Cookie(None)
):
    """List support tickets (admin only)."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    offset = (page - 1) * per_page
    
    tickets = await _db.execute(
        """SELECT t.id, t.nome, t.email, t.mensagem, t.status, t.resposta, t.created_at, t.updated_at,
                  u.username
           FROM support_ticket t
           LEFT JOIN user u ON t.usuario_id = u.id
           WHERE t.status = ?
           ORDER BY t.created_at DESC
           LIMIT ? OFFSET ?""",
        (status, per_page, offset)
    )
    
    return {"tickets": tickets or []}


@app.post("/api/admin/suporte/{ticket_id}/responder")
async def admin_respond_ticket(ticket_id: int, request: Request, session: Optional[str] = Cookie(None)):
    """Respond to a support ticket (admin only)."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    body = await request.json()
    resposta = body.get("resposta", "").strip()
    
    if not resposta:
        return JSONResponse({"error": "Resposta é obrigatória"}, status_code=400)
    
    await _db.run(
        "UPDATE support_ticket SET resposta = ?, status = 'respondido', updated_at = ? WHERE id = ?",
        (resposta, datetime.now(timezone.utc).isoformat(), ticket_id)
    )
    
    return {"success": True, "message": "Resposta enviada"}


@app.post("/api/admin/suporte/{ticket_id}/fechar")
async def admin_close_ticket(ticket_id: int, session: Optional[str] = Cookie(None)):
    """Close a support ticket (admin only)."""
    global _db
    user = get_current_user(session)
    
    if not require_admin(user):
        return JSONResponse({"error": "Acesso restrito"}, status_code=403)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    await _db.run(
        "UPDATE support_ticket SET status = 'fechado', updated_at = ? WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), ticket_id)
    )
    
    return {"success": True, "message": "Ticket fechado"}


# --- Reports API ---

@app.post("/api/posts/{post_id}/relatar")
async def relatar_post(post_id: int, request: Request, session: Optional[str] = Cookie(None)):
    """Report a post."""
    global _db
    user = get_current_user(session)
    
    if not user:
        return JSONResponse({"error": "Não autenticade"}, status_code=401)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    body = await request.json()
    motivo = body.get("motivo", "").strip()
    category = body.get("category", "outro").strip()
    
    if not motivo:
        return JSONResponse({"error": "Motivo é obrigatório"}, status_code=400)
    
    await _db.run(
        """INSERT INTO report (post_id, usuario_id, motivo, category, data, resolved)
           VALUES (?, ?, ?, ?, ?, 0)""",
        (post_id, user['user_id'], motivo, category, datetime.now(timezone.utc).isoformat())
    )
    
    return {"success": True, "message": "Denúncia enviada"}


# --- Divulgação (Featured Content) ---

@app.get("/api/divulgacao")
async def api_divulgacao(area: str = "", session: Optional[str] = Cookie(None)):
    """Get featured content cards."""
    global _db
    
    if not _db:
        return {"divulgacoes": []}
    
    if area:
        divulgacoes = await _db.execute(
            """SELECT id, area, titulo, texto, link, imagem, ordem
               FROM divulgacao
               WHERE ativo = 1 AND area = ?
               ORDER BY ordem ASC, created_at DESC
               LIMIT 20""",
            (area,)
        )
    else:
        divulgacoes = await _db.execute(
            """SELECT id, area, titulo, texto, link, imagem, ordem
               FROM divulgacao
               WHERE ativo = 1
               ORDER BY ordem ASC, created_at DESC
               LIMIT 20"""
        )
    
    return {"divulgacoes": divulgacoes or []}


@app.get("/api/novidades")
async def api_novidades(session: Optional[str] = Cookie(None)):
    """Get news/updates."""
    global _db
    
    if not _db:
        return {"novidades": []}
    
    novidades = await _db.execute(
        """SELECT id, titulo, descricao, link, created_at
           FROM edu_novidade
           ORDER BY created_at DESC
           LIMIT 10"""
    )
    
    return {"novidades": novidades or []}


@app.get("/novidade/{novidade_id}", response_class=HTMLResponse)
async def novidade_detail(novidade_id: int, session: Optional[str] = Cookie(None)):
    """View a news item detail."""
    global _db
    user = get_current_user(session)
    
    if not _db:
        return HTMLResponse(content="<h1>Banco de dados indisponível</h1>", status_code=500)
    
    novidades = await _db.execute(
        "SELECT * FROM edu_novidade WHERE id = ?",
        (novidade_id,)
    )
    
    if not novidades or len(novidades) == 0:
        return HTMLResponse(content="<h1>Novidade não encontrada</h1>", status_code=404)
    
    html = render_template("novidade_detail.html",
        session_id=session,
        current_user=user,
        novidade=novidades[0]
    )
    return HTMLResponse(content=html)


# --- Exercise API ---

@app.get("/api/exercicios/topics")
async def api_exercise_topics(session: Optional[str] = Cookie(None)):
    """Get exercise topics."""
    global _db
    
    if not _db:
        return {"topics": []}
    
    topics = await _db.execute(
        """SELECT id, nome, descricao
           FROM exercise_topic
           ORDER BY nome ASC"""
    )
    
    return {"topics": topics or []}


@app.get("/api/exercicios/topics/{topic_id}/sections")
async def api_exercise_sections(topic_id: int, session: Optional[str] = Cookie(None)):
    """Get sections for an exercise topic."""
    global _db
    
    if not _db:
        return {"sections": []}
    
    sections = await _db.execute(
        """SELECT id, nome, descricao, ordem
           FROM exercise_section
           WHERE topic_id = ?
           ORDER BY ordem ASC, nome ASC""",
        (topic_id,)
    )
    
    return {"sections": sections or []}


@app.get("/api/exercicios/topics/{topic_id}/questions")
async def api_exercise_questions(
    topic_id: int,
    section_id: Optional[int] = None,
    session: Optional[str] = Cookie(None)
):
    """Get questions for an exercise topic/section."""
    global _db
    
    if not _db:
        return {"questions": []}
    
    if section_id:
        questions = await _db.execute(
            """SELECT id, enunciado, resposta, dificuldade, tipo, opcoes
               FROM exercise_question
               WHERE topic_id = ? AND section_id = ?
               ORDER BY id ASC""",
            (topic_id, section_id)
        )
    else:
        questions = await _db.execute(
            """SELECT id, enunciado, resposta, dificuldade, tipo, opcoes
               FROM exercise_question
               WHERE topic_id = ?
               ORDER BY id ASC""",
            (topic_id,)
        )
    
    result = []
    for q in (questions or []):
        opcoes = []
        if q.get('opcoes'):
            try:
                opcoes = json.loads(q['opcoes'])
            except Exception:
                pass
        result.append({
            "id": q['id'],
            "enunciado": q.get('enunciado', ''),
            "dificuldade": q.get('dificuldade', 'medio'),
            "tipo": q.get('tipo', 'multipla_escolha'),
            "opcoes": opcoes
        })
    
    return {"questions": result}


@app.post("/api/exercicios/check")
async def api_exercise_check(request: Request, session: Optional[str] = Cookie(None)):
    """Check exercise answer."""
    global _db
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    body = await request.json()
    question_id = body.get("question_id")
    answer = body.get("answer", "").strip()
    
    if not question_id:
        return JSONResponse({"error": "ID da questão obrigatório"}, status_code=400)
    
    questions = await _db.execute(
        "SELECT resposta FROM exercise_question WHERE id = ?",
        (question_id,)
    )
    
    if not questions or len(questions) == 0:
        return JSONResponse({"error": "Questão não encontrada"}, status_code=404)
    
    correct_answer = questions[0].get('resposta', '')
    is_correct = answer.lower().strip() == correct_answer.lower().strip()
    
    return {
        "correct": is_correct,
        "correct_answer": correct_answer if not is_correct else None
    }


# --- Search API ---

@app.get("/api/search/suggest")
async def api_search_suggest(q: str = "", session: Optional[str] = Cookie(None)):
    """Search suggestions."""
    global _db
    
    if not _db or not q or len(q) < 2:
        return {"suggestions": []}
    
    # Search in posts
    posts = await _db.execute(
        """SELECT conteudo FROM post
           WHERE (is_deleted = 0 OR is_deleted IS NULL)
           AND conteudo LIKE ?
           ORDER BY data DESC
           LIMIT 5""",
        (f"%{q}%",)
    )
    
    # Search in edu content
    edu = await _db.execute(
        """SELECT titulo FROM edu_content
           WHERE titulo LIKE ?
           ORDER BY created_at DESC
           LIMIT 5""",
        (f"%{q}%",)
    )
    
    suggestions = []
    for p in (posts or []):
        text = (p.get('conteudo') or '')[:50]
        if text and text not in suggestions:
            suggestions.append(text)
    for e in (edu or []):
        title = e.get('titulo', '')
        if title and title not in suggestions:
            suggestions.append(title)
    
    return {"suggestions": suggestions[:10]}


# --- Profile Edit ---

@app.post("/api/editar-perfil")
async def editar_perfil(request: Request, session: Optional[str] = Cookie(None)):
    """Edit user profile."""
    global _db
    user = get_current_user(session)
    
    if not user:
        return JSONResponse({"error": "Não autenticade"}, status_code=401)
    
    if not _db:
        return JSONResponse({"error": "Banco de dados indisponível"}, status_code=500)
    
    body = await request.json()
    
    nome = body.get("nome", "").strip()
    bio = body.get("bio", "").strip()
    genero = body.get("genero", "").strip()
    pronome = body.get("pronome", "").strip()
    
    await _db.run(
        "UPDATE user SET nome = ?, bio = ?, genero = ?, pronome = ? WHERE id = ?",
        (nome, bio, genero, pronome, user['user_id'])
    )
    
    return {"success": True, "message": "Perfil atualizado"}


# --- Notifications (simplified) ---

@app.get("/api/notifications")
async def api_notifications(session: Optional[str] = Cookie(None)):
    """Get user notifications (simplified - shows recent activity)."""
    global _db
    user = get_current_user(session)
    
    if not user:
        return JSONResponse({"error": "Não autenticade"}, status_code=401)
    
    if not _db:
        return {"notifications": []}
    
    notifications = []
    
    # Get recent likes on user's posts
    likes = await _db.execute(
        """SELECT u.username, p.id as post_id, pl.user_id
           FROM post_likes pl
           JOIN user u ON pl.user_id = u.id
           JOIN post p ON pl.post_id = p.id
           WHERE p.usuario_id = ? AND pl.user_id != ?
           ORDER BY p.id DESC
           LIMIT 10""",
        (user['user_id'], user['user_id'])
    )
    
    for like in (likes or []):
        notifications.append({
            "type": "like",
            "message": f"@{like['username']} curtiu seu post",
            "post_id": like['post_id']
        })
    
    # Get recent comments on user's posts
    comments = await _db.execute(
        """SELECT u.username, c.post_id, c.data
           FROM comentario c
           JOIN user u ON c.usuario_id = u.id
           JOIN post p ON c.post_id = p.id
           WHERE p.usuario_id = ? AND c.usuario_id != ?
           ORDER BY c.data DESC
           LIMIT 10""",
        (user['user_id'], user['user_id'])
    )
    
    for comment in (comments or []):
        notifications.append({
            "type": "comment",
            "message": f"@{comment['username']} comentou no seu post",
            "post_id": comment['post_id'],
            "data": comment['data']
        })
    
    # Get new followers
    followers = await _db.execute(
        """SELECT u.username
           FROM seguidores s
           JOIN user u ON s.seguidor_id = u.id
           WHERE s.seguido_id = ?
           ORDER BY u.id DESC
           LIMIT 5""",
        (user['user_id'],)
    )
    
    for follower in (followers or []):
        notifications.append({
            "type": "follow",
            "message": f"@{follower['username']} começou a te seguir"
        })
    
    return {"notifications": notifications[:20]}


# --- Amigues (Friends) ---

@app.get("/api/amigues")
async def api_amigues(session: Optional[str] = Cookie(None)):
    """Get mutual followers (amigues)."""
    global _db
    user = get_current_user(session)
    
    if not user:
        return JSONResponse({"error": "Não autenticade"}, status_code=401)
    
    if not _db:
        return {"amigues": []}
    
    # Find mutual followers (user follows them AND they follow user)
    amigues = await _db.execute(
        """SELECT u.id, u.username, u.nome, u.foto_perfil
           FROM user u
           WHERE EXISTS (
               SELECT 1 FROM seguidores s1 
               WHERE s1.seguidor_id = ? AND s1.seguido_id = u.id
           )
           AND EXISTS (
               SELECT 1 FROM seguidores s2
               WHERE s2.seguidor_id = u.id AND s2.seguido_id = ?
           )
           ORDER BY u.username ASC
           LIMIT 50""",
        (user['user_id'], user['user_id'])
    )
    
    result = []
    for a in (amigues or []):
        result.append({
            "id": a['id'],
            "username": a['username'],
            "nome": a.get('nome', ''),
            "foto_perfil": a.get('foto_perfil', 'img/perfil.png')
        })
    
    return {"amigues": result}


# ============================================================================
# Static Files (for local development)
# ============================================================================

# Note: In Cloudflare Workers, static files should be served via R2 or Assets
# This is a fallback for local development
try:
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
except Exception:
    pass  # Static files may not be available in Workers environment


# ============================================================================
# Cloudflare Worker Entry Point
# ============================================================================

class Default(WorkerEntrypoint):
    """Cloudflare Worker entry point that delegates to FastAPI via ASGI."""
    
    async def fetch(self, request):
        """Handle incoming requests by delegating to the FastAPI ASGI app."""
        global _db
        
        # Initialize D1 database for this request
        _db = D1Database(self.env)
        
        # Use ASGI adapter to handle the request
        import asgi
        return await asgi.fetch(app, request.js_object, self.env)
