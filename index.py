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
from typing import Optional

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

# ============================================================================
# Helper Functions
# ============================================================================

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

def create_session(user_id: int, username: str) -> str:
    """Create a new session and return session ID."""
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {
        "user_id": user_id,
        "username": username,
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

def render_template(template_name: str, **context) -> str:
    """Render a Jinja2 template with context."""
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
        admin=False,  # TODO: check if user is admin
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
    
    html = render_template("login.html")
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
        # Fallback: demo user for testing
        if email == "demo@gramatike.com" and password == "demo123":
            session_id = create_session(1, "demo")
            response = RedirectResponse(url="/", status_code=302)
            response.set_cookie(key="session", value=session_id, httponly=True, secure=True, samesite="lax", max_age=604800)
            return response
        return RedirectResponse(url="/login?error=invalid", status_code=302)
    
    # Query user from D1
    users = await _db.execute(
        "SELECT id, username, password FROM user WHERE email = ? OR username = ?",
        (email, email)
    )
    
    if not users or len(users) == 0:
        return RedirectResponse(url="/login?error=invalid", status_code=302)
    
    user = users[0]
    if not verify_password(password, user['password']):
        return RedirectResponse(url="/login?error=invalid", status_code=302)
    
    # Create session
    session_id = create_session(user['id'], user['username'])
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="session", value=session_id, httponly=True, secure=True, samesite="lax", max_age=604800)
    return response


@app.get("/logout")
async def logout(session: Optional[str] = Cookie(None)):
    """Logout and clear session."""
    if session and session in sessions:
        del sessions[session]
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="session")
    return response


@app.get("/cadastro", response_class=HTMLResponse)
async def cadastro_page():
    """Registration page."""
    html = render_template("cadastro.html")
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
    
    html = render_template("meu_perfil.html", usuario=user)
    return HTMLResponse(content=html)


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
        """SELECT p.id, p.usuario, p.conteudo, p.imagem, p.data, u.foto_perfil
           FROM post p
           LEFT JOIN user u ON p.usuario_id = u.id
           WHERE p.is_deleted = 0 OR p.is_deleted IS NULL
           ORDER BY p.data DESC
           LIMIT 50"""
    )
    
    result = []
    for p in (posts or []):
        result.append({
            "id": p.get("id"),
            "usuario": p.get("usuario", "Usuárie"),
            "conteudo": p.get("conteudo", ""),
            "imagem": p.get("imagem", ""),
            "data": p.get("data", ""),
            "foto_perfil": p.get("foto_perfil", "img/perfil.png"),
            "liked": False
        })
    
    return {"posts": result}


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
