import sys, os
# Ensure project root on sys.path
try:
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
except Exception:
    pass

from gramatike_app import create_app
from gramatike_app.models import db, User
import argparse

def reset_password(ident: str, password: str) -> int:
    app = create_app()
    with app.app_context():
        from sqlalchemy import or_
        user = User.query.filter(or_(User.email==ident, User.username==ident)).first()
        if not user:
            print(f"Usuárie não encontrade: {ident}")
            return 1
        user.set_password(password)
        db.session.commit()
        print(f"Senha redefinida para: {user.username} ({user.email})")
        return 0

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('--ident', required=True, help='username ou email')
    p.add_argument('--password', required=True)
    args = p.parse_args()
    raise SystemExit(reset_password(args.ident, args.password))
