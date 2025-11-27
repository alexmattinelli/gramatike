# gramatike_d1/db.py
# Database helpers para Cloudflare D1
# Este módulo fornece funções para interagir com o D1 SQLite
#
# NOTA: Renomeado de 'workers/' para 'gramatike_d1/' para evitar conflito
# com o módulo 'workers' built-in do Cloudflare Workers Python.

import json
import sys
import traceback
from datetime import datetime, timedelta
import hashlib
import secrets

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

# ============================================================================
# HELPERS DE DATABASE
# ============================================================================

def row_to_dict(row, columns):
    """Converte uma row do D1 para dicionário."""
    if row is None:
        return None
    return dict(zip(columns, row))


def rows_to_list(rows, columns):
    """Converte múltiplas rows do D1 para lista de dicionários."""
    return [row_to_dict(row, columns) for row in rows]


def safe_dict(result):
    """Converte resultado D1 para dict de forma segura.
    
    Handles JsProxy objects returned by Cloudflare D1 in Pyodide environment.
    The D1 database returns JavaScript objects (JsProxy) that need special
    handling to convert to Python dicts.
    """
    if result is None:
        return None
    
    # Check if it's a JsProxy object (from Pyodide/Cloudflare Workers)
    result_type = type(result).__name__
    
    # Method 1: Try to_py() for JsProxy objects (Pyodide's conversion method)
    if hasattr(result, 'to_py'):
        try:
            converted = result.to_py()
            if isinstance(converted, dict):
                return converted
            # If to_py() returns something else, try dict() on it
            return dict(converted) if converted else None
        except Exception:
            pass  # Fall through to other methods
    
    # Method 2: Try Object.keys() for JavaScript objects
    try:
        from js import Object
        # Get JavaScript object keys
        js_keys = Object.keys(result)
        if js_keys:
            # Convert keys to Python list and build dict
            keys_list = js_keys.to_py() if hasattr(js_keys, 'to_py') else list(js_keys)
            return {k: (result[k].to_py() if hasattr(result[k], 'to_py') else result[k]) for k in keys_list}
    except ImportError:
        pass  # Not in Pyodide environment
    except Exception:
        pass  # Fall through to other methods
    
    # Method 3: Standard dict conversion (works for regular Python objects)
    try:
        converted = dict(result)
        return converted
    except TypeError:
        pass  # Not directly convertible
    except Exception:
        pass
    
    # Method 4: Try keys() method if available
    try:
        if hasattr(result, 'keys'):
            keys = result.keys()
            if hasattr(keys, 'to_py'):
                keys = keys.to_py()
            if keys:
                return {k: (result[k].to_py() if hasattr(result[k], 'to_py') else result[k]) for k in keys}
    except Exception:
        pass
    
    # Method 5: Try iterating as items
    try:
        if hasattr(result, 'items'):
            items = result.items()
            if hasattr(items, 'to_py'):
                items = items.to_py()
            return dict(items)
    except Exception:
        pass
    
    # All methods failed - log warning and return None
    console.warn(f"[safe_dict] Não foi possível converter resultado: type={result_type}")
    return None


def safe_get(result, key, default=None):
    """Safely get a value from a D1 result (handles JsProxy objects).
    
    This is a convenience function for accessing single values from D1 results,
    particularly useful for patterns like: safe_get(result, 'id')
    """
    if result is None:
        return default
    
    # If it's already a dict, just access it
    if isinstance(result, dict):
        return result.get(key, default)
    
    # Try to_py() first for JsProxy
    if hasattr(result, 'to_py'):
        try:
            converted = result.to_py()
            if isinstance(converted, dict):
                return converted.get(key, default)
        except Exception:
            pass
    
    # Try direct access with to_py() on the value
    try:
        value = result[key]
        if hasattr(value, 'to_py'):
            return value.to_py()
        return value
    except (KeyError, TypeError, IndexError):
        pass
    
    # Fallback to safe_dict
    try:
        d = safe_dict(result)
        if d:
            return d.get(key, default)
    except Exception:
        pass
    
    return default


# ============================================================================
# AUTO-INICIALIZAÇÃO DO BANCO DE DADOS
# ============================================================================

# Flag para controlar se já inicializamos o banco nesta execução
_db_initialized = False

async def ensure_database_initialized(db):
    """
    Garante que as tabelas do banco existem e cria um superadmin padrão se necessário.
    Esta função é idempotente - pode ser chamada múltiplas vezes sem problemas.
    """
    global _db_initialized
    if _db_initialized:
        return True
    
    # Use console.log for informational messages
    console.log("[D1 Init] Iniciando verificação do banco de dados...")
    
    try:
        # Criar tabela de usuáries se não existir
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email_confirmed INTEGER DEFAULT 0,
                email_confirmed_at TEXT,
                foto_perfil TEXT DEFAULT 'img/perfil.png',
                genero TEXT,
                pronome TEXT,
                bio TEXT,
                data_nascimento TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                is_admin INTEGER DEFAULT 0,
                is_superadmin INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                banned_at TEXT,
                ban_reason TEXT,
                suspended_until TEXT
            )
        """).run()
        
        # Criar tabela de sessões
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS user_session (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                expires_at TEXT NOT NULL,
                user_agent TEXT,
                ip_address TEXT,
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
            )
        """).run()
        
        # Criar tabela de posts
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS post (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT,
                usuario_id INTEGER,
                conteudo TEXT,
                imagem TEXT,
                data TEXT DEFAULT (datetime('now')),
                is_deleted INTEGER DEFAULT 0,
                deleted_at TEXT,
                deleted_by INTEGER,
                FOREIGN KEY (usuario_id) REFERENCES user(id),
                FOREIGN KEY (deleted_by) REFERENCES user(id)
            )
        """).run()
        
        # Criar tabela de likes
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS post_likes (
                user_id INTEGER NOT NULL,
                post_id INTEGER NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (user_id, post_id),
                FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
            )
        """).run()
        
        # Criar tabela de comentários
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS comentario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                conteudo TEXT,
                post_id INTEGER,
                data TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (usuario_id) REFERENCES user(id),
                FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
            )
        """).run()
        
        # Criar tabela de seguidories
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS seguidories (
                seguidore_id INTEGER NOT NULL,
                seguide_id INTEGER NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (seguidore_id, seguide_id),
                FOREIGN KEY (seguidore_id) REFERENCES user(id) ON DELETE CASCADE,
                FOREIGN KEY (seguide_id) REFERENCES user(id) ON DELETE CASCADE
            )
        """).run()
        
        # Criar tabela de conteúdo educacional
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS edu_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                titulo TEXT NOT NULL,
                resumo TEXT,
                corpo TEXT,
                url TEXT,
                file_path TEXT,
                extra TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                author_id INTEGER,
                topic_id INTEGER,
                FOREIGN KEY (author_id) REFERENCES user(id)
            )
        """).run()
        
        # Criar tabela de dinâmicas
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS dynamic (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                titulo TEXT NOT NULL,
                descricao TEXT,
                config TEXT,
                active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES user(id)
            )
        """).run()
        
        # Criar tabela de respostas de dinâmicas
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS dynamic_response (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dynamic_id INTEGER NOT NULL,
                usuario_id INTEGER,
                payload TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (dynamic_id) REFERENCES dynamic(id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES user(id)
            )
        """).run()
        
        # Criar tabela de tópicos de exercícios
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS exercise_topic (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                descricao TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """).run()
        
        # Criar tabela de questões
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS exercise_question (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id INTEGER NOT NULL,
                section_id INTEGER,
                enunciado TEXT NOT NULL,
                resposta TEXT,
                dificuldade TEXT,
                tipo TEXT,
                opcoes TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (topic_id) REFERENCES exercise_topic(id)
            )
        """).run()
        
        # Criar tabela de palavra do dia
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS palavra_do_dia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                palavra TEXT NOT NULL,
                significado TEXT NOT NULL,
                ordem INTEGER DEFAULT 0,
                ativo INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES user(id)
            )
        """).run()
        
        # Criar tabela de divulgação
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS divulgacao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area TEXT NOT NULL,
                titulo TEXT NOT NULL,
                texto TEXT,
                link TEXT,
                imagem TEXT,
                ordem INTEGER DEFAULT 0,
                ativo INTEGER DEFAULT 1,
                show_on_edu INTEGER DEFAULT 1,
                show_on_index INTEGER DEFAULT 1,
                edu_content_id INTEGER,
                post_id INTEGER,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """).run()
        
        # Criar tabela de novidades
        await db.prepare("""
            CREATE TABLE IF NOT EXISTS edu_novidade (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                link TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                author_id INTEGER,
                FOREIGN KEY (author_id) REFERENCES user(id)
            )
        """).run()
        
        # Verificar se existe superadmin, se não, criar um
        superadmin = await db.prepare(
            "SELECT id FROM user WHERE is_superadmin = 1 LIMIT 1"
        ).first()
        
        # Use console.log for informational messages
        console.log(f"[D1 Init] Superadmin check result: {superadmin}")
        
        if not superadmin:
            # Verificar se o usuário 'gramatike' já existe (sem ser superadmin)
            existing_user = await db.prepare(
                "SELECT id, username, is_superadmin FROM user WHERE username = 'gramatike' LIMIT 1"
            ).first()
            
            if existing_user:
                console.log(f"[D1 Init] Usuário 'gramatike' já existe: {existing_user}")
                # Se existe mas não é superadmin, promover a superadmin
                await db.prepare("""
                    UPDATE user SET is_admin = 1, is_superadmin = 1 WHERE username = 'gramatike'
                """).run()
                console.log("[D1 Init] Usuário 'gramatike' promovido a superadmin!")
            else:
                # Criar senha hasheada para o superadmin
                salt = secrets.token_hex(16)
                password = "GramatikeAdmin2024!"
                hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
                password_hash = f"{salt}:{hashed.hex()}"
                
                try:
                    await db.prepare("""
                        INSERT INTO user (username, email, password, nome, is_admin, is_superadmin, created_at)
                        VALUES (?, ?, ?, ?, 1, 1, datetime('now'))
                    """).bind('gramatike', 'admin@gramatike.com.br', password_hash, 'Gramátike Admin').run()
                    
                    console.log("[D1 Init] Superadmin 'gramatike' criado automaticamente!")
                except Exception as insert_error:
                    # Use console.error for actual errors
                    console.error(f"[D1 Init Error] Falha ao criar superadmin: {insert_error}")
        else:
            console.log("[D1 Init] Superadmin já existe, pulando criação.")
        
        # Verificar quantos usuários existem no banco
        user_count = await db.prepare("SELECT COUNT(*) as count FROM user").first()
        console.log(f"[D1 Init] Total de usuários no banco: {user_count}")
        
        _db_initialized = True
        console.log("[D1 Init] Inicialização concluída com sucesso!")
        return True
        
    except Exception as e:
        # Use console.error for actual errors
        console.error(f"[D1 Init Error] {e}")
        console.error(f"[D1 Init Traceback] {traceback.format_exc()}")
        return False


# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

def hash_password(password):
    """Hash simples de senha usando SHA-256 + salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{hashed.hex()}"


