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
    'main.dinamicas_home': '/dinamicas',
    'main.suporte': '/suporte',
    'main.configuracoes': '/configuracoes',
    'main.novo_post': '/novo_post',
    'main.post_detail': '/post/<int:post_id>',
    'main.perfil_publico': '/perfil/<username>',
    'admin.dashboard': '/admin',
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
