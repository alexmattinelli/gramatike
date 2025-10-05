import os
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me')
    # Use DATABASE_URL se fornecido; senão SQLite local na pasta instance (caminho absoluto)
    _ROOT = os.path.dirname(os.path.abspath(__file__))
    _DEFAULT_SQLITE_PATH = os.path.join(_ROOT, 'instance', 'app.db')
    # Normaliza para formato URI (barras) para evitar problemas de escape no Windows
    _SQLITE_POSIX = _DEFAULT_SQLITE_PATH.replace('\\', '/')
    _RAW_DB_URL = os.environ.get('DATABASE_URL')
    if _RAW_DB_URL:
        # Normaliza esquemas antigos 'postgres://' para 'postgresql+psycopg2://'
        if _RAW_DB_URL.startswith('postgres://'):
            _RAW_DB_URL = 'postgresql+psycopg2://' + _RAW_DB_URL[len('postgres://'):]
        # Remove channel_binding=require (incompatível em alguns ambientes psycopg2/libpq)
        try:
            parts = urlsplit(_RAW_DB_URL)
            if parts.query:
                q = [(k, v) for (k, v) in parse_qsl(parts.query, keep_blank_values=True) if k.lower() != 'channel_binding']
                _RAW_DB_URL = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q), parts.fragment))
        except Exception:
            pass
        SQLALCHEMY_DATABASE_URI = _RAW_DB_URL
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{_SQLITE_POSIX}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    # CSRF em formulários; para APIs usamos isenção no app
    WTF_CSRF_ENABLED = True
    # Opções extras do engine para conexões estáveis em ambientes serverless
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        # Em serverless, manter pool pequeno evita retenção desnecessária
        'pool_size': int(os.environ.get('DB_POOL_SIZE', '1') or '1'),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', '2') or '2'),
    }
