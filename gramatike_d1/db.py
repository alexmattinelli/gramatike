# gramatike_d1/db.py
# Database helpers para Cloudflare D1
# Este módulo fornece funções para interagir com o D1 SQLite
#
# NOTA: Renomeado de 'workers/' para 'gramatike_d1/' para evitar conflito
# com o módulo 'workers' built-in do Cloudflare Workers Python.
#
# ============================================================================
# IMPORTANTE: Prevenindo D1_TYPE_ERROR
# ============================================================================
#
# D1 não aceita JavaScript 'undefined' como valor de bind. Para prevenir erros
# D1_TYPE_ERROR, SEMPRE siga este padrão ao usar .bind():
#
# 1. Sanitize parâmetros com sanitize_params() ou sanitize_for_d1()
# 2. Chame to_d1_null() DIRETAMENTE dentro de .bind() para minimizar FFI crossings
#
# EXEMPLO CORRETO (RECOMENDADO):
#   s_usuario_id, s_conteudo = sanitize_params(usuario_id, conteudo)
#   await db.prepare("INSERT INTO ... VALUES (?, ?)").bind(
#       to_d1_null(s_usuario_id),
#       to_d1_null(s_conteudo)
#   ).run()
#
# ALTERNATIVA (para muitos parâmetros):
#   params = d1_params(usuario_id, conteudo)  # d1_params já faz sanitize + to_d1_null
#   await db.prepare("INSERT INTO ... VALUES (?, ?)").bind(*params).run()
#   # NOTA: Este padrão pode causar 2 FFI crossings em alguns casos
#
# NUNCA faça:
#   # ❌ Usar valores não sanitizados pode causar D1_TYPE_ERROR
#   await db.prepare("...").bind(usuario_id, conteudo).run()
#   
#   # ❌ Armazenar to_d1_null() em variáveis pode causar FFI boundary issues
#   d1_value = to_d1_null(s_usuario_id)
#   await db.prepare("...").bind(d1_value).run()
#
# ============================================================================

import json
import sys
import traceback
from datetime import datetime, timedelta
import hashlib
import secrets

# Import JavaScript console for proper log levels in Cloudflare Workers
# console.log = info level, console.warn = warning, console.error = error
# Also import JavaScript's null to properly handle None values in D1 queries
try:
    from js import console, null as JS_NULL
    _IN_PYODIDE = True
except ImportError:
    # Fallback for local testing - create a mock console
    class MockConsole:
        def log(self, *args): print(*args)
        def info(self, *args): print(*args)
        def warn(self, *args): print(*args, file=sys.stderr)
        def error(self, *args): print(*args, file=sys.stderr)
    console = MockConsole()
    JS_NULL = None  # In non-Pyodide environments, use Python None
    _IN_PYODIDE = False


def to_d1_null(value):
    """Converts Python None and JavaScript undefined to JavaScript null for D1 queries.
    
    ⚠️ CRITICAL: ALWAYS use this function to wrap parameters before .bind()
    
    In the Pyodide/Cloudflare Workers environment, Python None is converted to
    JavaScript undefined when crossing the FFI boundary, which D1 cannot handle.
    This function converts None and undefined to JavaScript null, which D1 accepts as SQL NULL.
    
    Even non-None values should be wrapped with this function as a safety measure,
    as values can unexpectedly become undefined when crossing the FFI boundary.
    
    Args:
        value: The value to convert (None/undefined is converted to JS null, others pass through)
        
    Returns:
        JavaScript null if value is None or undefined (in Pyodide), otherwise the original value
        
    Example:
        # ALWAYS wrap ALL bind parameters:
        d1_user_id = to_d1_null(sanitized_user_id)
        d1_content = to_d1_null(sanitized_content)
        await db.prepare("INSERT INTO post (user_id, content) VALUES (?, ?)")
            .bind(d1_user_id, d1_content).run()
    """
    if not _IN_PYODIDE:
        # In non-Pyodide environments, just return None for None values
        if value is None:
            return None
        return value
    
    # In Pyodide environment, perform comprehensive checks for None and undefined
    
    # Check 1: Python None (identity check)
    if value is None:
        return JS_NULL
    
    # Check 2: JavaScript undefined by string representation
    # This is the most reliable check as undefined always converts to 'undefined' string
    try:
        str_repr = str(value)
        if str_repr == 'undefined':
            console.warn(f"[to_d1_null] Detected undefined value (str check), converting to JS_NULL")
            return JS_NULL
    except Exception as e:
        # If str() fails, it's likely a problematic JavaScript object
        console.warn(f"[to_d1_null] str() failed on value, returning JS_NULL: {e}")
        return JS_NULL
    
    # Check 3: Type name matches known undefined patterns
    # Only check for exact JavaScript undefined type names to avoid false positives
    try:
        type_name = type(value).__name__
        if type_name in ('JsUndefined', 'undefined'):
            console.warn(f"[to_d1_null] Detected JS undefined type: {type_name}, converting to JS_NULL")
            return JS_NULL
    except Exception:
        pass
    
    # If all checks pass, return the value as is
    return value

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
    
    All values in the resulting dict are sanitized to convert JavaScript
    'undefined' to Python None.
    """
    if result is None:
        return None
    
    # Check if it's a JsProxy object (from Pyodide/Cloudflare Workers)
    result_type = type(result).__name__
    
    def _sanitize_value(val):
        """Sanitize a single value from JsProxy conversion."""
        if val is None:
            return None
        # Check for JsProxy wrapping undefined
        if hasattr(val, 'to_py'):
            try:
                str_val = str(val)
                if str_val == 'undefined':
                    return None
                return val.to_py()
            except Exception:
                return None
        return val
    
    # Method 1: Try to_py() for JsProxy objects (Pyodide's conversion method)
    if hasattr(result, 'to_py'):
        try:
            converted = result.to_py()
            if isinstance(converted, dict):
                # Sanitize all values in the converted dict
                return {k: _sanitize_value(v) if hasattr(v, 'to_py') else v for k, v in converted.items()}
            # If to_py() returns something else, try dict() on it
            if converted:
                d = dict(converted)
                return {k: _sanitize_value(v) if hasattr(v, 'to_py') else v for k, v in d.items()}
            return None
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
            return {k: _sanitize_value(result[k]) for k in keys_list}
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
                return {k: _sanitize_value(result[k]) for k in keys}
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


# Maximum recursion depth for sanitize_for_d1 function
_SANITIZE_MAX_DEPTH = 3

# Pyodide module prefixes for JsProxy detection
_PYODIDE_MODULE_PREFIXES = ('pyodide.', 'pyodide', 'js')


def _is_pyodide_module(module_name):
    """Check if a module name matches known Pyodide module patterns."""
    return any(
        module_name.startswith(prefix) if prefix.endswith('.') else module_name == prefix
        for prefix in _PYODIDE_MODULE_PREFIXES
    )


def _is_js_proxy(value):
    """Check if a value is a JavaScript proxy object from Pyodide.
    
    Returns True if the value is a JsProxy or similar object that wraps
    JavaScript values in the Pyodide/Cloudflare Workers environment.
    """
    value_type = type(value)
    type_name = value_type.__name__
    
    # JsProxy is the exact type used by Pyodide for JS objects
    if type_name == 'JsProxy':
        return True
    
    # Also check for objects with to_py that are from pyodide module
    if hasattr(value, 'to_py'):
        module = getattr(value_type, '__module__', '')
        if _is_pyodide_module(module):
            return True
    
    return False


def sanitize_for_d1(value, _depth=0):
    """Sanitizes a value before passing it to D1 SQL queries.
    
    This handles the case where JavaScript 'undefined' values might be passed
    instead of Python None, which causes D1_TYPE_ERROR.
    
    In the Pyodide/Cloudflare Workers environment, accessing a non-existent
    key from a JsProxy object returns JavaScript's undefined, which D1
    cannot handle. This function converts such values to Python None.
    
    Args:
        value: The value to sanitize
        _depth: Internal recursion depth counter
        
    Returns:
        A Python-native value (str, int, float, None) safe for D1 queries.
        Returns None for any undefined, null, or problematic values.
    """
    # Prevent infinite recursion
    if _depth >= _SANITIZE_MAX_DEPTH:
        console.warn(f"[sanitize_for_d1] Max recursion depth reached, returning None")
        return None
    
    if value is None:
        return None
    
    # CRITICAL: Check string representation FIRST before any other checks
    # This catches cases where the value is 'undefined' as a string or JsProxy
    try:
        str_repr = str(value)
        if str_repr == 'undefined' or str_repr == 'null':
            return None
    except Exception:
        # Objects that fail str() conversion are likely problematic JavaScript objects
        # In normal Python, str() works on almost any object, so this indicates
        # a JavaScript-specific issue in the Pyodide environment
        console.warn(f"[sanitize_for_d1] Failed to get string representation for type {type(value).__name__}")
        return None
    
    # Check type name - some JsProxy types have specific names
    try:
        type_name = type(value).__name__
        if type_name in ('JsUndefined', 'JsNull', 'undefined', 'null', 'JsException'):
            return None
        # Safe Js* types that can be converted to Python values
        SAFE_JS_TYPES = ('JsProxy', 'JsArray', 'JsObject')
        # Check for any type starting with 'Js' that might be problematic
        if type_name.startswith('Js') and type_name not in SAFE_JS_TYPES:
            # For non-standard Js types, try to convert or return None
            if hasattr(value, 'to_py'):
                try:
                    py_value = value.to_py()
                    if py_value is None or str(py_value) == 'undefined':
                        return None
                    return py_value
                except Exception:
                    return None
            return None
    except Exception:
        pass
    
    # Check for JavaScript undefined (appears as a JsProxy with undefined type)
    try:
        if _is_js_proxy(value):
            # Try to convert to Python - undefined converts to None
            if hasattr(value, 'to_py'):
                try:
                    py_value = value.to_py()
                    # to_py() on undefined returns None
                    if py_value is None:
                        return None
                    # Check if the converted value is also undefined string
                    if str(py_value) == 'undefined':
                        return None
                    # After successful conversion, the value should be a Python native type
                    # Only recurse if still a JsProxy-like object (shouldn't normally happen)
                    if _is_js_proxy(py_value):
                        return sanitize_for_d1(py_value, _depth + 1)
                    return py_value
                except Exception:
                    # If conversion fails (including JsException), treat as None
                    return None
            
            # If we reach here, we have a JsProxy-like object but couldn't convert it
            # Return None to be safe
            return None
        
        # Check if value has to_py method even if not detected as JsProxy
        # This handles edge cases where type detection fails
        if hasattr(value, 'to_py') and callable(getattr(value, 'to_py')):
            try:
                py_value = value.to_py()
                if py_value is None or str(py_value) == 'undefined':
                    return None
                return py_value
            except Exception:
                return None
        
        # Final validation: ensure the value is a type that D1 can handle
        # D1 supports: str, int, float, bytes, None
        if isinstance(value, (str, int, float, bytes, bool)):
            return value
        
        # For other types, try to convert to a safe representation
        # This catches any remaining edge cases
        try:
            if isinstance(value, (list, dict, tuple)):
                # Complex types like list/dict/tuple cannot be directly passed to D1.
                # They should be JSON serialized by the caller if needed.
                # We log a warning and return None to prevent D1_TYPE_ERROR.
                # Callers expecting to store complex data should use json.dumps() first.
                console.warn(f"[sanitize_for_d1] Complex type {type(value).__name__} passed, returning None. Use json.dumps() to serialize complex data.")
                return None
            # Last resort: convert to string if it's not a known safe type
            return str(value)
        except Exception:
            return None
        
    except Exception as e:
        # Log the error for debugging but return None to prevent D1_TYPE_ERROR
        console.warn(f"[sanitize_for_d1] Unexpected error converting value: {e}")
        return None


def sanitize_params(*args):
    """Sanitizes multiple parameters for D1 SQL queries.
    
    Returns a tuple of sanitized values. Note that None values are returned as
    Python None; use d1_params() instead if you need None converted to JavaScript
    null for D1 queries.
    """
    return tuple(sanitize_for_d1(arg) for arg in args)


def d1_params(*args):
    """Sanitizes parameters for D1 SQL queries, converting None to JavaScript null.
    
    ⚠️ RECOMMENDED: Use this function to prepare ALL parameters for .bind()
    
    This is the preferred function for preparing parameters for D1's .bind() method.
    It sanitizes all values using sanitize_for_d1() and then converts any Python None
    values to JavaScript null, which D1 accepts as SQL NULL.
    
    This function combines sanitize_for_d1() and to_d1_null() in a single call,
    making it easier to prepare multiple parameters safely.
    
    Args:
        *args: Values to sanitize for D1 queries
        
    Returns:
        A tuple of sanitized values where None values are converted to JS null
        
    Example:
        # Prepare all parameters in one call:
        params = d1_params(usuario_id, conteudo, imagem)
        await db.prepare("INSERT INTO post (user_id, content, image) VALUES (?, ?, ?)")
            .bind(*params).run()
    """
    return tuple(to_d1_null(sanitize_for_d1(arg)) for arg in args)


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
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_user_id = sanitize_for_d1(user_id)
    if s_user_id is None:
        return None
    
    # Use d1_params to properly handle FFI boundary issues
    params = d1_params(s_user_id)
    result = await db.prepare(
        "SELECT * FROM user WHERE id = ?"
    ).bind(*params).first()
    if result:
        return safe_dict(result)
    return None


async def get_user_by_username(db, username):
    """Busca ê usuárie por username."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_username = sanitize_for_d1(username)
    if s_username is None:
        return None
    
    try:
        # Use d1_params to properly handle FFI boundary issues
        params = d1_params(s_username)
        result = await db.prepare(
            "SELECT * FROM user WHERE username = ?"
        ).bind(*params).first()
        # Use console.log for debug/info messages
        console.log(f"[get_user_by_username] Query result for '{s_username}': {result}, type: {type(result)}")
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
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_email = sanitize_for_d1(email)
    if s_email is None:
        return None
    
    # Use d1_params to properly handle FFI boundary issues
    params = d1_params(s_email)
    result = await db.prepare(
        "SELECT * FROM user WHERE email = ?"
    ).bind(*params).first()
    if result:
        return safe_dict(result)
    return None