def verify_password(stored_hash, password):
    """Verifica se a senha corresponde ao hash armazenado.
    
    Suporta três formatos de hash:
    1. Formato D1 simples: "salt:hash" (usado pelo gramatike_d1)
    2. Formato Werkzeug pbkdf2: "pbkdf2:sha256:iterations$salt$hash"
    3. Formato Werkzeug scrypt: "scrypt:n:r:p$salt$hash" (padrão atual do Werkzeug)
    """
    if not stored_hash or not password:
        return False
    
    try:
        # Converte bytes para string se necessário (D1 pode retornar bytes)
        if isinstance(stored_hash, bytes):
            stored_hash = stored_hash.decode('utf-8')
        if isinstance(password, bytes):
            password = password.decode('utf-8')
        
        # Tenta formato D1 simples primeiro (salt:hash)
        if stored_hash.count(':') == 1 and '$' not in stored_hash:
            salt, hashed = stored_hash.split(':')
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return new_hash.hex() == hashed
        
        # Tenta formato Werkzeug (pbkdf2:sha256:iterations$salt$hash ou scrypt:...)
        # Primeiro verifica se werkzeug está disponível
        try:
            from werkzeug.security import check_password_hash as _werkzeug_check
            werkzeug_available = True
        except ImportError:
            werkzeug_available = False
        
        if werkzeug_available:
            try:
                return _werkzeug_check(stored_hash, password)
            except Exception:
                # Werkzeug falhou ao verificar, tenta fallback manual
                pass
        
        # Fallback: parse manual do formato pbkdf2 quando werkzeug não está disponível
        if stored_hash.startswith('pbkdf2:sha256:'):
            # Formato: pbkdf2:sha256:iterations$salt$hash
            parts = stored_hash.split('$')
            if len(parts) == 3:
                method_parts = parts[0].split(':')
                if len(method_parts) >= 3:
                    try:
                        iterations = int(method_parts[2])
                    except ValueError:
                        return False  # Formato de hash inválido
                    salt = parts[1]
                    expected_hash = parts[2]
                    new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), iterations)
                    return new_hash.hex() == expected_hash
        
        # Fallback: parse manual do formato scrypt quando werkzeug não está disponível
        # Formato: scrypt:n:r:p$salt$hash (ex: scrypt:32768:8:1$salt$hash)
        if stored_hash.startswith('scrypt:'):
            parts = stored_hash.split('$')
            if len(parts) == 3:
                method_parts = parts[0].split(':')
                # Werkzeug scrypt format has exactly 4 parts: scrypt, n, r, p
                if len(method_parts) == 4:
                    try:
                        n = int(method_parts[1])  # CPU/memory cost parameter
                        r = int(method_parts[2])  # Block size parameter
                        p = int(method_parts[3])  # Parallelization parameter
                    except ValueError:
                        return False  # Formato de hash inválido
                    
                    # Validate scrypt parameters to prevent DoS attacks
                    # Werkzeug defaults: n=32768, r=8, p=1
                    # Allow reasonable ranges: n <= 2^20 (1M), r <= 32, p <= 16
                    if n <= 0 or n > 1048576 or r <= 0 or r > 32 or p <= 0 or p > 16:
                        return False  # Parâmetros scrypt inválidos ou suspeitos
                    
                    salt = parts[1]
                    expected_hash = parts[2]
                    # Werkzeug uses dklen=64 (512 bits) for scrypt hashes
                    new_hash = hashlib.scrypt(
                        password.encode(), 
                        salt=salt.encode(), 
                        n=n, r=r, p=p, 
                        dklen=64
                    )
                    return new_hash.hex() == expected_hash
        
        return False
    except Exception:
        # Falha silenciosa para evitar vazamento de informações
        return False


def generate_session_token():
    """Gera um token de sessão seguro."""
    return secrets.token_urlsafe(32)


# ============================================================================
# QUERIES - USUÁRIOS
# ============================================================================

async def get_user_by_id(db, user_id):
    """Busca ê usuárie por ID."""
    result = await db.prepare(
        "SELECT * FROM user WHERE id = ?"
    ).bind(user_id).first()
    if result:
        return safe_dict(result)
    return None


async def get_user_by_username(db, username):
    """Busca ê usuárie por username."""
    try:
        result = await db.prepare(
            "SELECT * FROM user WHERE username = ?"
        ).bind(username).first()
        # Use console.log for debug/info messages
        console.log(f"[get_user_by_username] Query result for '{username}': {result}, type: {type(result)}")
        if result:
            converted = safe_dict(result)
            console.log(f"[get_user_by_username] safe_dict result: {converted is not None}")
            return converted
        return None
    except Exception as e:
        # Use console.error for actual errors
        console.error(f"[get_user_by_username] Error: {e}")
        return None


async def get_user_by_email(db, email):
    """Busca ê usuárie por email."""
    result = await db.prepare(
        "SELECT * FROM user WHERE email = ?"
    ).bind(email).first()
    if result:
        return safe_dict(result)
    return None


async def create_user(db, username, email, password, nome=None):
    """Cria ume nove usuárie."""
    hashed = hash_password(password)
    result = await db.prepare("""
        INSERT INTO user (username, email, password, nome, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        RETURNING id
    """).bind(username, email, hashed, nome).first()
    return safe_get(result, 'id')


async def update_user_profile(db, user_id, **kwargs):
    """Atualiza o perfil de usuárie."""
    allowed = ['nome', 'bio', 'genero', 'pronome', 'foto_perfil', 'data_nascimento']
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not updates:
        return False
    
    set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [user_id]
    
    await db.prepare(f"""
        UPDATE user SET {set_clause} WHERE id = ?
    """).bind(*values).run()
    return True


# ============================================================================
# QUERIES - SESSÕES
# ============================================================================

async def create_session(db, user_id, user_agent=None, ip_address=None):
    """Cria uma nova sessão de usuárie."""
    token = generate_session_token()
    expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()
    
    await db.prepare("""
        INSERT INTO user_session (user_id, token, expires_at, user_agent, ip_address)
        VALUES (?, ?, ?, ?, ?)
    """).bind(user_id, token, expires_at, user_agent, ip_address).run()
    
    return token


async def get_session(db, token):
    """Busca sessão pelo token."""
    result = await db.prepare("""
        SELECT s.*, u.username, u.email, u.is_admin, u.is_superadmin, u.is_banned
        FROM user_session s
        JOIN user u ON s.user_id = u.id
        WHERE s.token = ? AND s.expires_at > datetime('now')
    """).bind(token).first()
    if result:
        return safe_dict(result)
    return None


async def delete_session(db, token):
    """Remove uma sessão (logout)."""
    await db.prepare(
        "DELETE FROM user_session WHERE token = ?"
    ).bind(token).run()


async def cleanup_expired_sessions(db):
    """Remove sessões expiradas."""
    await db.prepare(
        "DELETE FROM user_session WHERE expires_at < datetime('now')"
    ).run()


# ============================================================================
# QUERIES - POSTS
# ============================================================================

