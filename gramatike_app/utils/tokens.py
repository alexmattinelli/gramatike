from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app


def _get_serializer() -> URLSafeTimedSerializer:
    secret = current_app.config.get('SECRET_KEY') or 'change-me'
    salt = current_app.config.get('SECURITY_SALT', 'gramatike-salt')
    return URLSafeTimedSerializer(secret_key=secret, salt=salt)


def generate_token(data: dict) -> str:
    s = _get_serializer()
    return s.dumps(data)


def verify_token(token: str, max_age: int = 3600) -> dict | None:
    s = _get_serializer()
    try:
        return s.loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
