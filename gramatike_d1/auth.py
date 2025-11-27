# gramatike_d1/auth.py
# Módulo de autenticação para Cloudflare Workers
# Gerencia login, logout, sessões via cookies
#
# NOTA: Renomeado de 'workers/' para 'gramatike_d1/' para evitar conflito
# com o módulo 'workers' built-in do Cloudflare Workers Python.

import json
from .db import (
    get_user_by_username, get_user_by_email, verify_password,
    create_session, get_session, delete_session, create_user
)

# Nome do cookie de sessão
SESSION_COOKIE = 'gramatike_session'


def get_session_token(request):
    """Extrai o token de sessão do cookie."""
    cookie_header = request.headers.get('Cookie', '')
    for cookie in cookie_header.split(';'):
        cookie = cookie.strip()
        if cookie.startswith(f'{SESSION_COOKIE}='):
            return cookie[len(f'{SESSION_COOKIE}='):]
    return None


def set_session_cookie(token, max_age=2592000):
    """Cria o header Set-Cookie para a sessão."""
    return f"{SESSION_COOKIE}={token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age={max_age}"


def clear_session_cookie():
    """Cria o header Set-Cookie para limpar a sessão."""
    return f"{SESSION_COOKIE}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0"


async def get_current_user(db, request):
    """Retorna ê usuárie atual baseade na sessão."""
    token = get_session_token(request)
    if not token:
        return None
    
    session = await get_session(db, token)
    if not session:
        return None
    
    # Verifica se usuárie está banide
    if session.get('is_banned'):
        return None
    
    return {
        'id': session['user_id'],
        'username': session['username'],
        'email': session['email'],
        'is_admin': bool(session.get('is_admin')),
        'is_superadmin': bool(session.get('is_superadmin')),
    }


async def authenticate(db, username_or_email, password):
    """Autentica usuárie e retorna dados se válide."""
    # Tenta buscar por username primeiro, depois por email
    user = await get_user_by_username(db, username_or_email)
    if not user:
        user = await get_user_by_email(db, username_or_email)
    
    if not user:
        return None, "Usuárie não encontrade"
    
    if user.get('is_banned'):
        return None, "Conta banida"
    
    if not verify_password(user['password'], password):
        return None, "Senha incorreta"
    
    return user, None


async def login(db, request, username_or_email, password):
    """Faz login e retorna token de sessão."""
    user, error = await authenticate(db, username_or_email, password)
    if error:
        return None, error
    
    # Extrai informações do request
    user_agent = request.headers.get('User-Agent')
    ip_address = request.headers.get('CF-Connecting-IP') or request.headers.get('X-Forwarded-For')
    
    # Cria sessão
    token = await create_session(db, user['id'], user_agent, ip_address)
    return token, None


async def logout(db, request):
    """Faz logout removendo a sessão."""
    token = get_session_token(request)
    if token:
        await delete_session(db, token)


async def register(db, username, email, password, nome=None):
    """Registra ume nove usuárie."""
    # Validações
    if len(username) < 3:
        return None, "Username deve ter pelo menos 3 caracteres"
    
    if len(password) < 6:
        return None, "Senha deve ter pelo menos 6 caracteres"
    
    if '@' not in email:
        return None, "Email inválido"
    
    # Verifica se username já existe
    existing = await get_user_by_username(db, username)
    if existing:
        return None, "Username já está em uso"
    
    # Verifica se email já existe
    existing = await get_user_by_email(db, email)
    if existing:
        return None, "Email já está cadastrade"
    
    # Cria ume usuárie
    user_id = await create_user(db, username, email, password, nome)
    if not user_id:
        return None, "Erro ao criar usuárie"
    
    return user_id, None


def require_auth(handler):
    """Decorator para rotas que requerem autenticação."""
    async def wrapper(self, request, *args, **kwargs):
        user = await get_current_user(self.env.DB, request)
        if not user:
            return self.redirect('/login')
        kwargs['current_user'] = user
        return await handler(self, request, *args, **kwargs)
    return wrapper


def require_admin(handler):
    """Decorator para rotas que requerem admin."""
    async def wrapper(self, request, *args, **kwargs):
        user = await get_current_user(self.env.DB, request)
        if not user:
            return self.redirect('/login')
        if not user.get('is_admin') and not user.get('is_superadmin'):
            return self.json_response({'error': 'Acesso negado'}, 403)
        kwargs['current_user'] = user
        return await handler(self, request, *args, **kwargs)
    return wrapper
