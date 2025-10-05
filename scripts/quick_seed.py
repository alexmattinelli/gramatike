import sys
import os
from datetime import datetime, timedelta

# Ensure project root on sys.path
try:
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
except Exception:
    pass

from gramatike_app import create_app
from gramatike_app.models import db, User, Post


def main():
    app = create_app()
    with app.app_context():
        created = False
        if User.query.count() == 0:
            u = User(username='alex', email='alex@example.com')
            try:
                u.set_password('123')
            except Exception:
                from werkzeug.security import generate_password_hash
                u.password = generate_password_hash('123')
            db.session.add(u)
            db.session.commit()
            created = True
        user = User.query.filter_by(username='alex').first()
        if user and Post.query.count() == 0:
            for i in range(3):
                p = Post(usuario='alex', usuario_id=user.id, conteudo=f'Post #{i} #tag', imagem='', data=datetime.utcnow()-timedelta(days=i))
                db.session.add(p)
            db.session.commit()
        users = User.query.order_by(User.id.asc()).all()
        print("OK: DB acessível. Usuários:", [(u.id, u.username, u.email) for u in users], "seed_criado="+str(created))


if __name__ == "__main__":
    main()