async def create_user(db, username, email, password, nome=None):
    """Cria ume nove usuárie."""
    hashed = hash_password(password)
    # Sanitize all parameters to prevent D1_TYPE_ERROR from undefined values
    s_username, s_email, s_hashed, s_nome = sanitize_params(username, email, hashed, nome)
    
    # Call to_d1_null() directly in bind() to prevent FFI boundary issues
    # The enhanced to_d1_null() now handles all edge cases of undefined values
    result = await db.prepare("""
        INSERT INTO user (username, email, password, nome, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        RETURNING id
    """).bind(
        to_d1_null(s_username),
        to_d1_null(s_email),
        to_d1_null(s_hashed),
        to_d1_null(s_nome)
    ).first()
    return safe_get(result, 'id')


async def update_user_profile(db, user_id, **kwargs):
    """Atualiza o perfil de usuárie."""
    allowed = ['nome', 'bio', 'genero', 'pronome', 'foto_perfil', 'data_nascimento']
    # Sanitize values to prevent D1_TYPE_ERROR from undefined values
    updates = {k: sanitize_for_d1(v) for k, v in kwargs.items() if k in allowed}
    # Filter out None values after sanitization
    updates = {k: v for k, v in updates.items() if v is not None}
    if not updates:
        return False
    
    set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
    # Convert all values to D1-safe format (wrap with to_d1_null)
    s_user_id = sanitize_for_d1(user_id)
    values = [to_d1_null(v) for v in updates.values()] + [to_d1_null(s_user_id)]
    
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
    
    # Sanitize all parameters to prevent D1_TYPE_ERROR from undefined values
    s_user_id, s_token, s_expires_at, s_user_agent, s_ip_address = sanitize_params(
        user_id, token, expires_at, user_agent, ip_address
    )
    
    # Call to_d1_null() directly in bind() to prevent FFI boundary issues
    # The enhanced to_d1_null() now handles all edge cases of undefined values
    await db.prepare("""
        INSERT INTO user_session (user_id, token, expires_at, user_agent, ip_address)
        VALUES (?, ?, ?, ?, ?)
    """).bind(
        to_d1_null(s_user_id),
        to_d1_null(s_token),
        to_d1_null(s_expires_at),
        to_d1_null(s_user_agent),
        to_d1_null(s_ip_address)
    ).run()
    
    return token


async def get_session(db, token):
    """Busca sessão pelo token."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_token = sanitize_for_d1(token)
    if s_token is None:
        return None
    
    # Use d1_params to properly handle FFI boundary issues
    params = d1_params(s_token)
    result = await db.prepare("""
        SELECT s.*, u.username, u.email, u.is_admin, u.is_superadmin, u.is_banned
        FROM user_session s
        JOIN user u ON s.user_id = u.id
        WHERE s.token = ? AND s.expires_at > datetime('now')
    """).bind(*params).first()
    if result:
        return safe_dict(result)
    return None


async def delete_session(db, token):
    """Remove uma sessão (logout)."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_token = sanitize_for_d1(token)
    if s_token is None:
        return
    
    # Use d1_params to properly handle FFI boundary issues
    params = d1_params(s_token)
    await db.prepare(
        "DELETE FROM user_session WHERE token = ?"
    ).bind(*params).run()


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
    # Sanitize all parameters to prevent D1_TYPE_ERROR from undefined values
    s_page = sanitize_for_d1(page) or 1
    s_per_page = sanitize_for_d1(per_page) or 20
    s_user_id = sanitize_for_d1(user_id)
    offset = (s_page - 1) * s_per_page
    
    # Build query with proper parameterization
    # Use d1_params to ensure all bind values are D1-safe (handles None -> JS null conversion)
    if s_user_id and not include_deleted:
        params = d1_params(s_user_id, s_per_page, offset)
        result = await db.prepare("""
            SELECT p.*, u.username, u.foto_perfil,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                   (SELECT COUNT(*) FROM comentario WHERE post_id = p.id) as comment_count
            FROM post p
            LEFT JOIN user u ON p.usuario_id = u.id
            WHERE p.is_deleted = 0 AND p.usuario_id = ?
            ORDER BY p.data DESC
            LIMIT ? OFFSET ?
        """).bind(*params).all()
    elif s_user_id:
        params = d1_params(s_user_id, s_per_page, offset)
        result = await db.prepare("""
            SELECT p.*, u.username, u.foto_perfil,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                   (SELECT COUNT(*) FROM comentario WHERE post_id = p.id) as comment_count
            FROM post p
            LEFT JOIN user u ON p.usuario_id = u.id
            WHERE p.usuario_id = ?
            ORDER BY p.data DESC
            LIMIT ? OFFSET ?
        """).bind(*params).all()
    elif not include_deleted:
        params = d1_params(s_per_page, offset)
        result = await db.prepare("""
            SELECT p.*, u.username, u.foto_perfil,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                   (SELECT COUNT(*) FROM comentario WHERE post_id = p.id) as comment_count
            FROM post p
            LEFT JOIN user u ON p.usuario_id = u.id
            WHERE p.is_deleted = 0
            ORDER BY p.data DESC
            LIMIT ? OFFSET ?
        """).bind(*params).all()
    else:
        params = d1_params(s_per_page, offset)
        result = await db.prepare("""
            SELECT p.*, u.username, u.foto_perfil,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                   (SELECT COUNT(*) FROM comentario WHERE post_id = p.id) as comment_count
            FROM post p
            LEFT JOIN user u ON p.usuario_id = u.id
            ORDER BY p.data DESC
            LIMIT ? OFFSET ?
        """).bind(*params).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_post_by_id(db, post_id):
    """Busca post por ID."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_post_id = sanitize_for_d1(post_id)
    if s_post_id is None:
        return None
    
    # Use d1_params to ensure bind value is D1-safe
    params = d1_params(s_post_id)
    result = await db.prepare("""
        SELECT p.*, u.username, u.foto_perfil,
               (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
               (SELECT COUNT(*) FROM comentario WHERE post_id = p.id) as comment_count
        FROM post p
        LEFT JOIN user u ON p.usuario_id = u.id
        WHERE p.id = ?
    """).bind(*params).first()
    if result:
        return safe_dict(result)
    return None


async def create_post(db, usuario_id, conteudo, imagem=None):
    """Cria um novo post.
    
    Args:
        db: D1 database connection
        usuario_id: ID of the user creating the post
        conteudo: Post content text
        imagem: Optional image URL/path (can be None)
    
    Returns:
        The ID of the created post, or None if creation failed
    """
    # Validate required fields before processing
    # Use sanitize_for_d1 to handle undefined/JsProxy values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_conteudo = sanitize_for_d1(conteudo)
    s_imagem = sanitize_for_d1(imagem)
    
    if s_usuario_id is None:
        console.error("[create_post] usuario_id is None after sanitization")
        return None
    if s_conteudo is None:
        console.error("[create_post] conteudo is None after sanitization")
        return None
    
    # Call to_d1_null() directly in bind() to prevent D1_TYPE_ERROR
    # The enhanced to_d1_null() now handles all edge cases of undefined values
    result = await db.prepare("""
        INSERT INTO post (usuario_id, usuario, conteudo, imagem, data)
        SELECT ?, username, ?, ?, datetime('now')
        FROM user WHERE id = ?
        RETURNING id
    """).bind(
        to_d1_null(s_usuario_id),  # for usuario_id column
        to_d1_null(s_conteudo),
        to_d1_null(s_imagem),
        to_d1_null(s_usuario_id)   # for WHERE clause (to fetch username)
    ).first()
    return safe_get(result, 'id')


async def delete_post(db, post_id, deleted_by=None):
    """Soft delete de um post.
    
    Args:
        db: D1 database connection
        post_id: ID of the post to delete
        deleted_by: Optional ID of the user who deleted the post
    """
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_post_id, s_deleted_by = sanitize_params(post_id, deleted_by)
    
    # Use d1_params to properly handle FFI boundary issues
    params = d1_params(s_deleted_by, s_post_id)
    await db.prepare("""
        UPDATE post SET is_deleted = 1, deleted_at = datetime('now'), deleted_by = ?
        WHERE id = ?
    """).bind(*params).run()


async def like_post(db, user_id, post_id):
    """Curte um post."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_user_id, s_post_id = sanitize_params(user_id, post_id)
    
    # Use d1_params to properly handle FFI boundary issues
    params = d1_params(s_user_id, s_post_id)
    try:
        await db.prepare("""
            INSERT INTO post_likes (user_id, post_id) VALUES (?, ?)
        """).bind(*params).run()
        return True
    except:
        return False


async def unlike_post(db, user_id, post_id):
    """Remove curtida de um post."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_user_id, s_post_id = sanitize_params(user_id, post_id)
    
    # Use d1_params to properly handle FFI boundary issues
    params = d1_params(s_user_id, s_post_id)
    await db.prepare("""
        DELETE FROM post_likes WHERE user_id = ? AND post_id = ?
    """).bind(*params).run()


async def has_liked(db, user_id, post_id):
    """Verifica se usuárie curtiu o post."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_user_id, s_post_id = sanitize_params(user_id, post_id)
    if s_user_id is None or s_post_id is None:
        return False
    
    # Use d1_params to properly handle FFI boundary issues
    params = d1_params(s_user_id, s_post_id)
    result = await db.prepare("""
        SELECT 1 FROM post_likes WHERE user_id = ? AND post_id = ?
    """).bind(*params).first()
    return result is not None


# ============================================================================
# QUERIES - COMENTÁRIOS
# ============================================================================

async def get_comments(db, post_id, page=1, per_page=50):
    """Lista comentários de um post."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_post_id = sanitize_for_d1(post_id)
    s_page = sanitize_for_d1(page) or 1
    s_per_page = sanitize_for_d1(per_page) or 50
    if s_post_id is None:
        return []
    offset = (s_page - 1) * s_per_page
    
    result = await db.prepare("""
        SELECT c.*, u.username, u.foto_perfil
        FROM comentario c
        LEFT JOIN user u ON c.usuario_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.data ASC
        LIMIT ? OFFSET ?
    """).bind(s_post_id, s_per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def create_comment(db, post_id, usuario_id, conteudo):
    """Cria um novo comentário."""
    # Sanitize all parameters to prevent D1_TYPE_ERROR from undefined values
    s_post_id, s_usuario_id, s_conteudo = sanitize_params(post_id, usuario_id, conteudo)
    
    # Convert Python None to JavaScript null for D1
    # Wrap ALL parameters to prevent undefined from crossing the FFI boundary
    d1_post_id = to_d1_null(s_post_id)
    d1_usuario_id = to_d1_null(s_usuario_id)
    d1_conteudo = to_d1_null(s_conteudo)
    
    result = await db.prepare("""
        INSERT INTO comentario (post_id, usuario_id, conteudo, data)
        VALUES (?, ?, ?, datetime('now'))
        RETURNING id
    """).bind(d1_post_id, d1_usuario_id, d1_conteudo).first()
    return safe_get(result, 'id')


# ============================================================================
# QUERIES - SEGUIDORIES
# ============================================================================

async def follow_user(db, seguidore_id, seguide_id):
    """Seguir ume usuárie."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_seguidore_id, s_seguide_id = sanitize_params(seguidore_id, seguide_id)
    if s_seguidore_id == s_seguide_id:
        return False
    
    # Convert Python None to JavaScript null for D1
    # Wrap ALL parameters to prevent undefined from crossing the FFI boundary
    d1_seguidore_id = to_d1_null(s_seguidore_id)
    d1_seguide_id = to_d1_null(s_seguide_id)
    
    try:
        await db.prepare("""
            INSERT INTO seguidories (seguidore_id, seguide_id) VALUES (?, ?)
        """).bind(d1_seguidore_id, d1_seguide_id).run()
        return True
    except:
        return False


async def unfollow_user(db, seguidore_id, seguide_id):
    """Deixar de seguir ume usuárie."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_seguidore_id, s_seguide_id = sanitize_params(seguidore_id, seguide_id)
    
    # Convert Python None to JavaScript null for D1
    # Wrap ALL parameters to prevent undefined from crossing the FFI boundary
    d1_seguidore_id = to_d1_null(s_seguidore_id)
    d1_seguide_id = to_d1_null(s_seguide_id)
    
    await db.prepare("""
        DELETE FROM seguidories WHERE seguidore_id = ? AND seguide_id = ?
    """).bind(d1_seguidore_id, d1_seguide_id).run()


async def is_following(db, seguidore_id, seguide_id):
    """Verifica se está seguindo."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_seguidore_id, s_seguide_id = sanitize_params(seguidore_id, seguide_id)
    if s_seguidore_id is None or s_seguide_id is None:
        return False
    result = await db.prepare("""
        SELECT 1 FROM seguidories WHERE seguidore_id = ? AND seguide_id = ?
    """).bind(s_seguidore_id, s_seguide_id).first()
    return result is not None


async def get_followers(db, user_id):
    """Lista seguidories de usuárie."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_user_id = sanitize_for_d1(user_id)
    if s_user_id is None:
        return []
    result = await db.prepare("""
        SELECT u.id, u.username, u.nome, u.foto_perfil
        FROM seguidories s
        JOIN user u ON s.seguidore_id = u.id
        WHERE s.seguide_id = ?
    """).bind(s_user_id).all()
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_following(db, user_id):
    """Lista quem ê usuárie segue."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_user_id = sanitize_for_d1(user_id)
    if s_user_id is None:
        return []
    result = await db.prepare("""
        SELECT u.id, u.username, u.nome, u.foto_perfil
        FROM seguidories s
        JOIN user u ON s.seguide_id = u.id
        WHERE s.seguidore_id = ?
    """).bind(s_user_id).all()
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - CONTEÚDO EDUCACIONAL
# ============================================================================

async def get_edu_contents(db, tipo=None, page=1, per_page=20):
    """Lista conteúdos educacionais."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_tipo = sanitize_for_d1(tipo)
    s_page = sanitize_for_d1(page) or 1
    s_per_page = sanitize_for_d1(per_page) or 20
    offset = (s_page - 1) * s_per_page
    
    if s_tipo:
        result = await db.prepare("""
            SELECT e.*, u.username as author_name, t.nome as topic_name
            FROM edu_content e
            LEFT JOIN user u ON e.author_id = u.id
            LEFT JOIN edu_topic t ON e.topic_id = t.id
            WHERE tipo = ?
            ORDER BY e.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(s_tipo, s_per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT e.*, u.username as author_name, t.nome as topic_name
            FROM edu_content e
            LEFT JOIN user u ON e.author_id = u.id
            LEFT JOIN edu_topic t ON e.topic_id = t.id
            ORDER BY e.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(s_per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_edu_content_by_id(db, content_id):
    """Busca conteúdo educacional por ID."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_content_id = sanitize_for_d1(content_id)
    if s_content_id is None:
        return None
    result = await db.prepare("""
        SELECT e.*, u.username as author_name, t.nome as topic_name
        FROM edu_content e
        LEFT JOIN user u ON e.author_id = u.id
        LEFT JOIN edu_topic t ON e.topic_id = t.id
        WHERE e.id = ?
    """).bind(s_content_id).first()
    if result:
        return safe_dict(result)
    return None


async def search_edu_contents(db, query, tipo=None):
    """Pesquisa conteúdos educacionais."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_query = sanitize_for_d1(query)
    s_tipo = sanitize_for_d1(tipo)
    if s_query is None:
        return []
    search_term = f"%{s_query}%"
    
    if s_tipo:
        result = await db.prepare("""
            SELECT e.*, u.username as author_name
            FROM edu_content e
            LEFT JOIN user u ON e.author_id = u.id
            WHERE (e.titulo LIKE ? OR e.resumo LIKE ? OR e.corpo LIKE ?)
            AND tipo = ?
            ORDER BY e.created_at DESC
            LIMIT 50
        """).bind(search_term, search_term, search_term, s_tipo).all()
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
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_topic_id = sanitize_for_d1(topic_id)
    s_section_id = sanitize_for_d1(section_id)
    
    if s_topic_id and s_section_id:
        result = await db.prepare("""
            SELECT q.*, t.nome as topic_name, s.nome as section_name
            FROM exercise_question q
            LEFT JOIN exercise_topic t ON q.topic_id = t.id
            LEFT JOIN exercise_section s ON q.section_id = s.id
            WHERE q.topic_id = ? AND q.section_id = ?
            ORDER BY q.created_at DESC
        """).bind(s_topic_id, s_section_id).all()
    elif s_topic_id:
        result = await db.prepare("""
            SELECT q.*, t.nome as topic_name, s.nome as section_name
            FROM exercise_question q
            LEFT JOIN exercise_topic t ON q.topic_id = t.id
            LEFT JOIN exercise_section s ON q.section_id = s.id
            WHERE q.topic_id = ?
            ORDER BY q.created_at DESC
        """).bind(s_topic_id).all()
    elif s_section_id:
        result = await db.prepare("""
            SELECT q.*, t.nome as topic_name, s.nome as section_name
            FROM exercise_question q
            LEFT JOIN exercise_topic t ON q.topic_id = t.id
            LEFT JOIN exercise_section s ON q.section_id = s.id
            WHERE q.section_id = ?
            ORDER BY q.created_at DESC
        """).bind(s_section_id).all()
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
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_dynamic_id = sanitize_for_d1(dynamic_id)
    if s_dynamic_id is None:
        return None
    result = await db.prepare("""
        SELECT d.*, u.username as author_name
        FROM dynamic d
        LEFT JOIN user u ON d.created_by = u.id
        WHERE d.id = ?
    """).bind(s_dynamic_id).first()
    if result:
        return safe_dict(result)
    return None


async def get_dynamic_responses(db, dynamic_id):
    """Lista respostas de uma dinâmica."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_dynamic_id = sanitize_for_d1(dynamic_id)
    if s_dynamic_id is None:
        return []
    result = await db.prepare("""
        SELECT r.*, u.username
        FROM dynamic_response r
        LEFT JOIN user u ON r.usuario_id = u.id
        WHERE r.dynamic_id = ?
        ORDER BY r.created_at DESC
    """).bind(s_dynamic_id).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def submit_dynamic_response(db, dynamic_id, usuario_id, payload):
    """Submete resposta para uma dinâmica."""
    payload_json = json.dumps(payload) if isinstance(payload, dict) else payload
    
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_dynamic_id, s_usuario_id, s_payload_json = sanitize_params(dynamic_id, usuario_id, payload_json)
    
    # Convert Python None to JavaScript null for D1
    # Wrap ALL parameters to prevent undefined from crossing the FFI boundary
    d1_dynamic_id = to_d1_null(s_dynamic_id)
    d1_usuario_id = to_d1_null(s_usuario_id)
    d1_payload_json = to_d1_null(s_payload_json)
    
    result = await db.prepare("""
        INSERT INTO dynamic_response (dynamic_id, usuario_id, payload)
        VALUES (?, ?, ?)
        RETURNING id
    """).bind(d1_dynamic_id, d1_usuario_id, d1_payload_json).first()
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
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_area = sanitize_for_d1(area)
    
    # Build query based on conditions - using parameterized queries
    if s_area and show_on_edu and show_on_index:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND area = ? AND show_on_edu = 1 AND show_on_index = 1
            ORDER BY ordem, created_at DESC
        """).bind(s_area).all()
    elif s_area and show_on_edu:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND area = ? AND show_on_edu = 1
            ORDER BY ordem, created_at DESC
        """).bind(s_area).all()
    elif s_area and show_on_index:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND area = ? AND show_on_index = 1
            ORDER BY ordem, created_at DESC
        """).bind(s_area).all()
    elif show_on_edu and show_on_index:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND show_on_edu = 1 AND show_on_index = 1
            ORDER BY ordem, created_at DESC
        """).all()
    elif s_area:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND area = ?
            ORDER BY ordem, created_at DESC
        """).bind(s_area).all()
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
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_limit = sanitize_for_d1(limit) or 5
    result = await db.prepare("""
        SELECT n.*, u.username as author_name
        FROM edu_novidade n
        LEFT JOIN user u ON n.author_id = u.id
        ORDER BY n.created_at DESC
        LIMIT ?
    """).bind(s_limit).all()
    
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
    
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id, s_token, s_tipo, s_novo_email, s_expires_at = sanitize_params(
        usuario_id, token, tipo, novo_email, expires_at
    )
    
    # Convert Python None to JavaScript null for D1
    # Wrap ALL parameters to prevent undefined from crossing the FFI boundary
    d1_usuario_id = to_d1_null(s_usuario_id)
    d1_token = to_d1_null(s_token)
    d1_tipo = to_d1_null(s_tipo)
    d1_novo_email = to_d1_null(s_novo_email)
    d1_expires_at = to_d1_null(s_expires_at)
    
    if s_novo_email:
        await db.prepare("""
            INSERT INTO email_token (usuario_id, token, tipo, novo_email, expires_at)
            VALUES (?, ?, ?, ?, ?)
        """).bind(d1_usuario_id, d1_token, d1_tipo, d1_novo_email, d1_expires_at).run()
    else:
        await db.prepare("""
            INSERT INTO email_token (usuario_id, token, tipo, expires_at)
            VALUES (?, ?, ?, ?)
        """).bind(d1_usuario_id, d1_token, d1_tipo, d1_expires_at).run()
    
    return token