async def get_posts(db, page=1, per_page=20, user_id=None, include_deleted=False):
    """Lista posts com paginação."""
    offset = (page - 1) * per_page
    
    # Build query with proper parameterization
    if user_id and not include_deleted:
        result = await db.prepare("""
            SELECT p.*, u.username, u.foto_perfil,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                   (SELECT COUNT(*) FROM comentario WHERE post_id = p.id) as comment_count
            FROM post p
            LEFT JOIN user u ON p.usuario_id = u.id
            WHERE p.is_deleted = 0 AND p.usuario_id = ?
            ORDER BY p.data DESC
            LIMIT ? OFFSET ?
        """).bind(user_id, per_page, offset).all()
    elif user_id:
        result = await db.prepare("""
            SELECT p.*, u.username, u.foto_perfil,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                   (SELECT COUNT(*) FROM comentario WHERE post_id = p.id) as comment_count
            FROM post p
            LEFT JOIN user u ON p.usuario_id = u.id
            WHERE p.usuario_id = ?
            ORDER BY p.data DESC
            LIMIT ? OFFSET ?
        """).bind(user_id, per_page, offset).all()
    elif not include_deleted:
        result = await db.prepare("""
            SELECT p.*, u.username, u.foto_perfil,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                   (SELECT COUNT(*) FROM comentario WHERE post_id = p.id) as comment_count
            FROM post p
            LEFT JOIN user u ON p.usuario_id = u.id
            WHERE p.is_deleted = 0
            ORDER BY p.data DESC
            LIMIT ? OFFSET ?
        """).bind(per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT p.*, u.username, u.foto_perfil,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                   (SELECT COUNT(*) FROM comentario WHERE post_id = p.id) as comment_count
            FROM post p
            LEFT JOIN user u ON p.usuario_id = u.id
            ORDER BY p.data DESC
            LIMIT ? OFFSET ?
        """).bind(per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_post_by_id(db, post_id):
    """Busca post por ID."""
    result = await db.prepare("""
        SELECT p.*, u.username, u.foto_perfil,
               (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
               (SELECT COUNT(*) FROM comentario WHERE post_id = p.id) as comment_count
        FROM post p
        LEFT JOIN user u ON p.usuario_id = u.id
        WHERE p.id = ?
    """).bind(post_id).first()
    if result:
        return safe_dict(result)
    return None


async def create_post(db, usuario_id, conteudo, imagem=None):
    """Cria um novo post."""
    result = await db.prepare("""
        INSERT INTO post (usuario_id, usuario, conteudo, imagem, data)
        SELECT ?, username, ?, ?, datetime('now')
        FROM user WHERE id = ?
        RETURNING id
    """).bind(usuario_id, conteudo, imagem, usuario_id).first()
    return safe_get(result, 'id')


async def delete_post(db, post_id, deleted_by=None):
    """Soft delete de um post."""
    await db.prepare("""
        UPDATE post SET is_deleted = 1, deleted_at = datetime('now'), deleted_by = ?
        WHERE id = ?
    """).bind(deleted_by, post_id).run()


async def like_post(db, user_id, post_id):
    """Curte um post."""
    try:
        await db.prepare("""
            INSERT INTO post_likes (user_id, post_id) VALUES (?, ?)
        """).bind(user_id, post_id).run()
        return True
    except:
        return False


async def unlike_post(db, user_id, post_id):
    """Remove curtida de um post."""
    await db.prepare("""
        DELETE FROM post_likes WHERE user_id = ? AND post_id = ?
    """).bind(user_id, post_id).run()


async def has_liked(db, user_id, post_id):
    """Verifica se usuárie curtiu o post."""
    result = await db.prepare("""
        SELECT 1 FROM post_likes WHERE user_id = ? AND post_id = ?
    """).bind(user_id, post_id).first()
    return result is not None


# ============================================================================
# QUERIES - COMENTÁRIOS
# ============================================================================

async def get_comments(db, post_id, page=1, per_page=50):
    """Lista comentários de um post."""
    offset = (page - 1) * per_page
    
    result = await db.prepare("""
        SELECT c.*, u.username, u.foto_perfil
        FROM comentario c
        LEFT JOIN user u ON c.usuario_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.data ASC
        LIMIT ? OFFSET ?
    """).bind(post_id, per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def create_comment(db, post_id, usuario_id, conteudo):
    """Cria um novo comentário."""
    result = await db.prepare("""
        INSERT INTO comentario (post_id, usuario_id, conteudo, data)
        VALUES (?, ?, ?, datetime('now'))
        RETURNING id
    """).bind(post_id, usuario_id, conteudo).first()
    return safe_get(result, 'id')


# ============================================================================
# QUERIES - SEGUIDORIES
# ============================================================================

async def follow_user(db, seguidore_id, seguide_id):
    """Seguir ume usuárie."""
    if seguidore_id == seguide_id:
        return False
    try:
        await db.prepare("""
            INSERT INTO seguidories (seguidore_id, seguide_id) VALUES (?, ?)
        """).bind(seguidore_id, seguide_id).run()
        return True
    except:
        return False


async def unfollow_user(db, seguidore_id, seguide_id):
    """Deixar de seguir ume usuárie."""
    await db.prepare("""
        DELETE FROM seguidories WHERE seguidore_id = ? AND seguide_id = ?
    """).bind(seguidore_id, seguide_id).run()


async def is_following(db, seguidore_id, seguide_id):
    """Verifica se está seguindo."""
    result = await db.prepare("""
        SELECT 1 FROM seguidories WHERE seguidore_id = ? AND seguide_id = ?
    """).bind(seguidore_id, seguide_id).first()
    return result is not None


async def get_followers(db, user_id):
    """Lista seguidories de usuárie."""
    result = await db.prepare("""
        SELECT u.id, u.username, u.nome, u.foto_perfil
        FROM seguidories s
        JOIN user u ON s.seguidore_id = u.id
        WHERE s.seguide_id = ?
    """).bind(user_id).all()
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_following(db, user_id):
    """Lista quem ê usuárie segue."""
    result = await db.prepare("""
        SELECT u.id, u.username, u.nome, u.foto_perfil
        FROM seguidories s
        JOIN user u ON s.seguide_id = u.id
        WHERE s.seguidore_id = ?
    """).bind(user_id).all()
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - CONTEÚDO EDUCACIONAL
# ============================================================================

async def get_edu_contents(db, tipo=None, page=1, per_page=20):
    """Lista conteúdos educacionais."""
    offset = (page - 1) * per_page
    
    if tipo:
        result = await db.prepare("""
            SELECT e.*, u.username as author_name, t.nome as topic_name
            FROM edu_content e
            LEFT JOIN user u ON e.author_id = u.id
            LEFT JOIN edu_topic t ON e.topic_id = t.id
            WHERE tipo = ?
            ORDER BY e.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(tipo, per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT e.*, u.username as author_name, t.nome as topic_name
            FROM edu_content e
            LEFT JOIN user u ON e.author_id = u.id
            LEFT JOIN edu_topic t ON e.topic_id = t.id
            ORDER BY e.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_edu_content_by_id(db, content_id):
    """Busca conteúdo educacional por ID."""
    result = await db.prepare("""
        SELECT e.*, u.username as author_name, t.nome as topic_name
        FROM edu_content e
        LEFT JOIN user u ON e.author_id = u.id
        LEFT JOIN edu_topic t ON e.topic_id = t.id
        WHERE e.id = ?
    """).bind(content_id).first()
    if result:
        return safe_dict(result)
    return None


async def search_edu_contents(db, query, tipo=None):
    """Pesquisa conteúdos educacionais."""
    search_term = f"%{query}%"
    
    if tipo:
        result = await db.prepare("""
            SELECT e.*, u.username as author_name
            FROM edu_content e
            LEFT JOIN user u ON e.author_id = u.id
            WHERE (e.titulo LIKE ? OR e.resumo LIKE ? OR e.corpo LIKE ?)
            AND tipo = ?
            ORDER BY e.created_at DESC
            LIMIT 50
        """).bind(search_term, search_term, search_term, tipo).all()
    else:
        result = await db.prepare("""
            SELECT e.*, u.username as author_name
            FROM edu_content e
            LEFT JOIN user u ON e.author_id = u.id
            WHERE (e.titulo LIKE ? OR e.resumo LIKE ? OR e.corpo LIKE ?)
            ORDER BY e.created_at DESC
            LIMIT 50
        """).bind(search_term, search_term, search_term).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - EXERCÍCIOS
# ============================================================================

async def get_exercise_topics(db):
    """Lista tópicos de exercícios."""
    result = await db.prepare("""
        SELECT t.*, 
               (SELECT COUNT(*) FROM exercise_question WHERE topic_id = t.id) as question_count
        FROM exercise_topic t
        ORDER BY t.nome
    """).all()
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_exercise_questions(db, topic_id=None, section_id=None):
    """Lista questões de exercícios."""
    if topic_id and section_id:
        result = await db.prepare("""
            SELECT q.*, t.nome as topic_name, s.nome as section_name
            FROM exercise_question q
            LEFT JOIN exercise_topic t ON q.topic_id = t.id
            LEFT JOIN exercise_section s ON q.section_id = s.id
            WHERE q.topic_id = ? AND q.section_id = ?
            ORDER BY q.created_at DESC
        """).bind(topic_id, section_id).all()
    elif topic_id:
        result = await db.prepare("""
            SELECT q.*, t.nome as topic_name, s.nome as section_name
            FROM exercise_question q
            LEFT JOIN exercise_topic t ON q.topic_id = t.id
            LEFT JOIN exercise_section s ON q.section_id = s.id
            WHERE q.topic_id = ?
            ORDER BY q.created_at DESC
        """).bind(topic_id).all()
    elif section_id:
        result = await db.prepare("""
            SELECT q.*, t.nome as topic_name, s.nome as section_name
            FROM exercise_question q
            LEFT JOIN exercise_topic t ON q.topic_id = t.id
            LEFT JOIN exercise_section s ON q.section_id = s.id
            WHERE q.section_id = ?
            ORDER BY q.created_at DESC
        """).bind(section_id).all()
    else:
        result = await db.prepare("""
            SELECT q.*, t.nome as topic_name, s.nome as section_name
            FROM exercise_question q
            LEFT JOIN exercise_topic t ON q.topic_id = t.id
            LEFT JOIN exercise_section s ON q.section_id = s.id
            ORDER BY q.created_at DESC
        """).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - DINÂMICAS
# ============================================================================

async def get_dynamics(db, active_only=True):
    """Lista dinâmicas."""
    if active_only:
        result = await db.prepare("""
            SELECT d.*, u.username as author_name,
                   (SELECT COUNT(*) FROM dynamic_response WHERE dynamic_id = d.id) as response_count
            FROM dynamic d
            LEFT JOIN user u ON d.created_by = u.id
            WHERE active = 1
            ORDER BY d.created_at DESC
        """).all()
    else:
        result = await db.prepare("""
            SELECT d.*, u.username as author_name,
                   (SELECT COUNT(*) FROM dynamic_response WHERE dynamic_id = d.id) as response_count
            FROM dynamic d
            LEFT JOIN user u ON d.created_by = u.id
            ORDER BY d.created_at DESC
        """).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_dynamic_by_id(db, dynamic_id):
    """Busca dinâmica por ID."""
    result = await db.prepare("""
        SELECT d.*, u.username as author_name
        FROM dynamic d
        LEFT JOIN user u ON d.created_by = u.id
        WHERE d.id = ?
    """).bind(dynamic_id).first()
    if result:
        return safe_dict(result)
    return None


async def get_dynamic_responses(db, dynamic_id):
    """Lista respostas de uma dinâmica."""
    result = await db.prepare("""
        SELECT r.*, u.username
        FROM dynamic_response r
        LEFT JOIN user u ON r.usuario_id = u.id
        WHERE r.dynamic_id = ?
        ORDER BY r.created_at DESC
    """).bind(dynamic_id).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def submit_dynamic_response(db, dynamic_id, usuario_id, payload):
    """Submete resposta para uma dinâmica."""
    payload_json = json.dumps(payload) if isinstance(payload, dict) else payload
    
    result = await db.prepare("""
        INSERT INTO dynamic_response (dynamic_id, usuario_id, payload)
        VALUES (?, ?, ?)
        RETURNING id
    """).bind(dynamic_id, usuario_id, payload_json).first()
    return safe_get(result, 'id')


# ============================================================================
# QUERIES - PALAVRAS DO DIA
# ============================================================================

async def get_palavras_do_dia(db, ativas_only=True):
    """Lista palavras do dia."""
    if ativas_only:
        result = await db.prepare("""
            SELECT p.*, 
                   (SELECT COUNT(*) FROM palavra_do_dia_interacao WHERE palavra_id = p.id) as interacao_count
            FROM palavra_do_dia p
            WHERE ativo = 1
            ORDER BY p.ordem, p.created_at DESC
        """).all()
    else:
        result = await db.prepare("""
            SELECT p.*, 
                   (SELECT COUNT(*) FROM palavra_do_dia_interacao WHERE palavra_id = p.id) as interacao_count
            FROM palavra_do_dia p
            ORDER BY p.ordem, p.created_at DESC
        """).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_palavra_do_dia_atual(db):
    """Busca a palavra do dia atual (primeira ativa)."""
    result = await db.prepare("""
        SELECT * FROM palavra_do_dia 
        WHERE ativo = 1 
        ORDER BY ordem, created_at DESC 
        LIMIT 1
    """).first()
    if result:
        return safe_dict(result)
    return None


# ============================================================================
# QUERIES - DIVULGAÇÃO / NOVIDADES
# ============================================================================

async def get_divulgacoes(db, area=None, show_on_edu=None, show_on_index=None):
    """Lista divulgações."""
    # Build query based on conditions - using parameterized queries
    if area and show_on_edu and show_on_index:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND area = ? AND show_on_edu = 1 AND show_on_index = 1
            ORDER BY ordem, created_at DESC
        """).bind(area).all()
    elif area and show_on_edu:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND area = ? AND show_on_edu = 1
            ORDER BY ordem, created_at DESC
        """).bind(area).all()
    elif area and show_on_index:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND area = ? AND show_on_index = 1
            ORDER BY ordem, created_at DESC
        """).bind(area).all()
    elif show_on_edu and show_on_index:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND show_on_edu = 1 AND show_on_index = 1
            ORDER BY ordem, created_at DESC
        """).all()
    elif area:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND area = ?
            ORDER BY ordem, created_at DESC
        """).bind(area).all()
    elif show_on_edu:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND show_on_edu = 1
            ORDER BY ordem, created_at DESC
        """).all()
    elif show_on_index:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND show_on_index = 1
            ORDER BY ordem, created_at DESC
        """).all()
    else:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1
            ORDER BY ordem, created_at DESC
        """).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_novidades(db, limit=5):
    """Lista últimas novidades."""
    result = await db.prepare("""
        SELECT n.*, u.username as author_name
        FROM edu_novidade n
        LEFT JOIN user u ON n.author_id = u.id
        ORDER BY n.created_at DESC
        LIMIT ?
    """).bind(limit).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - TOKENS DE EMAIL (Verificação e Recuperação de Senha)
# ============================================================================

def generate_email_token():
    """Gera um token de email seguro."""
    return secrets.token_urlsafe(32)


async def create_email_token(db, usuario_id, tipo, expires_hours=24, novo_email=None):
    """Cria um token de verificação/recuperação."""
    token = generate_email_token()
    expires_at = (datetime.utcnow() + timedelta(hours=expires_hours)).isoformat()
    
    if novo_email:
        await db.prepare("""
            INSERT INTO email_token (usuario_id, token, tipo, novo_email, expires_at)
            VALUES (?, ?, ?, ?, ?)
        """).bind(usuario_id, token, tipo, novo_email, expires_at).run()
    else:
        await db.prepare("""
            INSERT INTO email_token (usuario_id, token, tipo, expires_at)
            VALUES (?, ?, ?, ?)
        """).bind(usuario_id, token, tipo, expires_at).run()
    
    return token


async def verify_email_token(db, token, tipo):
    """Verifica e retorna dados do token se válido."""
    result = await db.prepare("""
        SELECT * FROM email_token
        WHERE token = ? AND tipo = ? AND used = 0 AND expires_at > datetime('now')
    """).bind(token, tipo).first()
    
    if result:
        return safe_dict(result)
    return None


async def use_email_token(db, token):
    """Marca token como usado."""
    await db.prepare("""
        UPDATE email_token SET used = 1, used_at = datetime('now')
        WHERE token = ?
    """).bind(token).run()


async def confirm_user_email(db, usuario_id):
    """Confirma o email de usuárie."""
    await db.prepare("""
        UPDATE user SET email_confirmed = 1, email_confirmed_at = datetime('now')
        WHERE id = ?
    """).bind(usuario_id).run()


async def update_user_password(db, usuario_id, new_password):
    """Atualiza a senha de usuárie."""
    hashed = hash_password(new_password)
    await db.prepare("""
        UPDATE user SET password = ?
        WHERE id = ?
    """).bind(hashed, usuario_id).run()


async def update_user_email(db, usuario_id, new_email):
    """Atualiza o email de usuárie."""
    await db.prepare("""
        UPDATE user SET email = ?, email_confirmed = 0
        WHERE id = ?
    """).bind(new_email, usuario_id).run()


# ============================================================================
# QUERIES - NOTIFICAÇÕES
# ============================================================================

async def create_notification(db, usuario_id, tipo, titulo=None, mensagem=None, link=None,
                              from_usuario_id=None, post_id=None, comentario_id=None):
    """Cria uma notificação para usuárie."""
    result = await db.prepare("""
        INSERT INTO notification 
        (usuario_id, tipo, titulo, mensagem, link, from_usuario_id, post_id, comentario_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING id
    """).bind(usuario_id, tipo, titulo, mensagem, link, 
              from_usuario_id, post_id, comentario_id).first()
    return safe_get(result, 'id')


