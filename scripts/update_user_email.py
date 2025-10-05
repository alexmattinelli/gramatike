import sys, os
import argparse

# Ensure project root on sys.path
try:
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
except Exception:
    pass

from gramatike_app import create_app
from gramatike_app.models import db, User


def update_email(ident: str, new_email: str) -> int:
    app = create_app()
    with app.app_context():
        from sqlalchemy import or_
        u = User.query.filter(or_(User.username == ident, User.email == ident)).first()
        if not u:
            print(f"Usuárie não encontrade: {ident}")
            return 1
        # Check if new email is used by someone else
        exists = User.query.filter(User.email == new_email, User.id != u.id).first()
        if exists:
            print(f"Falha: e-mail '{new_email}' já está em uso por outra conta (@{exists.username}).")
            return 2
        u.email = new_email
        try:
            u.email_confirmed = False
        except Exception:
            pass
        db.session.commit()
        print(f"OK: e-mail de @{u.username} atualizado para {u.email}")
        return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description='Atualiza e-mail de um usuárie (por username ou e-mail atual).')
    p.add_argument('--ident', required=True, help='username ou e-mail atual')
    p.add_argument('--new-email', required=True, help='novo e-mail desejado')
    args = p.parse_args()
    raise SystemExit(update_email(args.ident, args.new_email))