async def verify_email_token(db, token, tipo):
    """Verifica e retorna dados do token se válido."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_token, s_tipo = sanitize_params(token, tipo)
    result = await db.prepare("""
        SELECT * FROM email_token
        WHERE token = ? AND tipo = ? AND used = 0 AND expires_at > datetime('now')
    """).bind(s_token, s_tipo).first()
    
    if result:
        return safe_dict(result)
    return None


async def use_email_token(db, token):
    """Marca token como usado."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_token = sanitize_for_d1(token)
    
    # Wrap parameter to prevent D1_TYPE_ERROR
    d1_token = to_d1_null(s_token)
    
    await db.prepare("""
        UPDATE email_token SET used = 1, used_at = datetime('now')
        WHERE token = ?
    """).bind(d1_token).run()


async def confirm_user_email(db, usuario_id):
    """Confirma o email de usuárie."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    
    # Wrap parameter to prevent D1_TYPE_ERROR
    d1_usuario_id = to_d1_null(s_usuario_id)
    
    await db.prepare("""
        UPDATE user SET email_confirmed = 1, email_confirmed_at = datetime('now')
        WHERE id = ?
    """).bind(d1_usuario_id).run()


async def update_user_password(db, usuario_id, new_password):
    """Atualiza a senha de usuárie."""
    hashed = hash_password(new_password)
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_hashed, s_usuario_id = sanitize_params(hashed, usuario_id)
    
    # Wrap all parameters to prevent D1_TYPE_ERROR
    d1_hashed = to_d1_null(s_hashed)
    d1_usuario_id = to_d1_null(s_usuario_id)
    
    await db.prepare("""
        UPDATE user SET password = ?
        WHERE id = ?
    """).bind(d1_hashed, d1_usuario_id).run()


async def update_user_email(db, usuario_id, new_email):
    """Atualiza o email de usuárie."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_new_email, s_usuario_id = sanitize_params(new_email, usuario_id)
    
    # Wrap all parameters to prevent D1_TYPE_ERROR
    d1_new_email = to_d1_null(s_new_email)
    d1_usuario_id = to_d1_null(s_usuario_id)
    
    await db.prepare("""
        UPDATE user SET email = ?, email_confirmed = 0
        WHERE id = ?
    """).bind(d1_new_email, d1_usuario_id).run()


# ============================================================================
# QUERIES - NOTIFICAÇÕES
# ============================================================================

async def create_notification(db, usuario_id, tipo, titulo=None, mensagem=None, link=None,
                              from_usuario_id=None, post_id=None, comentario_id=None):
    """Cria uma notificação para usuárie."""
    # Sanitize parameters and convert None to JavaScript null for D1
    params = d1_params(usuario_id, tipo, titulo, mensagem, link, 
                       from_usuario_id, post_id, comentario_id)
    
    result = await db.prepare("""
        INSERT INTO notification 
        (usuario_id, tipo, titulo, mensagem, link, from_usuario_id, post_id, comentario_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING id
    """).bind(*params).first()
    return safe_get(result, 'id')