async def get_notifications(db, usuario_id, apenas_nao_lidas=False, page=1, per_page=20):
    """Lista notificações de usuárie."""
    offset = (page - 1) * per_page
    
    if apenas_nao_lidas:
        result = await db.prepare("""
            SELECT n.*, u.username as from_username, u.foto_perfil as from_foto
            FROM notification n
            LEFT JOIN user u ON n.from_usuario_id = u.id
            WHERE n.usuario_id = ? AND n.lida = 0
            ORDER BY n.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(usuario_id, per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT n.*, u.username as from_username, u.foto_perfil as from_foto
            FROM notification n
            LEFT JOIN user u ON n.from_usuario_id = u.id
            WHERE n.usuario_id = ?
            ORDER BY n.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(usuario_id, per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def count_unread_notifications(db, usuario_id):
    """Conta notificações não lidas de usuárie."""
    result = await db.prepare("""
        SELECT COUNT(*) as count FROM notification
        WHERE usuario_id = ? AND lida = 0
    """).bind(usuario_id).first()
    return safe_get(result, 'count', 0)


async def mark_notification_read(db, notification_id, usuario_id):
    """Marca notificação como lida."""
    await db.prepare("""
        UPDATE notification SET lida = 1
        WHERE id = ? AND usuario_id = ?
    """).bind(notification_id, usuario_id).run()


async def mark_all_notifications_read(db, usuario_id):
    """Marca todas as notificações como lidas."""
    await db.prepare("""
        UPDATE notification SET lida = 1
        WHERE usuario_id = ? AND lida = 0
    """).bind(usuario_id).run()


# ============================================================================
# QUERIES - AMIGUES
# ============================================================================

async def send_friend_request(db, solicitante_id, destinatarie_id):
    """Envia pedido de amizade."""
    # Verifica se já existe relação
    existing = await db.prepare("""
        SELECT * FROM amizade
        WHERE (usuarie1_id = ? AND usuarie2_id = ?)
           OR (usuarie1_id = ? AND usuarie2_id = ?)
    """).bind(solicitante_id, destinatarie_id, destinatarie_id, solicitante_id).first()
    
    if existing:
        return None, "Já existe uma solicitação de amizade"
    
    # Cria solicitação
    result = await db.prepare("""
        INSERT INTO amizade (usuarie1_id, usuarie2_id, solicitante_id, status)
        VALUES (?, ?, ?, 'pendente')
        RETURNING id
    """).bind(solicitante_id, destinatarie_id, solicitante_id).first()
    
    # Notifica destinatárie
    await create_notification(db, destinatarie_id, 'amizade_pedido',
                              titulo='Novo pedido de amizade',
                              from_usuario_id=solicitante_id)
    
    return safe_get(result, 'id'), None


async def respond_friend_request(db, amizade_id, usuario_id, aceitar=True):
    """Responde a pedido de amizade."""
    # Verifica se o pedido existe e é para este usuárie
    amizade = await db.prepare("""
        SELECT * FROM amizade
        WHERE id = ? AND status = 'pendente'
        AND (usuarie1_id = ? OR usuarie2_id = ?)
        AND solicitante_id != ?
    """).bind(amizade_id, usuario_id, usuario_id, usuario_id).first()
    
    if not amizade:
        return False, "Pedido não encontrado"
    
    status = 'aceita' if aceitar else 'recusada'
    await db.prepare("""
        UPDATE amizade SET status = ?, updated_at = datetime('now')
        WHERE id = ?
    """).bind(status, amizade_id).run()
    
    # Notifica solicitante
    solicitante_id = amizade['solicitante_id']
    if aceitar:
        await create_notification(db, solicitante_id, 'amizade_aceita',
                                  titulo='Pedido de amizade aceito!',
                                  from_usuario_id=usuario_id)
    
    return True, None


async def get_amigues(db, usuario_id):
    """Lista amigues de usuárie (amizades aceitas)."""
    result = await db.prepare("""
        SELECT u.id, u.username, u.nome, u.foto_perfil, a.created_at as amigues_desde
        FROM amizade a
        JOIN user u ON (
            (a.usuarie1_id = ? AND a.usuarie2_id = u.id)
            OR (a.usuarie2_id = ? AND a.usuarie1_id = u.id)
        )
        WHERE a.status = 'aceita'
        ORDER BY u.nome, u.username
    """).bind(usuario_id, usuario_id).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_pending_friend_requests(db, usuario_id):
    """Lista pedidos de amizade pendentes recebidos."""
    result = await db.prepare("""
        SELECT a.*, u.username, u.nome, u.foto_perfil
        FROM amizade a
        JOIN user u ON a.solicitante_id = u.id
        WHERE (a.usuarie1_id = ? OR a.usuarie2_id = ?)
        AND a.status = 'pendente'
        AND a.solicitante_id != ?
        ORDER BY a.created_at DESC
    """).bind(usuario_id, usuario_id, usuario_id).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def are_amigues(db, usuarie1_id, usuarie2_id):
    """Verifica se dois usuáries são amigues."""
    result = await db.prepare("""
        SELECT 1 FROM amizade
        WHERE ((usuarie1_id = ? AND usuarie2_id = ?)
            OR (usuarie1_id = ? AND usuarie2_id = ?))
        AND status = 'aceita'
    """).bind(usuarie1_id, usuarie2_id, usuarie2_id, usuarie1_id).first()
    return result is not None


async def remove_amizade(db, usuario_id, amigue_id):
    """Remove amizade."""
    await db.prepare("""
        DELETE FROM amizade
        WHERE ((usuarie1_id = ? AND usuarie2_id = ?)
            OR (usuarie1_id = ? AND usuarie2_id = ?))
        AND status = 'aceita'
    """).bind(usuario_id, amigue_id, amigue_id, usuario_id).run()


# ============================================================================
# QUERIES - DENÚNCIAS
# ============================================================================

async def create_report(db, post_id, usuario_id, motivo, category=None):
    """Cria uma denúncia de post."""
    result = await db.prepare("""
        INSERT INTO report (post_id, usuario_id, motivo, category)
        VALUES (?, ?, ?, ?)
        RETURNING id
    """).bind(post_id, usuario_id, motivo, category).first()
    return safe_get(result, 'id')


async def get_reports(db, apenas_pendentes=True, page=1, per_page=20):
    """Lista denúncias (para admin)."""
    offset = (page - 1) * per_page
    
    if apenas_pendentes:
        result = await db.prepare("""
            SELECT r.*, p.conteudo as post_conteudo, u.username as reporter_username
            FROM report r
            LEFT JOIN post p ON r.post_id = p.id
            LEFT JOIN user u ON r.usuario_id = u.id
            WHERE r.resolved = 0
            ORDER BY r.data DESC
            LIMIT ? OFFSET ?
        """).bind(per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT r.*, p.conteudo as post_conteudo, u.username as reporter_username
            FROM report r
            LEFT JOIN post p ON r.post_id = p.id
            LEFT JOIN user u ON r.usuario_id = u.id
            ORDER BY r.data DESC
            LIMIT ? OFFSET ?
        """).bind(per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def resolve_report(db, report_id, resolver_id=None):
    """Resolve uma denúncia."""
    await db.prepare("""
        UPDATE report SET resolved = 1, resolved_at = datetime('now')
        WHERE id = ?
    """).bind(report_id).run()


async def count_pending_reports(db):
    """Conta denúncias pendentes."""
    result = await db.prepare("""
        SELECT COUNT(*) as count FROM report WHERE resolved = 0
    """).first()
    return safe_get(result, 'count', 0)


# ============================================================================
# QUERIES - SUPORTE/TICKETS
# ============================================================================

async def create_support_ticket(db, mensagem, usuario_id=None, nome=None, email=None):
    """Cria um ticket de suporte."""
    result = await db.prepare("""
        INSERT INTO support_ticket (usuario_id, nome, email, mensagem)
        VALUES (?, ?, ?, ?)
        RETURNING id
    """).bind(usuario_id, nome, email, mensagem).first()
    return safe_get(result, 'id')


async def get_support_tickets(db, status=None, page=1, per_page=20):
    """Lista tickets de suporte (para admin)."""
    offset = (page - 1) * per_page
    
    if status:
        result = await db.prepare("""
            SELECT t.*, u.username
            FROM support_ticket t
            LEFT JOIN user u ON t.usuario_id = u.id
            WHERE t.status = ?
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(status, per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT t.*, u.username
            FROM support_ticket t
            LEFT JOIN user u ON t.usuario_id = u.id
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_user_tickets(db, usuario_id):
    """Lista tickets de usuárie."""
    result = await db.prepare("""
        SELECT * FROM support_ticket
        WHERE usuario_id = ?
        ORDER BY created_at DESC
    """).bind(usuario_id).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def respond_ticket(db, ticket_id, resposta):
    """Responde a um ticket de suporte."""
    await db.prepare("""
        UPDATE support_ticket 
        SET resposta = ?, status = 'respondido', updated_at = datetime('now')
        WHERE id = ?
    """).bind(resposta, ticket_id).run()


async def close_ticket(db, ticket_id):
    """Fecha um ticket de suporte."""
    await db.prepare("""
        UPDATE support_ticket 
        SET status = 'fechado', updated_at = datetime('now')
        WHERE id = ?
    """).bind(ticket_id).run()


# ============================================================================
# QUERIES - DIVULGAÇÃO/PROMOÇÕES
# ============================================================================

async def create_divulgacao(db, area, titulo, texto=None, link=None, imagem=None, 
                            show_on_edu=True, show_on_index=True, author_id=None):
    """Cria uma divulgação."""
    # Nota: A tabela divulgacao não tem coluna author_id diretamente, 
    # mas podemos vincular via edu_content_id ou post_id se necessário
    result = await db.prepare("""
        INSERT INTO divulgacao (area, titulo, texto, link, imagem, show_on_edu, show_on_index)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        RETURNING id
    """).bind(area, titulo, texto, link, imagem, 
              1 if show_on_edu else 0, 1 if show_on_index else 0).first()
    return safe_get(result, 'id')


async def update_divulgacao(db, divulgacao_id, titulo=None, texto=None, link=None, 
                            imagem=None, ativo=None, ordem=None, 
                            show_on_edu=None, show_on_index=None):
    """Atualiza uma divulgação com parâmetros explícitos (evita SQL injection)."""
    # Construir updates de forma segura
    updates = []
    values = []
    
    if titulo is not None:
        updates.append("titulo = ?")
        values.append(titulo)
    if texto is not None:
        updates.append("texto = ?")
        values.append(texto)
    if link is not None:
        updates.append("link = ?")
        values.append(link)
    if imagem is not None:
        updates.append("imagem = ?")
        values.append(imagem)
    if ativo is not None:
        updates.append("ativo = ?")
        values.append(1 if ativo else 0)
    if ordem is not None:
        updates.append("ordem = ?")
        values.append(ordem)
    if show_on_edu is not None:
        updates.append("show_on_edu = ?")
        values.append(1 if show_on_edu else 0)
    if show_on_index is not None:
        updates.append("show_on_index = ?")
        values.append(1 if show_on_index else 0)
    
    if not updates:
        return False
    
    updates.append("updated_at = datetime('now')")
    values.append(divulgacao_id)
    
    set_clause = ", ".join(updates)
    
    await db.prepare(f"""
        UPDATE divulgacao SET {set_clause}
        WHERE id = ?
    """).bind(*values).run()
    return True


async def delete_divulgacao(db, divulgacao_id):
    """Remove uma divulgação."""
    await db.prepare("""
        DELETE FROM divulgacao WHERE id = ?
    """).bind(divulgacao_id).run()


# ============================================================================
# QUERIES - UPLOAD DE IMAGENS
# ============================================================================

async def save_upload(db, usuario_id, tipo, path, filename=None, content_type=None, size=None):
    """Registra um upload de imagem."""
    result = await db.prepare("""
        INSERT INTO upload (usuario_id, tipo, path, filename, content_type, size)
        VALUES (?, ?, ?, ?, ?, ?)
        RETURNING id
    """).bind(usuario_id, tipo, path, filename, content_type, size).first()
    return safe_get(result, 'id')


async def get_user_uploads(db, usuario_id, tipo=None):
    """Lista uploads de usuárie."""
    if tipo:
        result = await db.prepare("""
            SELECT * FROM upload
            WHERE usuario_id = ? AND tipo = ?
            ORDER BY created_at DESC
        """).bind(usuario_id, tipo).all()
    else:
        result = await db.prepare("""
            SELECT * FROM upload
            WHERE usuario_id = ?
            ORDER BY created_at DESC
        """).bind(usuario_id).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - ADMIN
# ============================================================================

async def get_all_usuaries(db, page=1, per_page=20, search=None):
    """Lista todes usuáries (para admin)."""
    offset = (page - 1) * per_page
    
    if search:
        search_term = f"%{search}%"
        result = await db.prepare("""
            SELECT id, username, nome, email, foto_perfil, is_admin, is_superadmin, 
                   is_banned, created_at, email_confirmed
            FROM user
            WHERE username LIKE ? OR nome LIKE ? OR email LIKE ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """).bind(search_term, search_term, search_term, per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT id, username, nome, email, foto_perfil, is_admin, is_superadmin, 
                   is_banned, created_at, email_confirmed
            FROM user
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """).bind(per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def ban_usuarie(db, usuario_id, reason=None, admin_id=None):
    """Bane usuárie."""
    await db.prepare("""
        UPDATE user SET is_banned = 1, banned_at = datetime('now'), ban_reason = ?
        WHERE id = ?
    """).bind(reason, usuario_id).run()


async def unban_usuarie(db, usuario_id):
    """Remove ban de usuárie."""
    await db.prepare("""
        UPDATE user SET is_banned = 0, banned_at = NULL, ban_reason = NULL
        WHERE id = ?
    """).bind(usuario_id).run()


async def suspend_usuarie(db, usuario_id, until_date):
    """Suspende usuárie temporariamente."""
    await db.prepare("""
        UPDATE user SET suspended_until = ?
        WHERE id = ?
    """).bind(until_date, usuario_id).run()


async def make_admin(db, usuario_id, is_admin=True):
    """Torna usuárie admin ou remove permissão."""
    await db.prepare("""
        UPDATE user SET is_admin = ?
        WHERE id = ?
    """).bind(1 if is_admin else 0, usuario_id).run()


async def get_admin_stats(db):
    """Estatísticas para painel admin."""
    stats = {}
    
    # Total de usuáries
    result = await db.prepare("SELECT COUNT(*) as count FROM user").first()
    stats['total_usuaries'] = safe_get(result, 'count', 0)
    
    # Usuáries ativos (últimos 7 dias)
    result = await db.prepare("""
        SELECT COUNT(DISTINCT user_id) as count FROM user_session
        WHERE created_at > datetime('now', '-7 days')
    """).first()
    stats['usuaries_ativos'] = safe_get(result, 'count', 0)
    
    # Total de posts
    result = await db.prepare("SELECT COUNT(*) as count FROM post WHERE is_deleted = 0").first()
    stats['total_posts'] = safe_get(result, 'count', 0)
    
    # Denúncias pendentes
    stats['denuncias_pendentes'] = await count_pending_reports(db)
    
    # Tickets abertos
    result = await db.prepare("SELECT COUNT(*) as count FROM support_ticket WHERE status = 'aberto'").first()
    stats['tickets_abertos'] = safe_get(result, 'count', 0)
    
    return stats


# ============================================================================
# QUERIES - RATE LIMITING
# ============================================================================

async def check_rate_limit(db, ip_address, endpoint, max_attempts=10, window_minutes=5):
    """Verifica se IP está bloqueado ou excedeu limite."""
    now = datetime.utcnow()
    
    result = await db.prepare("""
        SELECT * FROM rate_limit
        WHERE ip_address = ? AND endpoint = ?
    """).bind(ip_address, endpoint).first()
    
    if not result:
        # Primeiro acesso
        await db.prepare("""
            INSERT INTO rate_limit (ip_address, endpoint, attempts)
            VALUES (?, ?, 1)
        """).bind(ip_address, endpoint).run()
        return True, None
    
    rate = safe_dict(result)
    
    # Handle case where safe_dict returns None
    if not rate:
        return True, None
    
    # Verifica se está bloqueado
    if rate.get('blocked_until'):
        blocked_until = datetime.fromisoformat(rate['blocked_until'])
        if now < blocked_until:
            return False, f"Bloqueade até {rate['blocked_until']}"
        else:
            # Desbloquear
            await db.prepare("""
                UPDATE rate_limit SET attempts = 1, blocked_until = NULL, 
                first_attempt = datetime('now'), last_attempt = datetime('now')
                WHERE ip_address = ? AND endpoint = ?
            """).bind(ip_address, endpoint).run()
            return True, None
    
    # Verifica janela de tempo
    first_attempt_str = rate.get('first_attempt')
    if not first_attempt_str:
        return True, None
    first_attempt = datetime.fromisoformat(first_attempt_str)
    window = timedelta(minutes=window_minutes)
    
    if now - first_attempt > window:
        # Reset contagem
        await db.prepare("""
            UPDATE rate_limit SET attempts = 1, 
            first_attempt = datetime('now'), last_attempt = datetime('now')
            WHERE ip_address = ? AND endpoint = ?
        """).bind(ip_address, endpoint).run()
        return True, None
    
    if rate['attempts'] >= max_attempts:
        # Bloquear
        block_until = (now + timedelta(minutes=15)).isoformat()
        await db.prepare("""
            UPDATE rate_limit SET blocked_until = ?
            WHERE ip_address = ? AND endpoint = ?
        """).bind(block_until, ip_address, endpoint).run()
        return False, "Muitas tentativas. Bloqueade por 15 minutos."
    
    # Incrementar tentativas
    await db.prepare("""
        UPDATE rate_limit SET attempts = attempts + 1, last_attempt = datetime('now')
        WHERE ip_address = ? AND endpoint = ?
    """).bind(ip_address, endpoint).run()
    return True, None


# ============================================================================
# QUERIES - LOGS DE ATIVIDADE
# ============================================================================

async def log_activity(db, acao, usuario_id=None, descricao=None, ip_address=None, 
                       user_agent=None, dados_extra=None):
    """Registra uma atividade no log de auditoria."""
    dados_json = json.dumps(dados_extra) if dados_extra else None
    
    await db.prepare("""
        INSERT INTO activity_log (usuario_id, acao, descricao, ip_address, user_agent, dados_extra)
        VALUES (?, ?, ?, ?, ?, ?)
    """).bind(usuario_id, acao, descricao, ip_address, user_agent, dados_json).run()


async def get_activity_log(db, usuario_id=None, acao=None, page=1, per_page=50):
    """Lista atividades do log."""
    offset = (page - 1) * per_page
    
    if usuario_id and acao:
        result = await db.prepare("""
            SELECT a.*, u.username
            FROM activity_log a
            LEFT JOIN user u ON a.usuario_id = u.id
            WHERE a.usuario_id = ? AND a.acao = ?
            ORDER BY a.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(usuario_id, acao, per_page, offset).all()
    elif usuario_id:
        result = await db.prepare("""
            SELECT a.*, u.username
            FROM activity_log a
            LEFT JOIN user u ON a.usuario_id = u.id
            WHERE a.usuario_id = ?
            ORDER BY a.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(usuario_id, per_page, offset).all()
    elif acao:
        result = await db.prepare("""
            SELECT a.*, u.username
            FROM activity_log a
            LEFT JOIN user u ON a.usuario_id = u.id
            WHERE a.acao = ?
            ORDER BY a.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(acao, per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT a.*, u.username
            FROM activity_log a
            LEFT JOIN user u ON a.usuario_id = u.id
            ORDER BY a.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - GAMIFICAÇÃO (Pontos e Badges)
# ============================================================================

async def get_user_points(db, usuario_id):
    """Retorna pontos de usuárie."""
    result = await db.prepare("""
        SELECT * FROM user_points WHERE usuario_id = ?
    """).bind(usuario_id).first()
    
    if not result:
        # Criar registro se não existe
        await db.prepare("""
            INSERT INTO user_points (usuario_id) VALUES (?)
        """).bind(usuario_id).run()
        return {'usuario_id': usuario_id, 'pontos_total': 0, 'pontos_exercicios': 0,
                'pontos_posts': 0, 'pontos_dinamicas': 0, 'nivel': 1}
    
    return safe_dict(result)


async def add_points(db, usuario_id, pontos, tipo='exercicios'):
    """Adiciona pontos a usuárie."""
    # Primeiro garante que o registro existe
    await get_user_points(db, usuario_id)
    
    # Map tipo to column name safely - apenas colunas da whitelist são usadas
    # Isso é seguro porque tipo_coluna só pode ser um dos valores do dict
    column_map = {
        'exercicios': 'pontos_exercicios',
        'posts': 'pontos_posts',
        'dinamicas': 'pontos_dinamicas'
    }
    
    tipo_coluna = column_map.get(tipo, 'pontos_exercicios')
    
    # Usar queries separadas para cada tipo para evitar f-string SQL
    if tipo_coluna == 'pontos_exercicios':
        await db.prepare("""
            UPDATE user_points 
            SET pontos_total = pontos_total + ?,
                pontos_exercicios = pontos_exercicios + ?,
                updated_at = datetime('now')
            WHERE usuario_id = ?
        """).bind(pontos, pontos, usuario_id).run()
    elif tipo_coluna == 'pontos_posts':
        await db.prepare("""
            UPDATE user_points 
            SET pontos_total = pontos_total + ?,
                pontos_posts = pontos_posts + ?,
                updated_at = datetime('now')
            WHERE usuario_id = ?
        """).bind(pontos, pontos, usuario_id).run()
    elif tipo_coluna == 'pontos_dinamicas':
        await db.prepare("""
            UPDATE user_points 
            SET pontos_total = pontos_total + ?,
                pontos_dinamicas = pontos_dinamicas + ?,
                updated_at = datetime('now')
            WHERE usuario_id = ?
        """).bind(pontos, pontos, usuario_id).run()
    
    # Atualizar nível baseado em pontos
    await update_user_level(db, usuario_id)


async def update_user_level(db, usuario_id):
    """Atualiza o nível de usuárie baseado em pontos."""
    result = await db.prepare("""
        SELECT pontos_total FROM user_points WHERE usuario_id = ?
    """).bind(usuario_id).first()
    
    if not result:
        return
    
    pontos = safe_get(result, 'pontos_total', 0)
    
    # Calcular nível (a cada 100 pontos sobe um nível)
    nivel = max(1, (pontos // 100) + 1)
    
    await db.prepare("""
        UPDATE user_points SET nivel = ? WHERE usuario_id = ?
    """).bind(nivel, usuario_id).run()


async def get_ranking(db, limit=10, tipo=None):
    """Retorna ranking de usuáries por pontos."""
    # Usar queries separadas para cada tipo para evitar f-string SQL
    if tipo == 'exercicios':
        result = await db.prepare("""
            SELECT p.*, u.username, u.nome, u.foto_perfil
            FROM user_points p
            JOIN user u ON p.usuario_id = u.id
            WHERE u.is_banned = 0
            ORDER BY p.pontos_exercicios DESC
            LIMIT ?
        """).bind(limit).all()
    elif tipo == 'posts':
        result = await db.prepare("""
            SELECT p.*, u.username, u.nome, u.foto_perfil
            FROM user_points p
            JOIN user u ON p.usuario_id = u.id
            WHERE u.is_banned = 0
            ORDER BY p.pontos_posts DESC
            LIMIT ?
        """).bind(limit).all()
    elif tipo == 'dinamicas':
        result = await db.prepare("""
            SELECT p.*, u.username, u.nome, u.foto_perfil
            FROM user_points p
            JOIN user u ON p.usuario_id = u.id
            WHERE u.is_banned = 0
            ORDER BY p.pontos_dinamicas DESC
            LIMIT ?
        """).bind(limit).all()
    else:
        result = await db.prepare("""
            SELECT p.*, u.username, u.nome, u.foto_perfil
            FROM user_points p
            JOIN user u ON p.usuario_id = u.id
            WHERE u.is_banned = 0
            ORDER BY p.pontos_total DESC
            LIMIT ?
        """).bind(limit).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_all_badges(db):
    """Lista todos os badges disponíveis."""
    result = await db.prepare("""
        SELECT * FROM badge ORDER BY categoria, pontos_necessarios
    """).all()
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_user_badges(db, usuario_id):
    """Lista badges de usuárie."""
    result = await db.prepare("""
        SELECT b.*, ub.earned_at
        FROM user_badge ub
        JOIN badge b ON ub.badge_id = b.id
        WHERE ub.usuario_id = ?
        ORDER BY ub.earned_at DESC
    """).bind(usuario_id).all()
    return [safe_dict(row) for row in result.results] if result.results else []


async def award_badge(db, usuario_id, badge_nome):
    """Concede um badge a usuárie."""
    # Buscar badge por nome
    badge = await db.prepare("""
        SELECT id FROM badge WHERE nome = ?
    """).bind(badge_nome).first()
    
    if not badge:
        return False
    
    try:
        await db.prepare("""
            INSERT INTO user_badge (usuario_id, badge_id) VALUES (?, ?)
        """).bind(usuario_id, badge['id']).run()
        
        # Notificar usuárie
        await create_notification(db, usuario_id, 'badge',
                                  titulo=f'Novo badge: {badge_nome}! 🎖️')
        return True
    except Exception:
        return False  # Já tem o badge ou erro de constraint


async def check_and_award_badges(db, usuario_id):
    """Verifica e concede badges que usuárie merece."""
    # Buscar estatísticas
    points = await get_user_points(db, usuario_id)
    
    badges_concedidos = []
    
    # Badge por pontos de exercícios
    if points['pontos_exercicios'] >= 100:
        if await award_badge(db, usuario_id, 'Estudante'):
            badges_concedidos.append('Estudante')
    if points['pontos_exercicios'] >= 500:
        if await award_badge(db, usuario_id, 'Dedicade'):
            badges_concedidos.append('Dedicade')
    if points['pontos_exercicios'] >= 1000:
        if await award_badge(db, usuario_id, 'Mestre'):
            badges_concedidos.append('Mestre')
    
    # Badge por posts
    post_count = await db.prepare("""
        SELECT COUNT(*) as count FROM post WHERE usuario_id = ? AND is_deleted = 0
    """).bind(usuario_id).first()
    if post_count and post_count['count'] >= 5:
        if await award_badge(db, usuario_id, 'Escritor'):
            badges_concedidos.append('Escritor')
    
    # Badge por amigues
    amigues_count = await db.prepare("""
        SELECT COUNT(*) as count FROM amizade
        WHERE (usuarie1_id = ? OR usuarie2_id = ?) AND status = 'aceita'
    """).bind(usuario_id, usuario_id).first()
    if amigues_count and amigues_count['count'] >= 5:
        if await award_badge(db, usuario_id, 'Social'):
            badges_concedidos.append('Social')
    
    return badges_concedidos


# ============================================================================
# QUERIES - PROGRESSO EM EXERCÍCIOS
# ============================================================================

async def record_exercise_answer(db, usuario_id, question_id, resposta, correto, tempo_resposta=None):
    """Registra resposta de exercício e retorna pontos ganhos."""
    pontos = 0
    primeira_tentativa = 1
    
    # Verificar se já respondeu corretamente antes (para não dar pontos novamente)
    scored = await db.prepare("""
        SELECT 1 FROM exercise_scored WHERE usuario_id = ? AND question_id = ?
    """).bind(usuario_id, question_id).first()
    
    if scored:
        primeira_tentativa = 0
    elif correto:
        # Primeira vez acertando - dar pontos
        pontos = 1  # 1 ponto por acerto
        
        # Marcar como pontuado
        await db.prepare("""
            INSERT INTO exercise_scored (usuario_id, question_id) VALUES (?, ?)
        """).bind(usuario_id, question_id).run()
        
        # Adicionar pontos ao total
        await add_points(db, usuario_id, pontos, 'exercicios')
    
    # Registrar no histórico
    await db.prepare("""
        INSERT INTO exercise_progress (usuario_id, question_id, resposta_usuarie, correto, 
                                        pontos_ganhos, primeira_tentativa, tempo_resposta)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """).bind(usuario_id, question_id, resposta, 1 if correto else 0, 
              pontos, primeira_tentativa, tempo_resposta).run()
    
    # Verificar badges
    await check_and_award_badges(db, usuario_id)
    
    return pontos


async def get_user_exercise_stats(db, usuario_id, topic_id=None):
    """Retorna estatísticas de exercícios de usuárie."""
    if topic_id:
        result = await db.prepare("""
            SELECT 
                COUNT(*) as total_respostas,
                SUM(CASE WHEN correto = 1 THEN 1 ELSE 0 END) as acertos,
                SUM(pontos_ganhos) as pontos
            FROM exercise_progress ep
            JOIN exercise_question eq ON ep.question_id = eq.id
            WHERE ep.usuario_id = ? AND eq.topic_id = ?
        """).bind(usuario_id, topic_id).first()
    else:
        result = await db.prepare("""
            SELECT 
                COUNT(*) as total_respostas,
                SUM(CASE WHEN correto = 1 THEN 1 ELSE 0 END) as acertos,
                SUM(pontos_ganhos) as pontos
            FROM exercise_progress
            WHERE usuario_id = ?
        """).bind(usuario_id).first()
    
    if result:
        return safe_dict(result)
    return {'total_respostas': 0, 'acertos': 0, 'pontos': 0}


async def get_questions_not_scored(db, usuario_id, topic_id=None, limit=10):
    """Retorna questões que usuárie ainda não pontuou."""
    if topic_id:
        result = await db.prepare("""
            SELECT eq.*, et.nome as topic_name
            FROM exercise_question eq
            JOIN exercise_topic et ON eq.topic_id = et.id
            LEFT JOIN exercise_scored es ON eq.id = es.question_id AND es.usuario_id = ?
            WHERE es.question_id IS NULL AND eq.topic_id = ?
            ORDER BY RANDOM()
            LIMIT ?
        """).bind(usuario_id, topic_id, limit).all()
    else:
        result = await db.prepare("""
            SELECT eq.*, et.nome as topic_name
            FROM exercise_question eq
            JOIN exercise_topic et ON eq.topic_id = et.id
            LEFT JOIN exercise_scored es ON eq.id = es.question_id AND es.usuario_id = ?
            WHERE es.question_id IS NULL
            ORDER BY RANDOM()
            LIMIT ?
        """).bind(usuario_id, limit).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - LISTAS DE EXERCÍCIOS PERSONALIZADAS
# ============================================================================

async def create_exercise_list(db, usuario_id, nome, descricao=None, modo='estudo', tempo_limite=None):
    """Cria uma lista personalizada de exercícios."""
    result = await db.prepare("""
        INSERT INTO exercise_list (usuario_id, nome, descricao, modo, tempo_limite)
        VALUES (?, ?, ?, ?, ?)
        RETURNING id
    """).bind(usuario_id, nome, descricao, modo, tempo_limite).first()
    return safe_get(result, 'id')


async def add_to_exercise_list(db, list_id, question_id, ordem=0):
    """Adiciona questão à lista de exercícios."""
    try:
        await db.prepare("""
            INSERT INTO exercise_list_item (list_id, question_id, ordem) VALUES (?, ?, ?)
        """).bind(list_id, question_id, ordem).run()
        return True
    except Exception:
        return False  # Questão já está na lista


async def get_exercise_lists(db, usuario_id):
    """Lista as listas de exercícios de usuárie."""
    result = await db.prepare("""
        SELECT el.*, 
               (SELECT COUNT(*) FROM exercise_list_item WHERE list_id = el.id) as question_count
        FROM exercise_list el
        WHERE el.usuario_id = ?
        ORDER BY el.created_at DESC
    """).bind(usuario_id).all()
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_exercise_list_questions(db, list_id):
    """Retorna questões de uma lista."""
    result = await db.prepare("""
        SELECT eq.*, et.nome as topic_name, eli.ordem
        FROM exercise_list_item eli
        JOIN exercise_question eq ON eli.question_id = eq.id
        JOIN exercise_topic et ON eq.topic_id = et.id
        WHERE eli.list_id = ?
        ORDER BY eli.ordem
    """).bind(list_id).all()
    return [safe_dict(row) for row in result.results] if result.results else []


async def save_quiz_result(db, usuario_id, acertos, erros, pontos, tempo_total, list_id=None, topic_id=None):
    """Salva resultado de quiz."""
    result = await db.prepare("""
        INSERT INTO quiz_result (usuario_id, list_id, topic_id, acertos, erros, pontos_ganhos, tempo_total)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        RETURNING id
    """).bind(usuario_id, list_id, topic_id, acertos, erros, pontos, tempo_total).first()
    return safe_get(result, 'id')


# ============================================================================
# QUERIES - FLASHCARDS
# ============================================================================

async def create_flashcard_deck(db, titulo, usuario_id=None, descricao=None, is_public=False):
    """Cria um deck de flashcards."""
    result = await db.prepare("""
        INSERT INTO flashcard_deck (usuario_id, titulo, descricao, is_public)
        VALUES (?, ?, ?, ?)
        RETURNING id
    """).bind(usuario_id, titulo, descricao, 1 if is_public else 0).first()
    
    # Dar badge se for o primeiro deck
    if usuario_id:
        await award_badge(db, usuario_id, 'Flashcard Pro')
    
    return safe_get(result, 'id')


async def add_flashcard(db, deck_id, frente, verso, dica=None, ordem=0):
    """Adiciona um flashcard ao deck."""
    result = await db.prepare("""
        INSERT INTO flashcard (deck_id, frente, verso, dica, ordem)
        VALUES (?, ?, ?, ?, ?)
        RETURNING id
    """).bind(deck_id, frente, verso, dica, ordem).first()
    return safe_get(result, 'id')


async def get_flashcard_decks(db, usuario_id=None, include_public=True):
    """Lista decks de flashcards."""
    if usuario_id and include_public:
        result = await db.prepare("""
            SELECT fd.*, u.username as author_name,
                   (SELECT COUNT(*) FROM flashcard WHERE deck_id = fd.id) as card_count
            FROM flashcard_deck fd
            LEFT JOIN user u ON fd.usuario_id = u.id
            WHERE fd.usuario_id = ? OR fd.is_public = 1
            ORDER BY fd.created_at DESC
        """).bind(usuario_id).all()
    elif usuario_id:
        result = await db.prepare("""
            SELECT fd.*, u.username as author_name,
                   (SELECT COUNT(*) FROM flashcard WHERE deck_id = fd.id) as card_count
            FROM flashcard_deck fd
            LEFT JOIN user u ON fd.usuario_id = u.id
            WHERE fd.usuario_id = ?
            ORDER BY fd.created_at DESC
        """).bind(usuario_id).all()
    else:
        result = await db.prepare("""
            SELECT fd.*, u.username as author_name,
                   (SELECT COUNT(*) FROM flashcard WHERE deck_id = fd.id) as card_count
            FROM flashcard_deck fd
            LEFT JOIN user u ON fd.usuario_id = u.id
            WHERE fd.is_public = 1
            ORDER BY fd.created_at DESC
        """).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_flashcards(db, deck_id):
    """Retorna flashcards de um deck."""
    result = await db.prepare("""
        SELECT * FROM flashcard WHERE deck_id = ? ORDER BY ordem
    """).bind(deck_id).all()
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_cards_to_review(db, usuario_id, deck_id=None, limit=20):
    """Retorna flashcards para revisão espaçada."""
    now = datetime.utcnow().isoformat()
    
    if deck_id:
        result = await db.prepare("""
            SELECT f.*, fr.ease_factor, fr.interval_days, fr.repetitions, fr.next_review
            FROM flashcard f
            LEFT JOIN flashcard_review fr ON f.id = fr.flashcard_id AND fr.usuario_id = ?
            WHERE f.deck_id = ?
            AND (fr.next_review IS NULL OR fr.next_review <= ?)
            ORDER BY fr.next_review NULLS FIRST, RANDOM()
            LIMIT ?
        """).bind(usuario_id, deck_id, now, limit).all()
    else:
        result = await db.prepare("""
            SELECT f.*, fd.titulo as deck_titulo, fr.ease_factor, fr.interval_days, 
                   fr.repetitions, fr.next_review
            FROM flashcard f
            JOIN flashcard_deck fd ON f.deck_id = fd.id
            LEFT JOIN flashcard_review fr ON f.id = fr.flashcard_id AND fr.usuario_id = ?
            WHERE (fd.usuario_id = ? OR fd.is_public = 1)
            AND (fr.next_review IS NULL OR fr.next_review <= ?)
            ORDER BY fr.next_review NULLS FIRST, RANDOM()
            LIMIT ?
        """).bind(usuario_id, usuario_id, now, limit).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def record_flashcard_review(db, usuario_id, flashcard_id, quality):
    """
    Registra revisão de flashcard usando algoritmo SM-2.
    quality: 0-5 (0-2 = errou, 3-5 = acertou com diferentes níveis de facilidade)
    """
    # Buscar revisão existente
    existing = await db.prepare("""
        SELECT * FROM flashcard_review WHERE usuario_id = ? AND flashcard_id = ?
    """).bind(usuario_id, flashcard_id).first()
    
    if existing:
        ef = existing['ease_factor']
        reps = existing['repetitions']
        interval = existing['interval_days']
    else:
        ef = 2.5
        reps = 0
        interval = 1
    
    # Algoritmo SM-2
    if quality < 3:
        # Errou - resetar
        reps = 0
        interval = 1
    else:
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = int(interval * ef)
        
        reps += 1
    
    # Atualizar ease factor
    ef = max(1.3, ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    
    # Calcular próxima revisão
    next_review = (datetime.utcnow() + timedelta(days=interval)).isoformat()
    
    if existing:
        await db.prepare("""
            UPDATE flashcard_review 
            SET ease_factor = ?, interval_days = ?, repetitions = ?, 
                next_review = ?, last_review = datetime('now')
            WHERE usuario_id = ? AND flashcard_id = ?
        """).bind(ef, interval, reps, next_review, usuario_id, flashcard_id).run()
    else:
        await db.prepare("""
            INSERT INTO flashcard_review (usuario_id, flashcard_id, ease_factor, 
                                          interval_days, repetitions, next_review, last_review)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """).bind(usuario_id, flashcard_id, ef, interval, reps, next_review).run()
    
    return {'ease_factor': ef, 'interval_days': interval, 'next_review': next_review}


# ============================================================================
# QUERIES - FAVORITOS
# ============================================================================

async def add_favorite(db, usuario_id, tipo, item_id):
    """Adiciona item aos favoritos."""
    try:
        await db.prepare("""
            INSERT INTO favorito (usuario_id, tipo, item_id) VALUES (?, ?, ?)
        """).bind(usuario_id, tipo, item_id).run()
        return True
    except Exception:
        return False  # Já é favorito


async def remove_favorite(db, usuario_id, tipo, item_id):
    """Remove item dos favoritos."""
    await db.prepare("""
        DELETE FROM favorito WHERE usuario_id = ? AND tipo = ? AND item_id = ?
    """).bind(usuario_id, tipo, item_id).run()


async def is_favorite(db, usuario_id, tipo, item_id):
    """Verifica se item é favorito."""
    result = await db.prepare("""
        SELECT 1 FROM favorito WHERE usuario_id = ? AND tipo = ? AND item_id = ?
    """).bind(usuario_id, tipo, item_id).first()
    return result is not None


async def get_favorites(db, usuario_id, tipo=None):
    """Lista favoritos de usuárie."""
    if tipo:
        result = await db.prepare("""
            SELECT * FROM favorito WHERE usuario_id = ? AND tipo = ?
            ORDER BY created_at DESC
        """).bind(usuario_id, tipo).all()
    else:
        result = await db.prepare("""
            SELECT * FROM favorito WHERE usuario_id = ?
            ORDER BY created_at DESC
        """).bind(usuario_id).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - HISTÓRICO DE USUÁRIE
# ============================================================================

async def add_to_history(db, usuario_id, tipo, item_tipo, item_id, dados=None):
    """Adiciona item ao histórico de usuárie."""
    dados_json = json.dumps(dados) if dados else None
    
    await db.prepare("""
        INSERT INTO user_history (usuario_id, tipo, item_tipo, item_id, dados)
        VALUES (?, ?, ?, ?, ?)
    """).bind(usuario_id, tipo, item_tipo, item_id, dados_json).run()


async def get_user_history(db, usuario_id, item_tipo=None, limit=50):
    """Lista histórico de usuárie."""
    if item_tipo:
        result = await db.prepare("""
            SELECT * FROM user_history 
            WHERE usuario_id = ? AND item_tipo = ?
            ORDER BY created_at DESC
            LIMIT ?
        """).bind(usuario_id, item_tipo, limit).all()
    else:
        result = await db.prepare("""
            SELECT * FROM user_history 
            WHERE usuario_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """).bind(usuario_id, limit).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - PREFERÊNCIAS DE USUÁRIE
# ============================================================================

async def get_user_preferences(db, usuario_id):
    """Retorna preferências de usuárie."""
    result = await db.prepare("""
        SELECT * FROM user_preferences WHERE usuario_id = ?
    """).bind(usuario_id).first()
    
    if not result:
        # Criar preferências padrão
        await db.prepare("""
            INSERT INTO user_preferences (usuario_id) VALUES (?)
        """).bind(usuario_id).run()
        return await get_user_preferences(db, usuario_id)
    
    return safe_dict(result)


async def update_user_preferences(db, usuario_id, **kwargs):
    """Atualiza preferências de usuárie."""
    # Garantir que registro existe
    await get_user_preferences(db, usuario_id)
    
    # Apenas colunas da whitelist são atualizadas - isso é seguro
    allowed_columns = {
        'tema': 'tema',
        'fonte_tamanho': 'fonte_tamanho', 
        'fonte_familia': 'fonte_familia',
        'alto_contraste': 'alto_contraste',
        'animacoes_reduzidas': 'animacoes_reduzidas',
        'exibir_libras': 'exibir_libras',
        'audio_habilitado': 'audio_habilitado',
        'velocidade_audio': 'velocidade_audio',
        'notificacoes_email': 'notificacoes_email',
        'notificacoes_push': 'notificacoes_push',
        'idioma': 'idioma'
    }
    
    # Filtrar apenas chaves permitidas
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_columns}
    
    if not filtered_kwargs:
        return False
    
    # Atualizar cada campo individualmente para evitar SQL dinâmico
    for key, value in filtered_kwargs.items():
        # Os nomes de colunas são validados pela whitelist acima
        if key == 'tema':
            await db.prepare("UPDATE user_preferences SET tema = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(value, usuario_id).run()
        elif key == 'fonte_tamanho':
            await db.prepare("UPDATE user_preferences SET fonte_tamanho = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(value, usuario_id).run()
        elif key == 'fonte_familia':
            await db.prepare("UPDATE user_preferences SET fonte_familia = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(value, usuario_id).run()
        elif key == 'alto_contraste':
            await db.prepare("UPDATE user_preferences SET alto_contraste = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(value, usuario_id).run()
        elif key == 'animacoes_reduzidas':
            await db.prepare("UPDATE user_preferences SET animacoes_reduzidas = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(value, usuario_id).run()
        elif key == 'exibir_libras':
            await db.prepare("UPDATE user_preferences SET exibir_libras = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(value, usuario_id).run()
        elif key == 'audio_habilitado':
            await db.prepare("UPDATE user_preferences SET audio_habilitado = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(value, usuario_id).run()
        elif key == 'velocidade_audio':
            await db.prepare("UPDATE user_preferences SET velocidade_audio = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(value, usuario_id).run()
        elif key == 'notificacoes_email':
            await db.prepare("UPDATE user_preferences SET notificacoes_email = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(value, usuario_id).run()
        elif key == 'notificacoes_push':
            await db.prepare("UPDATE user_preferences SET notificacoes_push = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(value, usuario_id).run()
        elif key == 'idioma':
            await db.prepare("UPDATE user_preferences SET idioma = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(value, usuario_id).run()
    
    return True


# ============================================================================
# QUERIES - MENSAGENS DIRETAS
# ============================================================================

async def send_direct_message(db, remetente_id, destinatarie_id, conteudo):
    """Envia mensagem direta."""
    result = await db.prepare("""
        INSERT INTO mensagem_direta (remetente_id, destinatarie_id, conteudo)
        VALUES (?, ?, ?)
        RETURNING id
    """).bind(remetente_id, destinatarie_id, conteudo).first()
    
    # Notificar destinatárie
    await create_notification(db, destinatarie_id, 'mensagem',
                              titulo='Nova mensagem!',
                              from_usuario_id=remetente_id)
    
    return safe_get(result, 'id')


async def get_conversations(db, usuario_id):
    """Lista conversas de usuárie."""
    result = await db.prepare("""
        SELECT DISTINCT 
            CASE 
                WHEN remetente_id = ? THEN destinatarie_id 
                ELSE remetente_id 
            END as other_user_id
        FROM mensagem_direta
        WHERE remetente_id = ? OR destinatarie_id = ?
    """).bind(usuario_id, usuario_id, usuario_id).all()
    
    if not result.results:
        return []
    
    # Buscar dados dos usuáries
    conversations = []
    for row in result.results:
        other_id = row['other_user_id']
        user = await get_user_by_id(db, other_id)
        
        # Última mensagem
        last_msg = await db.prepare("""
            SELECT * FROM mensagem_direta
            WHERE (remetente_id = ? AND destinatarie_id = ?)
               OR (remetente_id = ? AND destinatarie_id = ?)
            ORDER BY created_at DESC
            LIMIT 1
        """).bind(usuario_id, other_id, other_id, usuario_id).first()
        
        # Mensagens não lidas
        unread = await db.prepare("""
            SELECT COUNT(*) as count FROM mensagem_direta
            WHERE remetente_id = ? AND destinatarie_id = ? AND lida = 0
        """).bind(other_id, usuario_id).first()
        
        conversations.append({
            'other_user': user,
            'last_message': safe_dict(last_msg) if last_msg else None,
            'unread_count': safe_dict(unread)['count'] if unread else 0
        })
    
    return conversations


async def get_messages_with_user(db, usuario_id, other_user_id, page=1, per_page=50):
    """Lista mensagens entre dois usuáries."""
    offset = (page - 1) * per_page
    
    result = await db.prepare("""
        SELECT m.*, 
               ur.username as remetente_username, ur.foto_perfil as remetente_foto,
               ud.username as destinatarie_username
        FROM mensagem_direta m
        LEFT JOIN user ur ON m.remetente_id = ur.id
        LEFT JOIN user ud ON m.destinatarie_id = ud.id
        WHERE (m.remetente_id = ? AND m.destinatarie_id = ?)
           OR (m.remetente_id = ? AND m.destinatarie_id = ?)
        ORDER BY m.created_at DESC
        LIMIT ? OFFSET ?
    """).bind(usuario_id, other_user_id, other_user_id, usuario_id, 
              per_page, offset).all()
    
    # Marcar como lidas
    await db.prepare("""
        UPDATE mensagem_direta SET lida = 1
        WHERE remetente_id = ? AND destinatarie_id = ? AND lida = 0
    """).bind(other_user_id, usuario_id).run()
    
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - GRUPOS DE ESTUDO
# ============================================================================

async def create_study_group(db, nome, criador_id, descricao=None, is_public=True, max_membres=50):
    """Cria um grupo de estudo."""
    result = await db.prepare("""
        INSERT INTO grupo_estudo (nome, descricao, criador_id, is_public, max_membres)
        VALUES (?, ?, ?, ?, ?)
        RETURNING id
    """).bind(nome, descricao, criador_id, 1 if is_public else 0, max_membres).first()
    
    if result:
        # Adicionar criador como admin
        grupo_id = safe_get(result, 'id')
        if grupo_id:
            await db.prepare("""
                INSERT INTO grupo_membre (grupo_id, usuario_id, role) VALUES (?, ?, 'admin')
            """).bind(grupo_id, criador_id).run()
    
    return safe_get(result, 'id')


async def join_study_group(db, grupo_id, usuario_id):
    """Entrar em um grupo de estudo."""
    # Verificar limite de membros
    count = await db.prepare("""
        SELECT COUNT(*) as count FROM grupo_membre WHERE grupo_id = ?
    """).bind(grupo_id).first()
    
    grupo = await db.prepare("""
        SELECT max_membres FROM grupo_estudo WHERE id = ?
    """).bind(grupo_id).first()
    
    if count and grupo and count['count'] >= grupo['max_membres']:
        return False, "Grupo cheio"
    
    try:
        await db.prepare("""
            INSERT INTO grupo_membre (grupo_id, usuario_id) VALUES (?, ?)
        """).bind(grupo_id, usuario_id).run()
        return True, None
    except Exception:
        return False, "Já é membre do grupo"


async def leave_study_group(db, grupo_id, usuario_id):
    """Sair de um grupo de estudo."""
    await db.prepare("""
        DELETE FROM grupo_membre WHERE grupo_id = ? AND usuario_id = ?
    """).bind(grupo_id, usuario_id).run()


async def get_study_groups(db, usuario_id=None, apenas_meus=False):
    """Lista grupos de estudo."""
    if apenas_meus and usuario_id:
        result = await db.prepare("""
            SELECT g.*, gm.role,
                   (SELECT COUNT(*) FROM grupo_membre WHERE grupo_id = g.id) as member_count,
                   u.username as criador_username
            FROM grupo_estudo g
            JOIN grupo_membre gm ON g.id = gm.grupo_id
            LEFT JOIN user u ON g.criador_id = u.id
            WHERE gm.usuario_id = ?
            ORDER BY g.created_at DESC
        """).bind(usuario_id).all()
    else:
        result = await db.prepare("""
            SELECT g.*,
                   (SELECT COUNT(*) FROM grupo_membre WHERE grupo_id = g.id) as member_count,
                   u.username as criador_username
            FROM grupo_estudo g
            LEFT JOIN user u ON g.criador_id = u.id
            WHERE g.is_public = 1
            ORDER BY g.created_at DESC
        """).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_group_messages(db, grupo_id, page=1, per_page=50):
    """Lista mensagens de um grupo."""
    offset = (page - 1) * per_page
    
    result = await db.prepare("""
        SELECT gm.*, u.username, u.foto_perfil
        FROM grupo_mensagem gm
        LEFT JOIN user u ON gm.usuario_id = u.id
        WHERE gm.grupo_id = ?
        ORDER BY gm.created_at DESC
        LIMIT ? OFFSET ?
    """).bind(grupo_id, per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def send_group_message(db, grupo_id, usuario_id, conteudo):
    """Envia mensagem no grupo."""
    result = await db.prepare("""
        INSERT INTO grupo_mensagem (grupo_id, usuario_id, conteudo)
        VALUES (?, ?, ?)
        RETURNING id
    """).bind(grupo_id, usuario_id, conteudo).first()
    return safe_get(result, 'id')


# ============================================================================
# QUERIES - CONTEÚDO DE ACESSIBILIDADE
# ============================================================================

async def get_accessibility_content(db, tipo_conteudo, conteudo_id):
    """Retorna conteúdo de acessibilidade (Libras/Áudio)."""
    result = await db.prepare("""
        SELECT * FROM accessibility_content
        WHERE tipo_conteudo = ? AND conteudo_id = ?
    """).bind(tipo_conteudo, conteudo_id).first()
    
    if result:
        return safe_dict(result)
    return None


async def save_accessibility_content(db, tipo_conteudo, conteudo_id, video_libras_url=None,
                                     audio_url=None, audio_duracao=None, transcricao=None):
    """Salva ou atualiza conteúdo de acessibilidade."""
    existing = await get_accessibility_content(db, tipo_conteudo, conteudo_id)
    
    if existing:
        await db.prepare("""
            UPDATE accessibility_content 
            SET video_libras_url = COALESCE(?, video_libras_url),
                audio_url = COALESCE(?, audio_url),
                audio_duracao = COALESCE(?, audio_duracao),
                transcricao = COALESCE(?, transcricao),
                updated_at = datetime('now')
            WHERE tipo_conteudo = ? AND conteudo_id = ?
        """).bind(video_libras_url, audio_url, audio_duracao, transcricao,
                  tipo_conteudo, conteudo_id).run()
    else:
        await db.prepare("""
            INSERT INTO accessibility_content 
            (tipo_conteudo, conteudo_id, video_libras_url, audio_url, audio_duracao, transcricao)
            VALUES (?, ?, ?, ?, ?, ?)
        """).bind(tipo_conteudo, conteudo_id, video_libras_url, audio_url, 
                  audio_duracao, transcricao).run()


# ============================================================================
# VALIDAÇÃO DE FORÇA DE SENHA
# ============================================================================

def validate_password_strength(password):
    """
    Valida força da senha.
    Retorna (is_valid, message)
    """
    if len(password) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres"
    
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    
    score = sum([has_lower, has_upper, has_digit, has_special])
    
    if score < 2:
        return False, "A senha deve ter pelo menos 2 dos seguintes: minúsculas, maiúsculas, números, símbolos"
    
    if len(password) < 10 and score < 3:
        return False, "Senhas curtas devem ter pelo menos 3 tipos de caracteres"
    
    return True, "Senha válida"


# ============================================================================
# MENÇÕES (@)
# ============================================================================

import re


def extract_mentions(text):
    """Extrai menções @username do texto."""
    if not text:
        return []
    # Encontra todas as menções @username
    pattern = r'@([a-zA-Z0-9_]+)'
    matches = re.findall(pattern, text)
    # Remove duplicatas mantendo ordem
    seen = set()
    result = []
    for m in matches:
        if m.lower() not in seen:
            seen.add(m.lower())
            result.append(m)
    return result


async def create_mencao(db, usuario_id, autor_id, tipo, item_id):
    """Cria uma menção."""
    try:
        await db.prepare("""
            INSERT INTO mencao (usuario_id, autor_id, tipo, item_id, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """).bind(usuario_id, autor_id, tipo, item_id).run()
        return True
    except Exception:
        return False


async def process_mentions(db, text, autor_id, tipo, item_id):
    """Processa menções em um texto, cria registros e notificações."""
    usernames = extract_mentions(text)
    for username in usernames:
        # Buscar usuárie por username
        user = await get_user_by_username(db, username)
        if user and user['id'] != autor_id:
            # Criar menção
            await create_mencao(db, user['id'], autor_id, tipo, item_id)
            # Criar notificação
            autor = await get_user_by_id(db, autor_id)
            autor_nome = autor['nome'] or autor['username'] if autor else 'Alguém'
            await create_notification(
                db,
                user['id'],
                'mencao',
                'Você foi mencionade!',
                f'{autor_nome} mencionou você em um {tipo}',
                f'/{tipo}/{item_id}',
                autor_id,
                item_id if tipo == 'post' else None,
                item_id if tipo == 'comentario' else None
            )
    return usernames


async def get_user_mentions(db, usuario_id, limit=50, offset=0):
    """Busca menções de um usuárie."""
    results = await db.prepare("""
        SELECT m.*, u.nome as autor_nome, u.username as autor_username, u.foto_perfil as autor_foto
        FROM mencao m
        LEFT JOIN user u ON m.autor_id = u.id
        WHERE m.usuario_id = ?
        ORDER BY m.created_at DESC
        LIMIT ? OFFSET ?
    """).bind(usuario_id, limit, offset).all()
    return [safe_dict(r) for r in results.results] if results.results else []


# ============================================================================
# HASHTAGS (#)
# ============================================================================

def extract_hashtags(text):
    """Extrai hashtags do texto."""
    if not text:
        return []
    # Encontra todas as hashtags (aceita acentos e caracteres especiais em português)
    pattern = r'#([a-zA-ZÀ-ÿ0-9_]+)'
    matches = re.findall(pattern, text)
    # Remove duplicatas mantendo ordem e converte para minúsculas
    seen = set()
    result = []
    for m in matches:
        lower = m.lower()
        if lower not in seen:
            seen.add(lower)
            result.append(lower)
    return result


async def get_or_create_hashtag(db, tag):
    """Busca ou cria uma hashtag."""
    tag = tag.lower()
    result = await db.prepare(
        "SELECT * FROM hashtag WHERE tag = ?"
    ).bind(tag).first()
    if result:
        return safe_dict(result)
    # Criar nova
    new_result = await db.prepare("""
        INSERT INTO hashtag (tag, count_uso, created_at)
        VALUES (?, 1, datetime('now'))
        RETURNING id
    """).bind(tag).first()
    if new_result:
        new_id = safe_get(new_result, 'id')
        return {'id': new_id, 'tag': tag, 'count_uso': 1}
    return None


async def process_hashtags(db, text, tipo, item_id):
    """Processa hashtags em um texto e cria registros."""
    tags = extract_hashtags(text)
    for tag in tags:
        hashtag = await get_or_create_hashtag(db, tag)
        if hashtag:
            try:
                # Adicionar item à hashtag
                await db.prepare("""
                    INSERT OR IGNORE INTO hashtag_item (hashtag_id, tipo, item_id, created_at)
                    VALUES (?, ?, ?, datetime('now'))
                """).bind(hashtag['id'], tipo, item_id).run()
                # Incrementar contador
                await db.prepare(
                    "UPDATE hashtag SET count_uso = count_uso + 1 WHERE id = ?"
                ).bind(hashtag['id']).run()
            except Exception:
                pass
    return tags


async def get_trending_hashtags(db, limit=10):
    """Busca hashtags mais populares."""
    results = await db.prepare("""
        SELECT * FROM hashtag
        ORDER BY count_uso DESC
        LIMIT ?
    """).bind(limit).all()
    return [safe_dict(r) for r in results.results] if results.results else []


async def search_by_hashtag(db, tag, tipo=None, limit=50, offset=0):
    """Busca posts/comentários por hashtag."""
    tag = tag.lower().replace('#', '')
    
    # Query é a mesma para qualquer tipo (busca posts por padrão)
    results = await db.prepare("""
        SELECT p.*, u.nome as autor_nome, u.username as autor_username, u.foto_perfil as autor_foto
        FROM hashtag_item hi
        JOIN hashtag h ON hi.hashtag_id = h.id
        JOIN post p ON hi.item_id = p.id AND hi.tipo = 'post'
        LEFT JOIN user u ON p.usuario_id = u.id
        WHERE h.tag = ? AND p.is_deleted = 0
        ORDER BY p.data DESC
        LIMIT ? OFFSET ?
    """).bind(tag, limit, offset).all()
    
    return [safe_dict(r) for r in results.results] if results.results else []


# ============================================================================
# EMOJIS PERSONALIZADOS NÃO-BINÁRIOS
# ============================================================================

async def create_emoji_custom(db, codigo, nome, imagem_url, descricao=None, categoria='geral', created_by=None):
    """Cria um emoji personalizado."""
    # Formatar código: remover espaços, adicionar colons se não tiver
    codigo = codigo.strip().lower().replace(' ', '_')
    if not codigo.startswith(':'):
        codigo = f':{codigo}:'
    elif not codigo.endswith(':'):
        codigo = f'{codigo}:'
    
    try:
        result = await db.prepare("""
            INSERT INTO emoji_custom (codigo, nome, imagem_url, descricao, categoria, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
            RETURNING id
        """).bind(codigo, nome, imagem_url, descricao, categoria, created_by).first()
        return safe_get(result, 'id')
    except Exception:
        return None


async def get_emojis_custom(db, categoria=None, ativo_only=True):
    """Busca emojis personalizados."""
    if categoria and ativo_only:
        results = await db.prepare("""
            SELECT * FROM emoji_custom
            WHERE categoria = ? AND ativo = 1
            ORDER BY ordem, nome
        """).bind(categoria).all()
    elif categoria:
        results = await db.prepare("""
            SELECT * FROM emoji_custom
            WHERE categoria = ?
            ORDER BY ordem, nome
        """).bind(categoria).all()
    elif ativo_only:
        results = await db.prepare("""
            SELECT * FROM emoji_custom
            WHERE ativo = 1
            ORDER BY categoria, ordem, nome
        """).all()
    else:
        results = await db.prepare("""
            SELECT * FROM emoji_custom
            ORDER BY categoria, ordem, nome
        """).all()
    
    return [safe_dict(r) for r in results.results] if results.results else []


async def get_emoji_by_codigo(db, codigo):
    """Busca emoji por código."""
    result = await db.prepare(
        "SELECT * FROM emoji_custom WHERE codigo = ? AND ativo = 1"
    ).bind(codigo).first()
    return safe_dict(result) if result else None


async def update_emoji_custom(db, emoji_id, **kwargs):
    """Atualiza um emoji."""
    allowed = ['nome', 'descricao', 'imagem_url', 'categoria', 'ordem', 'ativo']
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    
    if not updates:
        return False
    
    # Construir query com placeholders
    set_parts = []
    values = []
    for key, value in updates.items():
        set_parts.append(f"{key} = ?")
        values.append(value)
    
    values.append(emoji_id)
    
    query = f"UPDATE emoji_custom SET {', '.join(set_parts)} WHERE id = ?"
    await db.prepare(query).bind(*values).run()
    return True


async def delete_emoji_custom(db, emoji_id):
    """Deleta um emoji."""
    await db.prepare("DELETE FROM emoji_custom WHERE id = ?").bind(emoji_id).run()
    return True


async def get_emoji_categories(db):
    """Busca categorias de emojis."""
    results = await db.prepare("""
        SELECT DISTINCT categoria, COUNT(*) as count
        FROM emoji_custom
        WHERE ativo = 1
        GROUP BY categoria
        ORDER BY categoria
    """).all()
    return [safe_dict(r) for r in results.results] if results.results else []


def escape_html(text):
    """Escapa caracteres HTML para prevenir XSS."""
    if not text:
        return text
    return (text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&#39;'))


def render_emojis_in_text(text, emojis_list):
    """Substitui códigos de emoji por imagens."""
    if not text or not emojis_list:
        return text
    
    for emoji in emojis_list:
        codigo = emoji['codigo']
        # Escapar valores para prevenir HTML injection
        safe_url = escape_html(emoji.get('imagem_url', ''))
        safe_nome = escape_html(emoji.get('nome', ''))
        img_tag = f'<img src="{safe_url}" alt="{safe_nome}" class="emoji-custom" style="width: 1.2em; height: 1.2em; vertical-align: middle;">'
        text = text.replace(codigo, img_tag)
    
    return text


# ============================================================================
# FEATURE FLAGS (para desativar funcionalidades temporariamente)
# ============================================================================

async def get_feature_flag(db, nome):
    """Verifica se uma funcionalidade está ativa."""
    result = await db.prepare(
        "SELECT ativo FROM feature_flag WHERE nome = ?"
    ).bind(nome).first()
    return bool(safe_get(result, 'ativo', 1)) if result else True


async def get_all_feature_flags(db):
    """Busca todas as feature flags."""
    results = await db.prepare(
        "SELECT * FROM feature_flag ORDER BY nome"
    ).all()
    return [safe_dict(r) for r in results.results] if results.results else []


async def update_feature_flag(db, nome, ativo, updated_by=None):
    """Atualiza uma feature flag."""
    await db.prepare("""
        UPDATE feature_flag 
        SET ativo = ?, updated_at = datetime('now'), updated_by = ?
        WHERE nome = ?
    """).bind(ativo, updated_by, nome).run()
    return True
