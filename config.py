import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me')
    # Use DATABASE_URL se fornecido; senão SQLite local na pasta instance (caminho absoluto)
    _ROOT = os.path.dirname(os.path.abspath(__file__))
    _DEFAULT_SQLITE_PATH = os.path.join(_ROOT, 'instance', 'app.db')
    # Normaliza para formato URI (barras) para evitar problemas de escape no Windows
    _SQLITE_POSIX = _DEFAULT_SQLITE_PATH.replace('\\', '/')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{_SQLITE_POSIX}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    # CSRF em formulários; para APIs usamos isenção no app
    WTF_CSRF_ENABLED = True