async def get_notifications(db, usuario_id, apenas_nao_lidas=False, page=1, per_page=20):
    """Lista notificações de usuárie."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_page = sanitize_for_d1(page) or 1
    s_per_page = sanitize_for_d1(per_page) or 20
    if s_usuario_id is None:
        return []
    offset = (s_page - 1) * s_per_page
    
    # Wrap all parameters to prevent D1_TYPE_ERROR
    d1_usuario_id = to_d1_null(s_usuario_id)
    d1_per_page = to_d1_null(s_per_page)
    d1_offset = to_d1_null(offset)
    
    if apenas_nao_lidas:
        result = await db.prepare("""
            SELECT n.*, u.username as from_username, u.foto_perfil as from_foto
            FROM notification n
            LEFT JOIN user u ON n.from_usuario_id = u.id
            WHERE n.usuario_id = ? AND n.lida = 0
            ORDER BY n.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(d1_usuario_id, d1_per_page, d1_offset).all()
    else:
        result = await db.prepare("""
            SELECT n.*, u.username as from_username, u.foto_perfil as from_foto
            FROM notification n
            LEFT JOIN user u ON n.from_usuario_id = u.id
            WHERE n.usuario_id = ?
            ORDER BY n.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(d1_usuario_id, d1_per_page, d1_offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def count_unread_notifications(db, usuario_id):
    """Conta notificações não lidas de usuárie."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    if s_usuario_id is None:
        return 0
    
    # Wrap parameter to prevent D1_TYPE_ERROR
    d1_usuario_id = to_d1_null(s_usuario_id)
    
    result = await db.prepare("""
        SELECT COUNT(*) as count FROM notification
        WHERE usuario_id = ? AND lida = 0
    """).bind(d1_usuario_id).first()
    return safe_get(result, 'count', 0)


async def mark_notification_read(db, notification_id, usuario_id):
    """Marca notificação como lida."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_notification_id, s_usuario_id = sanitize_params(notification_id, usuario_id)
    if s_notification_id is None or s_usuario_id is None:
        return
    
    # Wrap all parameters to prevent D1_TYPE_ERROR
    d1_notification_id = to_d1_null(s_notification_id)
    d1_usuario_id = to_d1_null(s_usuario_id)
    
    await db.prepare("""
        UPDATE notification SET lida = 1
        WHERE id = ? AND usuario_id = ?
    """).bind(d1_notification_id, d1_usuario_id).run()


async def mark_all_notifications_read(db, usuario_id):
    """Marca todas as notificações como lidas."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    if s_usuario_id is None:
        return
    
    # Wrap parameter to prevent D1_TYPE_ERROR
    d1_usuario_id = to_d1_null(s_usuario_id)
    
    await db.prepare("""
        UPDATE notification SET lida = 1
        WHERE usuario_id = ? AND lida = 0
    """).bind(d1_usuario_id).run()


# ============================================================================
# QUERIES - AMIGUES
# ============================================================================

async def send_friend_request(db, solicitante_id, destinatarie_id):
    """Envia pedido de amizade."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_solicitante_id, s_destinatarie_id = sanitize_params(solicitante_id, destinatarie_id)
    if s_solicitante_id is None or s_destinatarie_id is None:
        return None, "IDs inválidos"
    
    # Wrap all parameters to prevent D1_TYPE_ERROR
    d1_solicitante_id = to_d1_null(s_solicitante_id)
    d1_destinatarie_id = to_d1_null(s_destinatarie_id)
    
    # Verifica se já existe relação
    existing = await db.prepare("""
        SELECT * FROM amizade
        WHERE (usuario1_id = ? AND usuario2_id = ?)
           OR (usuario1_id = ? AND usuario2_id = ?)
    """).bind(d1_solicitante_id, d1_destinatarie_id, d1_destinatarie_id, d1_solicitante_id).first()
    
    if existing:
        return None, "Já existe uma solicitação de amizade"
    
    # Cria solicitação
    result = await db.prepare("""
        INSERT INTO amizade (usuario1_id, usuario2_id, solicitante_id, status)
        VALUES (?, ?, ?, 'pendente')
        RETURNING id
    """).bind(d1_solicitante_id, d1_destinatarie_id, d1_solicitante_id).first()
    
    # Notifica destinatárie
    await create_notification(db, s_destinatarie_id, 'amizade_pedido',
                              titulo='Novo pedido de amizade',
                              from_usuario_id=s_solicitante_id)
    
    return safe_get(result, 'id'), None


async def respond_friend_request(db, amizade_id, usuario_id, aceitar=True):
    """Responde a pedido de amizade."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_amizade_id, s_usuario_id = sanitize_params(amizade_id, usuario_id)
    if s_amizade_id is None or s_usuario_id is None:
        return False, "IDs inválidos"
    
    # Verifica se o pedido existe e é para este usuárie
    amizade = await db.prepare("""
        SELECT * FROM amizade
        WHERE id = ? AND status = 'pendente'
        AND (usuario1_id = ? OR usuario2_id = ?)
        AND solicitante_id != ?
    """).bind(s_amizade_id, s_usuario_id, s_usuario_id, s_usuario_id).first()
    
    if not amizade:
        return False, "Pedido não encontrado"
    
    status = 'aceita' if aceitar else 'recusada'
    await db.prepare("""
        UPDATE amizade SET status = ?, updated_at = datetime('now')
        WHERE id = ?
    """).bind(status, s_amizade_id).run()
    
    # Notifica solicitante
    solicitante_id = safe_get(amizade, 'solicitante_id')
    if aceitar and solicitante_id:
        await create_notification(db, solicitante_id, 'amizade_aceita',
                                  titulo='Pedido de amizade aceito!',
                                  from_usuario_id=s_usuario_id)
    
    return True, None


async def get_amigues(db, usuario_id):
    """Lista amigues de usuárie (amizades aceitas)."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    if s_usuario_id is None:
        return []
    result = await db.prepare("""
        SELECT u.id, u.username, u.nome, u.foto_perfil, a.created_at as amigues_desde
        FROM amizade a
        JOIN user u ON (
            (a.usuario1_id = ? AND a.usuario2_id = u.id)
            OR (a.usuario2_id = ? AND a.usuario1_id = u.id)
        )
        WHERE a.status = 'aceita'
        ORDER BY u.nome, u.username
    """).bind(s_usuario_id, s_usuario_id).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_pending_friend_requests(db, usuario_id):
    """Lista pedidos de amizade pendentes recebidos."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    if s_usuario_id is None:
        return []
    result = await db.prepare("""
        SELECT a.*, u.username, u.nome, u.foto_perfil
        FROM amizade a
        JOIN user u ON a.solicitante_id = u.id
        WHERE (a.usuario1_id = ? OR a.usuario2_id = ?)
        AND a.status = 'pendente'
        AND a.solicitante_id != ?
        ORDER BY a.created_at DESC
    """).bind(s_usuario_id, s_usuario_id, s_usuario_id).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def are_amigues(db, usuarie1_id, usuarie2_id):
    """Verifica se dois usuáries são amigues."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuarie1_id, s_usuarie2_id = sanitize_params(usuarie1_id, usuarie2_id)
    if s_usuarie1_id is None or s_usuarie2_id is None:
        return False
    result = await db.prepare("""
        SELECT 1 FROM amizade
        WHERE ((usuario1_id = ? AND usuario2_id = ?)
            OR (usuario1_id = ? AND usuario2_id = ?))
        AND status = 'aceita'
    """).bind(s_usuarie1_id, s_usuarie2_id, s_usuarie2_id, s_usuarie1_id).first()
    return result is not None


async def remove_amizade(db, usuario_id, amigue_id):
    """Remove amizade."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id, s_amigue_id = sanitize_params(usuario_id, amigue_id)
    if s_usuario_id is None or s_amigue_id is None:
        return
    
    # Convert Python None to JavaScript null for D1
    # Wrap ALL parameters to prevent undefined from crossing the FFI boundary
    d1_usuario_id = to_d1_null(s_usuario_id)
    d1_amigue_id = to_d1_null(s_amigue_id)
    
    await db.prepare("""
        DELETE FROM amizade
        WHERE ((usuario1_id = ? AND usuario2_id = ?)
            OR (usuario1_id = ? AND usuario2_id = ?))
        AND status = 'aceita'
    """).bind(d1_usuario_id, d1_amigue_id, d1_amigue_id, d1_usuario_id).run()


# ============================================================================
# QUERIES - DENÚNCIAS
# ============================================================================

async def create_report(db, post_id, usuario_id, motivo, category=None):
    """Cria uma denúncia de post."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_post_id, s_usuario_id, s_motivo, s_category = sanitize_params(post_id, usuario_id, motivo, category)
    
    # Convert Python None to JavaScript null for D1
    # Wrap ALL parameters to prevent undefined from crossing the FFI boundary
    d1_post_id = to_d1_null(s_post_id)
    d1_usuario_id = to_d1_null(s_usuario_id)
    d1_motivo = to_d1_null(s_motivo)
    d1_category = to_d1_null(s_category)
    
    result = await db.prepare("""
        INSERT INTO report (post_id, usuario_id, motivo, category)
        VALUES (?, ?, ?, ?)
        RETURNING id
    """).bind(d1_post_id, d1_usuario_id, d1_motivo, d1_category).first()
    return safe_get(result, 'id')


async def get_reports(db, apenas_pendentes=True, page=1, per_page=20):
    """Lista denúncias (para admin)."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_page = sanitize_for_d1(page) or 1
    s_per_page = sanitize_for_d1(per_page) or 20
    offset = (s_page - 1) * s_per_page
    
    if apenas_pendentes:
        result = await db.prepare("""
            SELECT r.*, p.conteudo as post_conteudo, u.username as reporter_username
            FROM report r
            LEFT JOIN post p ON r.post_id = p.id
            LEFT JOIN user u ON r.usuario_id = u.id
            WHERE r.resolved = 0
            ORDER BY r.data DESC
            LIMIT ? OFFSET ?
        """).bind(s_per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT r.*, p.conteudo as post_conteudo, u.username as reporter_username
            FROM report r
            LEFT JOIN post p ON r.post_id = p.id
            LEFT JOIN user u ON r.usuario_id = u.id
            ORDER BY r.data DESC
            LIMIT ? OFFSET ?
        """).bind(s_per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def resolve_report(db, report_id, resolver_id=None):
    """Resolve uma denúncia."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_report_id = sanitize_for_d1(report_id)
    if s_report_id is None:
        return
    await db.prepare("""
        UPDATE report SET resolved = 1, resolved_at = datetime('now')
        WHERE id = ?
    """).bind(s_report_id).run()


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
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id, s_nome, s_email, s_mensagem = sanitize_params(usuario_id, nome, email, mensagem)
    
    # Convert Python None to JavaScript null for D1
    # Wrap ALL parameters to prevent undefined from crossing the FFI boundary
    d1_usuario_id = to_d1_null(s_usuario_id)
    d1_nome = to_d1_null(s_nome)
    d1_email = to_d1_null(s_email)
    d1_mensagem = to_d1_null(s_mensagem)
    
    result = await db.prepare("""
        INSERT INTO support_ticket (usuario_id, nome, email, mensagem)
        VALUES (?, ?, ?, ?)
        RETURNING id
    """).bind(d1_usuario_id, d1_nome, d1_email, d1_mensagem).first()
    return safe_get(result, 'id')


async def get_support_tickets(db, status=None, page=1, per_page=20):
    """Lista tickets de suporte (para admin)."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_status = sanitize_for_d1(status)
    s_page = sanitize_for_d1(page) or 1
    s_per_page = sanitize_for_d1(per_page) or 20
    offset = (s_page - 1) * s_per_page
    
    if s_status:
        result = await db.prepare("""
            SELECT t.*, u.username
            FROM support_ticket t
            LEFT JOIN user u ON t.usuario_id = u.id
            WHERE t.status = ?
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(s_status, s_per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT t.*, u.username
            FROM support_ticket t
            LEFT JOIN user u ON t.usuario_id = u.id
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(s_per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_user_tickets(db, usuario_id):
    """Lista tickets de usuárie."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    if s_usuario_id is None:
        return []
    result = await db.prepare("""
        SELECT * FROM support_ticket
        WHERE usuario_id = ?
        ORDER BY created_at DESC
    """).bind(s_usuario_id).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def respond_ticket(db, ticket_id, resposta):
    """Responde a um ticket de suporte."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_ticket_id, s_resposta = sanitize_params(ticket_id, resposta)
    if s_ticket_id is None:
        return
    await db.prepare("""
        UPDATE support_ticket 
        SET resposta = ?, status = 'respondido', updated_at = datetime('now')
        WHERE id = ?
    """).bind(s_resposta, s_ticket_id).run()


async def close_ticket(db, ticket_id):
    """Fecha um ticket de suporte."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_ticket_id = sanitize_for_d1(ticket_id)
    if s_ticket_id is None:
        return
    await db.prepare("""
        UPDATE support_ticket 
        SET status = 'fechado', updated_at = datetime('now')
        WHERE id = ?
    """).bind(s_ticket_id).run()


# ============================================================================
# QUERIES - DIVULGAÇÃO/PROMOÇÕES
# ============================================================================

async def create_divulgacao(db, area, titulo, texto=None, link=None, imagem=None, 
                            show_on_edu=True, show_on_index=True, author_id=None):
    """Cria uma divulgação."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_area, s_titulo, s_texto, s_link, s_imagem = sanitize_params(area, titulo, texto, link, imagem)
    
    # Convert Python None to JavaScript null for D1
    d1_texto = to_d1_null(s_texto)
    d1_link = to_d1_null(s_link)
    d1_imagem = to_d1_null(s_imagem)
    
    # Nota: A tabela divulgacao não tem coluna author_id diretamente, 
    # mas podemos vincular via edu_content_id ou post_id se necessário
    result = await db.prepare("""
        INSERT INTO divulgacao (area, titulo, texto, link, imagem, show_on_edu, show_on_index)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        RETURNING id
    """).bind(s_area, s_titulo, d1_texto, d1_link, d1_imagem, 
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
        values.append(sanitize_for_d1(link))
    if imagem is not None:
        updates.append("imagem = ?")
        values.append(sanitize_for_d1(imagem))
    if ativo is not None:
        updates.append("ativo = ?")
        values.append(1 if ativo else 0)
    if ordem is not None:
        updates.append("ordem = ?")
        values.append(sanitize_for_d1(ordem))
    if show_on_edu is not None:
        updates.append("show_on_edu = ?")
        values.append(1 if show_on_edu else 0)
    if show_on_index is not None:
        updates.append("show_on_index = ?")
        values.append(1 if show_on_index else 0)
    
    if not updates:
        return False
    
    updates.append("updated_at = datetime('now')")
    # Sanitize divulgacao_id to prevent D1_TYPE_ERROR from undefined values
    s_divulgacao_id = sanitize_for_d1(divulgacao_id)
    if s_divulgacao_id is None:
        return False
    values.append(s_divulgacao_id)
    
    set_clause = ", ".join(updates)
    
    await db.prepare(f"""
        UPDATE divulgacao SET {set_clause}
        WHERE id = ?
    """).bind(*values).run()
    return True


async def delete_divulgacao(db, divulgacao_id):
    """Remove uma divulgação."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_divulgacao_id = sanitize_for_d1(divulgacao_id)
    if s_divulgacao_id is None:
        return
    await db.prepare("""
        DELETE FROM divulgacao WHERE id = ?
    """).bind(s_divulgacao_id).run()


# ============================================================================
# QUERIES - UPLOAD DE IMAGENS
# ============================================================================

async def save_upload(db, usuario_id, tipo, path, filename=None, content_type=None, size=None):
    """Registra um upload de imagem."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id, s_tipo, s_path, s_filename, s_content_type, s_size = sanitize_params(
        usuario_id, tipo, path, filename, content_type, size
    )
    
    # Convert Python None to JavaScript null for D1
    d1_filename = to_d1_null(s_filename)
    d1_content_type = to_d1_null(s_content_type)
    d1_size = to_d1_null(s_size)
    
    result = await db.prepare("""
        INSERT INTO upload (usuario_id, tipo, path, filename, content_type, size)
        VALUES (?, ?, ?, ?, ?, ?)
        RETURNING id
    """).bind(s_usuario_id, s_tipo, s_path, d1_filename, d1_content_type, d1_size).first()
    return safe_get(result, 'id')


async def get_user_uploads(db, usuario_id, tipo=None):
    """Lista uploads de usuárie."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_tipo = sanitize_for_d1(tipo)
    if s_usuario_id is None:
        return []
    
    if s_tipo:
        result = await db.prepare("""
            SELECT * FROM upload
            WHERE usuario_id = ? AND tipo = ?
            ORDER BY created_at DESC
        """).bind(s_usuario_id, s_tipo).all()
    else:
        result = await db.prepare("""
            SELECT * FROM upload
            WHERE usuario_id = ?
            ORDER BY created_at DESC
        """).bind(s_usuario_id).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - ADMIN
# ============================================================================

async def get_all_usuaries(db, page=1, per_page=20, search=None):
    """Lista todes usuáries (para admin)."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_page = sanitize_for_d1(page) or 1
    s_per_page = sanitize_for_d1(per_page) or 20
    s_search = sanitize_for_d1(search)
    offset = (s_page - 1) * s_per_page
    
    if s_search:
        search_term = f"%{s_search}%"
        result = await db.prepare("""
            SELECT id, username, nome, email, foto_perfil, is_admin, is_superadmin, 
                   is_banned, created_at, email_confirmed
            FROM user
            WHERE username LIKE ? OR nome LIKE ? OR email LIKE ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """).bind(search_term, search_term, search_term, s_per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT id, username, nome, email, foto_perfil, is_admin, is_superadmin, 
                   is_banned, created_at, email_confirmed
            FROM user
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """).bind(s_per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def ban_usuarie(db, usuario_id, reason=None, admin_id=None):
    """Bane usuárie."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_reason = sanitize_for_d1(reason)
    if s_usuario_id is None:
        return
    
    # Convert Python None to JavaScript null for D1
    d1_reason = to_d1_null(s_reason)
    
    await db.prepare("""
        UPDATE user SET is_banned = 1, banned_at = datetime('now'), ban_reason = ?
        WHERE id = ?
    """).bind(d1_reason, s_usuario_id).run()


async def unban_usuarie(db, usuario_id):
    """Remove ban de usuárie."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    if s_usuario_id is None:
        return
    await db.prepare("""
        UPDATE user SET is_banned = 0, banned_at = NULL, ban_reason = NULL
        WHERE id = ?
    """).bind(s_usuario_id).run()


async def suspend_usuarie(db, usuario_id, until_date):
    """Suspende usuárie temporariamente."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_until_date = sanitize_for_d1(until_date)
    if s_usuario_id is None:
        return
    await db.prepare("""
        UPDATE user SET suspended_until = ?
        WHERE id = ?
    """).bind(s_until_date, s_usuario_id).run()


async def make_admin(db, usuario_id, is_admin=True):
    """Torna usuárie admin ou remove permissão."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    if s_usuario_id is None:
        return
    await db.prepare("""
        UPDATE user SET is_admin = ?
        WHERE id = ?
    """).bind(1 if is_admin else 0, s_usuario_id).run()


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
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_ip_address = sanitize_for_d1(ip_address)
    s_endpoint = sanitize_for_d1(endpoint)
    if s_ip_address is None or s_endpoint is None:
        return True, None  # Block if no valid IP/endpoint
    
    now = datetime.utcnow()
    
    result = await db.prepare("""
        SELECT * FROM rate_limit
        WHERE ip_address = ? AND endpoint = ?
    """).bind(s_ip_address, s_endpoint).first()
    
    if not result:
        # Primeiro acesso
        await db.prepare("""
            INSERT INTO rate_limit (ip_address, endpoint, attempts)
            VALUES (?, ?, 1)
        """).bind(s_ip_address, s_endpoint).run()
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
            """).bind(s_ip_address, s_endpoint).run()
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
        """).bind(s_ip_address, s_endpoint).run()
        return True, None
    
    if rate['attempts'] >= max_attempts:
        # Bloquear
        block_until = (now + timedelta(minutes=15)).isoformat()
        await db.prepare("""
            UPDATE rate_limit SET blocked_until = ?
            WHERE ip_address = ? AND endpoint = ?
        """).bind(block_until, s_ip_address, s_endpoint).run()
        return False, "Muitas tentativas. Bloqueade por 15 minutos."
    
    # Incrementar tentativas
    await db.prepare("""
        UPDATE rate_limit SET attempts = attempts + 1, last_attempt = datetime('now')
        WHERE ip_address = ? AND endpoint = ?
    """).bind(s_ip_address, s_endpoint).run()
    return True, None


# ============================================================================
# QUERIES - LOGS DE ATIVIDADE
# ============================================================================

async def log_activity(db, acao, usuario_id=None, descricao=None, ip_address=None, 
                       user_agent=None, dados_extra=None):
    """Registra uma atividade no log de auditoria."""
    dados_json = json.dumps(dados_extra) if dados_extra else None
    
    # Sanitize parameters and convert None to JavaScript null for D1
    params = d1_params(usuario_id, acao, descricao, ip_address, user_agent, dados_json)
    
    await db.prepare("""
        INSERT INTO activity_log (usuario_id, acao, descricao, ip_address, user_agent, dados_extra)
        VALUES (?, ?, ?, ?, ?, ?)
    """).bind(*params).run()


async def get_activity_log(db, usuario_id=None, acao=None, page=1, per_page=50):
    """Lista atividades do log."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_acao = sanitize_for_d1(acao)
    s_page = sanitize_for_d1(page) or 1
    s_per_page = sanitize_for_d1(per_page) or 50
    offset = (s_page - 1) * s_per_page
    
    if s_usuario_id and s_acao:
        result = await db.prepare("""
            SELECT a.*, u.username
            FROM activity_log a
            LEFT JOIN user u ON a.usuario_id = u.id
            WHERE a.usuario_id = ? AND a.acao = ?
            ORDER BY a.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(s_usuario_id, s_acao, s_per_page, offset).all()
    elif s_usuario_id:
        result = await db.prepare("""
            SELECT a.*, u.username
            FROM activity_log a
            LEFT JOIN user u ON a.usuario_id = u.id
            WHERE a.usuario_id = ?
            ORDER BY a.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(s_usuario_id, s_per_page, offset).all()
    elif s_acao:
        result = await db.prepare("""
            SELECT a.*, u.username
            FROM activity_log a
            LEFT JOIN user u ON a.usuario_id = u.id
            WHERE a.acao = ?
            ORDER BY a.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(s_acao, s_per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT a.*, u.username
            FROM activity_log a
            LEFT JOIN user u ON a.usuario_id = u.id
            ORDER BY a.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(s_per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - GAMIFICAÇÃO (Pontos e Badges)
# ============================================================================

async def get_user_points(db, usuario_id):
    """Retorna pontos de usuárie."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    if s_usuario_id is None:
        return {'usuario_id': None, 'pontos_total': 0, 'pontos_exercicios': 0,
                'pontos_posts': 0, 'pontos_dinamicas': 0, 'nivel': 1}
    
    result = await db.prepare("""
        SELECT * FROM user_points WHERE usuario_id = ?
    """).bind(s_usuario_id).first()
    
    if not result:
        # Criar registro se não existe
        await db.prepare("""
            INSERT INTO user_points (usuario_id) VALUES (?)
        """).bind(s_usuario_id).run()
        return {'usuario_id': s_usuario_id, 'pontos_total': 0, 'pontos_exercicios': 0,
                'pontos_posts': 0, 'pontos_dinamicas': 0, 'nivel': 1}
    
    return safe_dict(result)


async def add_points(db, usuario_id, pontos, tipo='exercicios'):
    """Adiciona pontos a usuárie."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_pontos = sanitize_for_d1(pontos) or 0
    if s_usuario_id is None:
        return
    
    # Primeiro garante que o registro existe
    await get_user_points(db, s_usuario_id)
    
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
        """).bind(s_pontos, s_pontos, s_usuario_id).run()
    elif tipo_coluna == 'pontos_posts':
        await db.prepare("""
            UPDATE user_points 
            SET pontos_total = pontos_total + ?,
                pontos_posts = pontos_posts + ?,
                updated_at = datetime('now')
            WHERE usuario_id = ?
        """).bind(s_pontos, s_pontos, s_usuario_id).run()
    elif tipo_coluna == 'pontos_dinamicas':
        await db.prepare("""
            UPDATE user_points 
            SET pontos_total = pontos_total + ?,
                pontos_dinamicas = pontos_dinamicas + ?,
                updated_at = datetime('now')
            WHERE usuario_id = ?
        """).bind(s_pontos, s_pontos, s_usuario_id).run()
    
    # Atualizar nível baseado em pontos
    await update_user_level(db, s_usuario_id)


async def update_user_level(db, usuario_id):
    """Atualiza o nível de usuárie baseado em pontos."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    if s_usuario_id is None:
        return
    
    result = await db.prepare("""
        SELECT pontos_total FROM user_points WHERE usuario_id = ?
    """).bind(s_usuario_id).first()
    
    if not result:
        return
    
    pontos = safe_get(result, 'pontos_total', 0)
    
    # Calcular nível (a cada 100 pontos sobe um nível)
    nivel = max(1, (pontos // 100) + 1)
    
    await db.prepare("""
        UPDATE user_points SET nivel = ? WHERE usuario_id = ?
    """).bind(nivel, s_usuario_id).run()


async def get_ranking(db, limit=10, tipo=None):
    """Retorna ranking de usuáries por pontos."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_limit = sanitize_for_d1(limit) or 10
    
    # Usar queries separadas para cada tipo para evitar f-string SQL
    if tipo == 'exercicios':
        result = await db.prepare("""
            SELECT p.*, u.username, u.nome, u.foto_perfil
            FROM user_points p
            JOIN user u ON p.usuario_id = u.id
            WHERE u.is_banned = 0
            ORDER BY p.pontos_exercicios DESC
            LIMIT ?
        """).bind(s_limit).all()
    elif tipo == 'posts':
        result = await db.prepare("""
            SELECT p.*, u.username, u.nome, u.foto_perfil
            FROM user_points p
            JOIN user u ON p.usuario_id = u.id
            WHERE u.is_banned = 0
            ORDER BY p.pontos_posts DESC
            LIMIT ?
        """).bind(s_limit).all()
    elif tipo == 'dinamicas':
        result = await db.prepare("""
            SELECT p.*, u.username, u.nome, u.foto_perfil
            FROM user_points p
            JOIN user u ON p.usuario_id = u.id
            WHERE u.is_banned = 0
            ORDER BY p.pontos_dinamicas DESC
            LIMIT ?
        """).bind(s_limit).all()
    else:
        result = await db.prepare("""
            SELECT p.*, u.username, u.nome, u.foto_perfil
            FROM user_points p
            JOIN user u ON p.usuario_id = u.id
            WHERE u.is_banned = 0
            ORDER BY p.pontos_total DESC
            LIMIT ?
        """).bind(s_limit).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_all_badges(db):
    """Lista todos os badges disponíveis."""
    result = await db.prepare("""
        SELECT * FROM badge ORDER BY categoria, pontos_necessarios
    """).all()
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_user_badges(db, usuario_id):
    """Lista badges de usuárie."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    if s_usuario_id is None:
        return []
    result = await db.prepare("""
        SELECT b.*, ub.earned_at
        FROM user_badge ub
        JOIN badge b ON ub.badge_id = b.id
        WHERE ub.usuario_id = ?
        ORDER BY ub.earned_at DESC
    """).bind(s_usuario_id).all()
    return [safe_dict(row) for row in result.results] if result.results else []


async def award_badge(db, usuario_id, badge_nome):
    """Concede um badge a usuárie."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id, s_badge_nome = sanitize_params(usuario_id, badge_nome)
    if s_usuario_id is None or s_badge_nome is None:
        return False
    
    # Convert to D1-safe format
    d1_badge_nome = to_d1_null(s_badge_nome)
    
    # Buscar badge por nome
    badge = await db.prepare("""
        SELECT id FROM badge WHERE nome = ?
    """).bind(d1_badge_nome).first()
    
    if not badge:
        return False
    
    badge_id = safe_get(badge, 'id')
    if badge_id is None:
        return False
    
    # Convert all parameters to D1-safe format
    d1_usuario_id = to_d1_null(s_usuario_id)
    d1_badge_id = to_d1_null(badge_id)
    
    try:
        await db.prepare("""
            INSERT INTO user_badge (usuario_id, badge_id) VALUES (?, ?)
        """).bind(d1_usuario_id, d1_badge_id).run()
        
        # Notificar usuárie
        await create_notification(db, s_usuario_id, 'badge',
                                  titulo=f'Novo badge: {s_badge_nome}! 🎖️')
        return True
    except Exception:
        return False  # Já tem o badge ou erro de constraint


async def check_and_award_badges(db, usuario_id):
    """Verifica e concede badges que usuárie merece."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    if s_usuario_id is None:
        return []
    
    # Buscar estatísticas
    points = await get_user_points(db, s_usuario_id)
    
    badges_concedidos = []
    
    # Badge por pontos de exercícios
    if points['pontos_exercicios'] >= 100:
        if await award_badge(db, s_usuario_id, 'Estudante'):
            badges_concedidos.append('Estudante')
    if points['pontos_exercicios'] >= 500:
        if await award_badge(db, s_usuario_id, 'Dedicade'):
            badges_concedidos.append('Dedicade')
    if points['pontos_exercicios'] >= 1000:
        if await award_badge(db, s_usuario_id, 'Mestre'):
            badges_concedidos.append('Mestre')
    
    # Badge por posts
    post_count = await db.prepare("""
        SELECT COUNT(*) as count FROM post WHERE usuario_id = ? AND is_deleted = 0
    """).bind(s_usuario_id).first()
    if post_count and safe_get(post_count, 'count', 0) >= 5:
        if await award_badge(db, s_usuario_id, 'Escritor'):
            badges_concedidos.append('Escritor')
    
    # Badge por amigues
    amigues_count = await db.prepare("""
        SELECT COUNT(*) as count FROM amizade
        WHERE (usuario1_id = ? OR usuario2_id = ?) AND status = 'aceita'
    """).bind(s_usuario_id, s_usuario_id).first()
    if amigues_count and safe_get(amigues_count, 'count', 0) >= 5:
        if await award_badge(db, s_usuario_id, 'Social'):
            badges_concedidos.append('Social')
    
    return badges_concedidos


# ============================================================================
# QUERIES - PROGRESSO EM EXERCÍCIOS
# ============================================================================

async def record_exercise_answer(db, usuario_id, question_id, resposta, correto, tempo_resposta=None):
    """Registra resposta de exercício e retorna pontos ganhos."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_question_id = sanitize_for_d1(question_id)
    s_resposta = sanitize_for_d1(resposta)
    s_tempo = sanitize_for_d1(tempo_resposta)
    if s_usuario_id is None or s_question_id is None:
        return 0
    
    pontos = 0
    primeira_tentativa = 1
    
    # Verificar se já respondeu corretamente antes (para não dar pontos novamente)
    scored = await db.prepare("""
        SELECT 1 FROM exercise_scored WHERE usuario_id = ? AND question_id = ?
    """).bind(s_usuario_id, s_question_id).first()
    
    if scored:
        primeira_tentativa = 0
    elif correto:
        # Primeira vez acertando - dar pontos
        pontos = 1  # 1 ponto por acerto
        
        # Marcar como pontuado
        await db.prepare("""
            INSERT INTO exercise_scored (usuario_id, question_id) VALUES (?, ?)
        """).bind(s_usuario_id, s_question_id).run()
        
        # Adicionar pontos ao total
        await add_points(db, s_usuario_id, pontos, 'exercicios')
    
    # Registrar no histórico
    # Convert Python None to JavaScript null for D1
    d1_tempo = to_d1_null(s_tempo)
    
    await db.prepare("""
        INSERT INTO exercise_progress (usuario_id, question_id, resposta_usuarie, correto, 
                                        pontos_ganhos, primeira_tentativa, tempo_resposta)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """).bind(s_usuario_id, s_question_id, s_resposta, 1 if correto else 0, 
              pontos, primeira_tentativa, d1_tempo).run()
    
    # Verificar badges
    await check_and_award_badges(db, s_usuario_id)
    
    return pontos


async def get_user_exercise_stats(db, usuario_id, topic_id=None):
    """Retorna estatísticas de exercícios de usuárie."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_topic_id = sanitize_for_d1(topic_id)
    if s_usuario_id is None:
        return {'total_respostas': 0, 'acertos': 0, 'pontos': 0}
    
    if s_topic_id:
        result = await db.prepare("""
            SELECT 
                COUNT(*) as total_respostas,
                SUM(CASE WHEN correto = 1 THEN 1 ELSE 0 END) as acertos,
                SUM(pontos_ganhos) as pontos
            FROM exercise_progress ep
            JOIN exercise_question eq ON ep.question_id = eq.id
            WHERE ep.usuario_id = ? AND eq.topic_id = ?
        """).bind(s_usuario_id, s_topic_id).first()
    else:
        result = await db.prepare("""
            SELECT 
                COUNT(*) as total_respostas,
                SUM(CASE WHEN correto = 1 THEN 1 ELSE 0 END) as acertos,
                SUM(pontos_ganhos) as pontos
            FROM exercise_progress
            WHERE usuario_id = ?
        """).bind(s_usuario_id).first()
    
    if result:
        return safe_dict(result)
    return {'total_respostas': 0, 'acertos': 0, 'pontos': 0}


async def get_questions_not_scored(db, usuario_id, topic_id=None, limit=10):
    """Retorna questões que usuárie ainda não pontuou."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_topic_id = sanitize_for_d1(topic_id)
    s_limit = sanitize_for_d1(limit) or 10
    if s_usuario_id is None:
        return []
    
    if s_topic_id:
        result = await db.prepare("""
            SELECT eq.*, et.nome as topic_name
            FROM exercise_question eq
            JOIN exercise_topic et ON eq.topic_id = et.id
            LEFT JOIN exercise_scored es ON eq.id = es.question_id AND es.usuario_id = ?
            WHERE es.question_id IS NULL AND eq.topic_id = ?
            ORDER BY RANDOM()
            LIMIT ?
        """).bind(s_usuario_id, s_topic_id, s_limit).all()
    else:
        result = await db.prepare("""
            SELECT eq.*, et.nome as topic_name
            FROM exercise_question eq
            JOIN exercise_topic et ON eq.topic_id = et.id
            LEFT JOIN exercise_scored es ON eq.id = es.question_id AND es.usuario_id = ?
            WHERE es.question_id IS NULL
            ORDER BY RANDOM()
            LIMIT ?
        """).bind(s_usuario_id, s_limit).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - LISTAS DE EXERCÍCIOS PERSONALIZADAS
# ============================================================================

async def create_exercise_list(db, usuario_id, nome, descricao=None, modo='estudo', tempo_limite=None):
    """Cria uma lista personalizada de exercícios."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id, s_nome, s_descricao, s_modo, s_tempo_limite = sanitize_params(
        usuario_id, nome, descricao, modo, tempo_limite
    )
    
    # Convert Python None to JavaScript null for D1
    d1_descricao = to_d1_null(s_descricao)
    d1_tempo_limite = to_d1_null(s_tempo_limite)
    
    result = await db.prepare("""
        INSERT INTO exercise_list (usuario_id, nome, descricao, modo, tempo_limite)
        VALUES (?, ?, ?, ?, ?)
        RETURNING id
    """).bind(s_usuario_id, s_nome, d1_descricao, s_modo, d1_tempo_limite).first()
    return safe_get(result, 'id')


async def add_to_exercise_list(db, list_id, question_id, ordem=0):
    """Adiciona questão à lista de exercícios."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_list_id, s_question_id, s_ordem = sanitize_params(list_id, question_id, ordem)
    try:
        await db.prepare("""
            INSERT INTO exercise_list_item (list_id, question_id, ordem) VALUES (?, ?, ?)
        """).bind(s_list_id, s_question_id, s_ordem).run()
        return True
    except Exception:
        return False  # Questão já está na lista


async def get_exercise_lists(db, usuario_id):
    """Lista as listas de exercícios de usuárie."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    if s_usuario_id is None:
        return []
    result = await db.prepare("""
        SELECT el.*, 
               (SELECT COUNT(*) FROM exercise_list_item WHERE list_id = el.id) as question_count
        FROM exercise_list el
        WHERE el.usuario_id = ?
        ORDER BY el.created_at DESC
    """).bind(s_usuario_id).all()
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_exercise_list_questions(db, list_id):
    """Retorna questões de uma lista."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_list_id = sanitize_for_d1(list_id)
    if s_list_id is None:
        return []
    result = await db.prepare("""
        SELECT eq.*, et.nome as topic_name, eli.ordem
        FROM exercise_list_item eli
        JOIN exercise_question eq ON eli.question_id = eq.id
        JOIN exercise_topic et ON eq.topic_id = et.id
        WHERE eli.list_id = ?
        ORDER BY eli.ordem
    """).bind(s_list_id).all()
    return [safe_dict(row) for row in result.results] if result.results else []


async def save_quiz_result(db, usuario_id, acertos, erros, pontos, tempo_total, list_id=None, topic_id=None):
    """Salva resultado de quiz."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id, s_list_id, s_topic_id, s_acertos, s_erros, s_pontos, s_tempo_total = sanitize_params(
        usuario_id, list_id, topic_id, acertos, erros, pontos, tempo_total
    )
    
    # Convert Python None to JavaScript null for D1
    d1_list_id = to_d1_null(s_list_id)
    d1_topic_id = to_d1_null(s_topic_id)
    
    result = await db.prepare("""
        INSERT INTO quiz_result (usuario_id, list_id, topic_id, acertos, erros, pontos_ganhos, tempo_total)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        RETURNING id
    """).bind(s_usuario_id, d1_list_id, d1_topic_id, s_acertos, s_erros, s_pontos, s_tempo_total).first()
    return safe_get(result, 'id')


# ============================================================================
# QUERIES - FLASHCARDS
# ============================================================================

async def create_flashcard_deck(db, titulo, usuario_id=None, descricao=None, is_public=False):
    """Cria um deck de flashcards."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id, s_titulo, s_descricao = sanitize_params(usuario_id, titulo, descricao)
    
    # Convert Python None to JavaScript null for D1
    d1_usuario_id = to_d1_null(s_usuario_id)
    d1_descricao = to_d1_null(s_descricao)
    
    result = await db.prepare("""
        INSERT INTO flashcard_deck (usuario_id, titulo, descricao, is_public)
        VALUES (?, ?, ?, ?)
        RETURNING id
    """).bind(d1_usuario_id, s_titulo, d1_descricao, 1 if is_public else 0).first()
    
    # Dar badge se for o primeiro deck
    if s_usuario_id:
        await award_badge(db, s_usuario_id, 'Flashcard Pro')
    
    return safe_get(result, 'id')


async def add_flashcard(db, deck_id, frente, verso, dica=None, ordem=0):
    """Adiciona um flashcard ao deck."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_deck_id, s_frente, s_verso, s_dica, s_ordem = sanitize_params(
        deck_id, frente, verso, dica, ordem
    )
    
    # Convert Python None to JavaScript null for D1
    d1_dica = to_d1_null(s_dica)
    
    result = await db.prepare("""
        INSERT INTO flashcard (deck_id, frente, verso, dica, ordem)
        VALUES (?, ?, ?, ?, ?)
        RETURNING id
    """).bind(s_deck_id, s_frente, s_verso, d1_dica, s_ordem).first()
    return safe_get(result, 'id')


async def get_flashcard_decks(db, usuario_id=None, include_public=True):
    """Lista decks de flashcards."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    
    if s_usuario_id and include_public:
        result = await db.prepare("""
            SELECT fd.*, u.username as author_name,
                   (SELECT COUNT(*) FROM flashcard WHERE deck_id = fd.id) as card_count
            FROM flashcard_deck fd
            LEFT JOIN user u ON fd.usuario_id = u.id
            WHERE fd.usuario_id = ? OR fd.is_public = 1
            ORDER BY fd.created_at DESC
        """).bind(s_usuario_id).all()
    elif s_usuario_id:
        result = await db.prepare("""
            SELECT fd.*, u.username as author_name,
                   (SELECT COUNT(*) FROM flashcard WHERE deck_id = fd.id) as card_count
            FROM flashcard_deck fd
            LEFT JOIN user u ON fd.usuario_id = u.id
            WHERE fd.usuario_id = ?
            ORDER BY fd.created_at DESC
        """).bind(s_usuario_id).all()
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
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_deck_id = sanitize_for_d1(deck_id)
    if s_deck_id is None:
        return []
    result = await db.prepare("""
        SELECT * FROM flashcard WHERE deck_id = ? ORDER BY ordem
    """).bind(s_deck_id).all()
    return [safe_dict(row) for row in result.results] if result.results else []


async def get_cards_to_review(db, usuario_id, deck_id=None, limit=20):
    """Retorna flashcards para revisão espaçada."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_deck_id = sanitize_for_d1(deck_id)
    s_limit = sanitize_for_d1(limit) or 20
    if s_usuario_id is None:
        return []
    
    now = datetime.utcnow().isoformat()
    
    if s_deck_id:
        result = await db.prepare("""
            SELECT f.*, fr.ease_factor, fr.interval_days, fr.repetitions, fr.next_review
            FROM flashcard f
            LEFT JOIN flashcard_review fr ON f.id = fr.flashcard_id AND fr.usuario_id = ?
            WHERE f.deck_id = ?
            AND (fr.next_review IS NULL OR fr.next_review <= ?)
            ORDER BY fr.next_review NULLS FIRST, RANDOM()
            LIMIT ?
        """).bind(s_usuario_id, s_deck_id, now, s_limit).all()
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
        """).bind(s_usuario_id, s_usuario_id, now, s_limit).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def record_flashcard_review(db, usuario_id, flashcard_id, quality):
    """
    Registra revisão de flashcard usando algoritmo SM-2.
    quality: 0-5 (0-2 = errou, 3-5 = acertou com diferentes níveis de facilidade)
    """
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_flashcard_id = sanitize_for_d1(flashcard_id)
    s_quality = sanitize_for_d1(quality) or 3
    if s_usuario_id is None or s_flashcard_id is None:
        return {'ease_factor': 2.5, 'interval_days': 1, 'next_review': None}
    
    # Buscar revisão existente
    existing = await db.prepare("""
        SELECT * FROM flashcard_review WHERE usuario_id = ? AND flashcard_id = ?
    """).bind(s_usuario_id, s_flashcard_id).first()
    
    if existing:
        existing_dict = safe_dict(existing)
        ef = safe_get(existing_dict, 'ease_factor', 2.5)
        reps = safe_get(existing_dict, 'repetitions', 0)
        interval = safe_get(existing_dict, 'interval_days', 1)
    else:
        ef = 2.5
        reps = 0
        interval = 1
    
    # Algoritmo SM-2
    if s_quality < 3:
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
    ef = max(1.3, ef + (0.1 - (5 - s_quality) * (0.08 + (5 - s_quality) * 0.02)))
    
    # Calcular próxima revisão
    next_review = (datetime.utcnow() + timedelta(days=interval)).isoformat()
    
    if existing:
        await db.prepare("""
            UPDATE flashcard_review 
            SET ease_factor = ?, interval_days = ?, repetitions = ?, 
                next_review = ?, last_review = datetime('now')
            WHERE usuario_id = ? AND flashcard_id = ?
        """).bind(ef, interval, reps, next_review, s_usuario_id, s_flashcard_id).run()
    else:
        await db.prepare("""
            INSERT INTO flashcard_review (usuario_id, flashcard_id, ease_factor, 
                                          interval_days, repetitions, next_review, last_review)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """).bind(s_usuario_id, s_flashcard_id, ef, interval, reps, next_review).run()
    
    return {'ease_factor': ef, 'interval_days': interval, 'next_review': next_review}


# ============================================================================
# QUERIES - FAVORITOS
# ============================================================================

async def add_favorite(db, usuario_id, tipo, item_id):
    """Adiciona item aos favoritos."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id, s_tipo, s_item_id = sanitize_params(usuario_id, tipo, item_id)
    try:
        await db.prepare("""
            INSERT INTO favorito (usuario_id, tipo, item_id) VALUES (?, ?, ?)
        """).bind(s_usuario_id, s_tipo, s_item_id).run()
        return True
    except Exception:
        return False  # Já é favorito


async def remove_favorite(db, usuario_id, tipo, item_id):
    """Remove item dos favoritos."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id, s_tipo, s_item_id = sanitize_params(usuario_id, tipo, item_id)
    await db.prepare("""
        DELETE FROM favorito WHERE usuario_id = ? AND tipo = ? AND item_id = ?
    """).bind(s_usuario_id, s_tipo, s_item_id).run()


async def is_favorite(db, usuario_id, tipo, item_id):
    """Verifica se item é favorito."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id, s_tipo, s_item_id = sanitize_params(usuario_id, tipo, item_id)
    if s_usuario_id is None:
        return False
    result = await db.prepare("""
        SELECT 1 FROM favorito WHERE usuario_id = ? AND tipo = ? AND item_id = ?
    """).bind(s_usuario_id, s_tipo, s_item_id).first()
    return result is not None


async def get_favorites(db, usuario_id, tipo=None):
    """Lista favoritos de usuárie."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_tipo = sanitize_for_d1(tipo)
    if s_usuario_id is None:
        return []
    
    if s_tipo:
        result = await db.prepare("""
            SELECT * FROM favorito WHERE usuario_id = ? AND tipo = ?
            ORDER BY created_at DESC
        """).bind(s_usuario_id, s_tipo).all()
    else:
        result = await db.prepare("""
            SELECT * FROM favorito WHERE usuario_id = ?
            ORDER BY created_at DESC
        """).bind(s_usuario_id).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - HISTÓRICO DE USUÁRIE
# ============================================================================

async def add_to_history(db, usuario_id, tipo, item_tipo, item_id, dados=None):
    """Adiciona item ao histórico de usuárie."""
    dados_json = json.dumps(dados) if dados else None
    
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id, s_tipo, s_item_tipo, s_item_id, s_dados_json = sanitize_params(
        usuario_id, tipo, item_tipo, item_id, dados_json
    )
    
    await db.prepare("""
        INSERT INTO user_history (usuario_id, tipo, item_tipo, item_id, dados)
        VALUES (?, ?, ?, ?, ?)
    """).bind(s_usuario_id, s_tipo, s_item_tipo, s_item_id, s_dados_json).run()


async def get_user_history(db, usuario_id, item_tipo=None, limit=50):
    """Lista histórico de usuárie."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_item_tipo = sanitize_for_d1(item_tipo)
    s_limit = sanitize_for_d1(limit) or 50
    if s_usuario_id is None:
        return []
    
    if s_item_tipo:
        result = await db.prepare("""
            SELECT * FROM user_history 
            WHERE usuario_id = ? AND item_tipo = ?
            ORDER BY created_at DESC
            LIMIT ?
        """).bind(s_usuario_id, s_item_tipo, s_limit).all()
    else:
        result = await db.prepare("""
            SELECT * FROM user_history 
            WHERE usuario_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """).bind(s_usuario_id, s_limit).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - PREFERÊNCIAS DE USUÁRIE
# ============================================================================

async def get_user_preferences(db, usuario_id):
    """Retorna preferências de usuárie."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    if s_usuario_id is None:
        return {'tema': 'claro', 'alto_contraste': False}
    result = await db.prepare("""
        SELECT * FROM user_preferences WHERE usuario_id = ?
    """).bind(s_usuario_id).first()
    
    if not result:
        # Criar preferências padrão
        await db.prepare("""
            INSERT INTO user_preferences (usuario_id) VALUES (?)
        """).bind(s_usuario_id).run()
        return await get_user_preferences(db, s_usuario_id)
    
    return safe_dict(result)


async def update_user_preferences(db, usuario_id, **kwargs):
    """Atualiza preferências de usuárie."""
    # Sanitize usuario_id to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    
    # Garantir que registro existe
    await get_user_preferences(db, s_usuario_id)
    
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
    
    # Filtrar apenas chaves permitidas e sanitize values
    filtered_kwargs = {k: sanitize_for_d1(v) for k, v in kwargs.items() if k in allowed_columns}
    
    if not filtered_kwargs:
        return False
    
    # Atualizar cada campo individualmente para evitar SQL dinâmico
    # Wrap s_usuario_id once before the loop
    d1_usuario_id = to_d1_null(s_usuario_id)
    
    for key, value in filtered_kwargs.items():
        # Wrap value for each iteration to prevent D1_TYPE_ERROR
        d1_value = to_d1_null(value)
        
        # Os nomes de colunas são validados pela whitelist acima
        if key == 'tema':
            await db.prepare("UPDATE user_preferences SET tema = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(d1_value, d1_usuario_id).run()
        elif key == 'fonte_tamanho':
            await db.prepare("UPDATE user_preferences SET fonte_tamanho = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(d1_value, d1_usuario_id).run()
        elif key == 'fonte_familia':
            await db.prepare("UPDATE user_preferences SET fonte_familia = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(d1_value, d1_usuario_id).run()
        elif key == 'alto_contraste':
            await db.prepare("UPDATE user_preferences SET alto_contraste = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(d1_value, d1_usuario_id).run()
        elif key == 'animacoes_reduzidas':
            await db.prepare("UPDATE user_preferences SET animacoes_reduzidas = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(d1_value, d1_usuario_id).run()
        elif key == 'exibir_libras':
            await db.prepare("UPDATE user_preferences SET exibir_libras = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(d1_value, d1_usuario_id).run()
        elif key == 'audio_habilitado':
            await db.prepare("UPDATE user_preferences SET audio_habilitado = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(d1_value, d1_usuario_id).run()
        elif key == 'velocidade_audio':
            await db.prepare("UPDATE user_preferences SET velocidade_audio = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(d1_value, d1_usuario_id).run()
        elif key == 'notificacoes_email':
            await db.prepare("UPDATE user_preferences SET notificacoes_email = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(d1_value, d1_usuario_id).run()
        elif key == 'notificacoes_push':
            await db.prepare("UPDATE user_preferences SET notificacoes_push = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(d1_value, d1_usuario_id).run()
        elif key == 'idioma':
            await db.prepare("UPDATE user_preferences SET idioma = ?, updated_at = datetime('now') WHERE usuario_id = ?").bind(d1_value, d1_usuario_id).run()
    
    return True


# ============================================================================
# QUERIES - MENSAGENS DIRETAS
# ============================================================================

async def send_direct_message(db, remetente_id, destinatarie_id, conteudo):
    """Envia mensagem direta."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_remetente_id, s_destinatarie_id, s_conteudo = sanitize_params(
        remetente_id, destinatarie_id, conteudo
    )
    
    # Convert Python None to JavaScript null for D1
    # Wrap ALL parameters to prevent undefined from crossing the FFI boundary
    d1_remetente_id = to_d1_null(s_remetente_id)
    d1_destinatarie_id = to_d1_null(s_destinatarie_id)
    d1_conteudo = to_d1_null(s_conteudo)
    
    result = await db.prepare("""
        INSERT INTO mensagem_direta (remetente_id, destinatarie_id, conteudo)
        VALUES (?, ?, ?)
        RETURNING id
    """).bind(d1_remetente_id, d1_destinatarie_id, d1_conteudo).first()
    
    # Notificar destinatárie
    await create_notification(db, s_destinatarie_id, 'mensagem',
                              titulo='Nova mensagem!',
                              from_usuario_id=s_remetente_id)
    
    return safe_get(result, 'id')


async def get_conversations(db, usuario_id):
    """Lista conversas de usuárie."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    if s_usuario_id is None:
        return []
    result = await db.prepare("""
        SELECT DISTINCT 
            CASE 
                WHEN remetente_id = ? THEN destinatarie_id 
                ELSE remetente_id 
            END as other_user_id
        FROM mensagem_direta
        WHERE remetente_id = ? OR destinatarie_id = ?
    """).bind(s_usuario_id, s_usuario_id, s_usuario_id).all()
    
    if not result.results:
        return []
    
    # Buscar dados dos usuáries
    conversations = []
    for row in result.results:
        row_dict = safe_dict(row) if hasattr(row, 'to_py') else row
        if not isinstance(row_dict, dict):
            continue
        other_id = sanitize_for_d1(row_dict.get('other_user_id'))
        if other_id is None:
            continue
        user = await get_user_by_id(db, other_id)
        
        # Última mensagem
        last_msg = await db.prepare("""
            SELECT * FROM mensagem_direta
            WHERE (remetente_id = ? AND destinatarie_id = ?)
               OR (remetente_id = ? AND destinatarie_id = ?)
            ORDER BY created_at DESC
            LIMIT 1
        """).bind(s_usuario_id, other_id, other_id, s_usuario_id).first()
        
        # Mensagens não lidas
        unread = await db.prepare("""
            SELECT COUNT(*) as count FROM mensagem_direta
            WHERE remetente_id = ? AND destinatarie_id = ? AND lida = 0
        """).bind(other_id, s_usuario_id).first()
        
        unread_dict = safe_dict(unread) if unread else None
        conversations.append({
            'other_user': user,
            'last_message': safe_dict(last_msg) if last_msg else None,
            'unread_count': unread_dict.get('count', 0) if unread_dict else 0
        })
    
    return conversations


async def get_messages_with_user(db, usuario_id, other_user_id, page=1, per_page=50):
    """Lista mensagens entre dois usuáries."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_other_user_id = sanitize_for_d1(other_user_id)
    s_page = sanitize_for_d1(page) or 1
    s_per_page = sanitize_for_d1(per_page) or 50
    if s_usuario_id is None or s_other_user_id is None:
        return []
    offset = (s_page - 1) * s_per_page
    
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
    """).bind(s_usuario_id, s_other_user_id, s_other_user_id, s_usuario_id, 
              s_per_page, offset).all()
    
    # Marcar como lidas
    await db.prepare("""
        UPDATE mensagem_direta SET lida = 1
        WHERE remetente_id = ? AND destinatarie_id = ? AND lida = 0
    """).bind(s_other_user_id, s_usuario_id).run()
    
    return [safe_dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - GRUPOS DE ESTUDO
# ============================================================================

async def create_study_group(db, nome, criador_id, descricao=None, is_public=True, max_membres=50):
    """Cria um grupo de estudo."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_nome, s_descricao, s_criador_id, s_max_membres = sanitize_params(
        nome, descricao, criador_id, max_membres
    )
    result = await db.prepare("""
        INSERT INTO grupo_estudo (nome, descricao, criador_id, is_public, max_membres)
        VALUES (?, ?, ?, ?, ?)
        RETURNING id
    """).bind(s_nome, s_descricao, s_criador_id, 1 if is_public else 0, s_max_membres).first()
    
    if result:
        # Adicionar criador como admin
        grupo_id = safe_get(result, 'id')
        if grupo_id:
            await db.prepare("""
                INSERT INTO grupo_membre (grupo_id, usuario_id, role) VALUES (?, ?, 'admin')
            """).bind(grupo_id, s_criador_id).run()
    
    return safe_get(result, 'id')


async def join_study_group(db, grupo_id, usuario_id):
    """Entrar em um grupo de estudo."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_grupo_id, s_usuario_id = sanitize_params(grupo_id, usuario_id)
    
    # Verificar limite de membros
    count = await db.prepare("""
        SELECT COUNT(*) as count FROM grupo_membre WHERE grupo_id = ?
    """).bind(s_grupo_id).first()
    
    grupo = await db.prepare("""
        SELECT max_membres FROM grupo_estudo WHERE id = ?
    """).bind(s_grupo_id).first()
    
    if count and grupo and count['count'] >= grupo['max_membres']:
        return False, "Grupo cheio"
    
    try:
        await db.prepare("""
            INSERT INTO grupo_membre (grupo_id, usuario_id) VALUES (?, ?)
        """).bind(s_grupo_id, s_usuario_id).run()
        return True, None
    except Exception:
        return False, "Já é membre do grupo"


async def leave_study_group(db, grupo_id, usuario_id):
    """Sair de um grupo de estudo."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_grupo_id, s_usuario_id = sanitize_params(grupo_id, usuario_id)
    await db.prepare("""
        DELETE FROM grupo_membre WHERE grupo_id = ? AND usuario_id = ?
    """).bind(s_grupo_id, s_usuario_id).run()


async def get_study_groups(db, usuario_id=None, apenas_meus=False):
    """Lista grupos de estudo."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    if apenas_meus and s_usuario_id:
        result = await db.prepare("""
            SELECT g.*, gm.role,
                   (SELECT COUNT(*) FROM grupo_membre WHERE grupo_id = g.id) as member_count,
                   u.username as criador_username
            FROM grupo_estudo g
            JOIN grupo_membre gm ON g.id = gm.grupo_id
            LEFT JOIN user u ON g.criador_id = u.id
            WHERE gm.usuario_id = ?
            ORDER BY g.created_at DESC
        """).bind(s_usuario_id).all()
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
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_grupo_id = sanitize_for_d1(grupo_id)
    s_page = sanitize_for_d1(page) or 1
    s_per_page = sanitize_for_d1(per_page) or 50
    if s_grupo_id is None:
        return []
    offset = (s_page - 1) * s_per_page
    
    result = await db.prepare("""
        SELECT gm.*, u.username, u.foto_perfil
        FROM grupo_mensagem gm
        LEFT JOIN user u ON gm.usuario_id = u.id
        WHERE gm.grupo_id = ?
        ORDER BY gm.created_at DESC
        LIMIT ? OFFSET ?
    """).bind(s_grupo_id, s_per_page, offset).all()
    
    return [safe_dict(row) for row in result.results] if result.results else []


async def send_group_message(db, grupo_id, usuario_id, conteudo):
    """Envia mensagem no grupo."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_grupo_id, s_usuario_id, s_conteudo = sanitize_params(grupo_id, usuario_id, conteudo)
    
    # Convert Python None to JavaScript null for D1
    # Wrap ALL parameters to prevent undefined from crossing the FFI boundary
    d1_grupo_id = to_d1_null(s_grupo_id)
    d1_usuario_id = to_d1_null(s_usuario_id)
    d1_conteudo = to_d1_null(s_conteudo)
    
    result = await db.prepare("""
        INSERT INTO grupo_mensagem (grupo_id, usuario_id, conteudo)
        VALUES (?, ?, ?)
        RETURNING id
    """).bind(d1_grupo_id, d1_usuario_id, d1_conteudo).first()
    return safe_get(result, 'id')


# ============================================================================
# QUERIES - CONTEÚDO DE ACESSIBILIDADE
# ============================================================================

async def get_accessibility_content(db, tipo_conteudo, conteudo_id):
    """Retorna conteúdo de acessibilidade (Libras/Áudio)."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_tipo_conteudo, s_conteudo_id = sanitize_params(tipo_conteudo, conteudo_id)
    if s_tipo_conteudo is None or s_conteudo_id is None:
        return None
    result = await db.prepare("""
        SELECT * FROM accessibility_content
        WHERE tipo_conteudo = ? AND conteudo_id = ?
    """).bind(s_tipo_conteudo, s_conteudo_id).first()
    
    if result:
        return safe_dict(result)
    return None


async def save_accessibility_content(db, tipo_conteudo, conteudo_id, video_libras_url=None,
                                     audio_url=None, audio_duracao=None, transcricao=None):
    """Salva ou atualiza conteúdo de acessibilidade."""
    # Sanitize all parameters to prevent D1_TYPE_ERROR from undefined values
    s_tipo_conteudo, s_conteudo_id, s_video_libras_url, s_audio_url, s_audio_duracao, s_transcricao = sanitize_params(
        tipo_conteudo, conteudo_id, video_libras_url, audio_url, audio_duracao, transcricao
    )
    if s_tipo_conteudo is None or s_conteudo_id is None:
        return
    
    existing = await get_accessibility_content(db, s_tipo_conteudo, s_conteudo_id)
    
    if existing:
        await db.prepare("""
            UPDATE accessibility_content 
            SET video_libras_url = COALESCE(?, video_libras_url),
                audio_url = COALESCE(?, audio_url),
                audio_duracao = COALESCE(?, audio_duracao),
                transcricao = COALESCE(?, transcricao),
                updated_at = datetime('now')
            WHERE tipo_conteudo = ? AND conteudo_id = ?
        """).bind(s_video_libras_url, s_audio_url, s_audio_duracao, s_transcricao,
                  s_tipo_conteudo, s_conteudo_id).run()
    else:
        await db.prepare("""
            INSERT INTO accessibility_content 
            (tipo_conteudo, conteudo_id, video_libras_url, audio_url, audio_duracao, transcricao)
            VALUES (?, ?, ?, ?, ?, ?)
        """).bind(s_tipo_conteudo, s_conteudo_id, s_video_libras_url, s_audio_url, 
                  s_audio_duracao, s_transcricao).run()


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
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id, s_autor_id, s_tipo, s_item_id = sanitize_params(usuario_id, autor_id, tipo, item_id)
    try:
        await db.prepare("""
            INSERT INTO mencao (usuario_id, autor_id, tipo, item_id, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """).bind(s_usuario_id, s_autor_id, s_tipo, s_item_id).run()
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
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_usuario_id = sanitize_for_d1(usuario_id)
    s_limit = sanitize_for_d1(limit) or 50
    s_offset = sanitize_for_d1(offset) or 0
    if s_usuario_id is None:
        return []
    results = await db.prepare("""
        SELECT m.*, u.nome as autor_nome, u.username as autor_username, u.foto_perfil as autor_foto
        FROM mencao m
        LEFT JOIN user u ON m.autor_id = u.id
        WHERE m.usuario_id = ?
        ORDER BY m.created_at DESC
        LIMIT ? OFFSET ?
    """).bind(s_usuario_id, s_limit, s_offset).all()
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
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_tag = sanitize_for_d1(tag)
    if s_tag is None:
        return None
    s_tag = s_tag.lower()
    
    # Wrap parameter to prevent D1_TYPE_ERROR
    d1_tag = to_d1_null(s_tag)
    
    result = await db.prepare(
        "SELECT * FROM hashtag WHERE tag = ?"
    ).bind(d1_tag).first()
    if result:
        return safe_dict(result)
    # Criar nova
    new_result = await db.prepare("""
        INSERT INTO hashtag (tag, count_uso, created_at)
        VALUES (?, 1, datetime('now'))
        RETURNING id
    """).bind(d1_tag).first()
    if new_result:
        new_id = safe_get(new_result, 'id')
        return {'id': new_id, 'tag': s_tag, 'count_uso': 1}
    return None


async def process_hashtags(db, text, tipo, item_id):
    """Processa hashtags em um texto e cria registros."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_tipo = sanitize_for_d1(tipo)
    s_item_id = sanitize_for_d1(item_id)
    tags = extract_hashtags(text)
    for tag in tags:
        hashtag = await get_or_create_hashtag(db, tag)
        if hashtag:
            try:
                # Adicionar item à hashtag
                hashtag_id = sanitize_for_d1(hashtag['id'])
                await db.prepare("""
                    INSERT OR IGNORE INTO hashtag_item (hashtag_id, tipo, item_id, created_at)
                    VALUES (?, ?, ?, datetime('now'))
                """).bind(hashtag_id, s_tipo, s_item_id).run()
                # Incrementar contador
                await db.prepare(
                    "UPDATE hashtag SET count_uso = count_uso + 1 WHERE id = ?"
                ).bind(hashtag_id).run()
            except Exception:
                pass
    return tags


async def get_trending_hashtags(db, limit=10):
    """Busca hashtags mais populares."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_limit = sanitize_for_d1(limit) or 10
    results = await db.prepare("""
        SELECT * FROM hashtag
        ORDER BY count_uso DESC
        LIMIT ?
    """).bind(s_limit).all()
    return [safe_dict(r) for r in results.results] if results.results else []


async def search_by_hashtag(db, tag, tipo=None, limit=50, offset=0):
    """Busca posts/comentários por hashtag."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_tag = sanitize_for_d1(tag)
    s_limit = sanitize_for_d1(limit) or 50
    s_offset = sanitize_for_d1(offset) or 0
    if s_tag is None:
        return []
    s_tag = s_tag.lower().replace('#', '')
    
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
    """).bind(s_tag, s_limit, s_offset).all()
    
    return [safe_dict(r) for r in results.results] if results.results else []


# ============================================================================
# EMOJIS PERSONALIZADOS NÃO-BINÁRIOS
# ============================================================================

async def create_emoji_custom(db, codigo, nome, imagem_url, descricao=None, categoria='geral', created_by=None):
    """Cria um emoji personalizado."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_codigo = sanitize_for_d1(codigo)
    s_nome = sanitize_for_d1(nome)
    s_imagem_url = sanitize_for_d1(imagem_url)
    s_descricao = sanitize_for_d1(descricao)
    s_categoria = sanitize_for_d1(categoria) or 'geral'
    s_created_by = sanitize_for_d1(created_by)
    
    if s_codigo is None or s_nome is None or s_imagem_url is None:
        return None
    
    # Formatar código: remover espaços, adicionar colons se não tiver
    s_codigo = s_codigo.strip().lower().replace(' ', '_')
    if not s_codigo.startswith(':'):
        s_codigo = f':{s_codigo}:'
    elif not s_codigo.endswith(':'):
        s_codigo = f'{s_codigo}:'
    
    try:
        result = await db.prepare("""
            INSERT INTO emoji_custom (codigo, nome, imagem_url, descricao, categoria, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
            RETURNING id
        """).bind(s_codigo, s_nome, s_imagem_url, s_descricao, s_categoria, s_created_by).first()
        return safe_get(result, 'id')
    except Exception:
        return None


async def get_emojis_custom(db, categoria=None, ativo_only=True):
    """Busca emojis personalizados."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_categoria = sanitize_for_d1(categoria)
    if s_categoria and ativo_only:
        results = await db.prepare("""
            SELECT * FROM emoji_custom
            WHERE categoria = ? AND ativo = 1
            ORDER BY ordem, nome
        """).bind(s_categoria).all()
    elif s_categoria:
        results = await db.prepare("""
            SELECT * FROM emoji_custom
            WHERE categoria = ?
            ORDER BY ordem, nome
        """).bind(s_categoria).all()
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
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_codigo = sanitize_for_d1(codigo)
    if s_codigo is None:
        return None
    
    # Wrap parameter to prevent D1_TYPE_ERROR
    d1_codigo = to_d1_null(s_codigo)
    
    result = await db.prepare(
        "SELECT * FROM emoji_custom WHERE codigo = ? AND ativo = 1"
    ).bind(d1_codigo).first()
    return safe_dict(result) if result else None


async def update_emoji_custom(db, emoji_id, **kwargs):
    """Atualiza um emoji."""
    # Sanitize emoji_id to prevent D1_TYPE_ERROR from undefined values
    s_emoji_id = sanitize_for_d1(emoji_id)
    if s_emoji_id is None:
        return False
    allowed = ['nome', 'descricao', 'imagem_url', 'categoria', 'ordem', 'ativo']
    # Sanitize all kwargs values and filter out None values in one pass
    updates = {k: v for k, v in ((k, sanitize_for_d1(v)) for k, v in kwargs.items() if k in allowed) if v is not None}
    
    if not updates:
        return False
    
    # Construir query com placeholders
    set_parts = []
    values = []
    for key, value in updates.items():
        set_parts.append(f"{key} = ?")
        values.append(value)
    
    values.append(s_emoji_id)
    
    query = f"UPDATE emoji_custom SET {', '.join(set_parts)} WHERE id = ?"
    await db.prepare(query).bind(*values).run()
    return True


async def delete_emoji_custom(db, emoji_id):
    """Deleta um emoji."""
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_emoji_id = sanitize_for_d1(emoji_id)
    if s_emoji_id is None:
        return False
    
    # Wrap parameter to prevent D1_TYPE_ERROR
    d1_emoji_id = to_d1_null(s_emoji_id)
    
    await db.prepare("DELETE FROM emoji_custom WHERE id = ?").bind(d1_emoji_id).run()
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
    # Sanitize parameter to prevent D1_TYPE_ERROR from undefined values
    s_nome = sanitize_for_d1(nome)
    if s_nome is None:
        return True
    
    # Wrap parameter to prevent D1_TYPE_ERROR
    d1_nome = to_d1_null(s_nome)
    
    result = await db.prepare(
        "SELECT ativo FROM feature_flag WHERE nome = ?"
    ).bind(d1_nome).first()
    return bool(safe_get(result, 'ativo', 1)) if result else True


async def get_all_feature_flags(db):
    """Busca todas as feature flags."""
    results = await db.prepare(
        "SELECT * FROM feature_flag ORDER BY nome"
    ).all()
    return [safe_dict(r) for r in results.results] if results.results else []


async def update_feature_flag(db, nome, ativo, updated_by=None):
    """Atualiza uma feature flag."""
    # Sanitize parameters to prevent D1_TYPE_ERROR from undefined values
    s_nome, s_ativo, s_updated_by = sanitize_params(nome, ativo, updated_by)
    if s_nome is None:
        return False
    await db.prepare("""
        UPDATE feature_flag 
        SET ativo = ?, updated_at = datetime('now'), updated_by = ?
        WHERE nome = ?
    """).bind(s_ativo, s_updated_by, s_nome).run()
    return True
