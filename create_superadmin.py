from gramatike_app import create_app
from gramatike_app.models import db, User

USERNAME='gramatike'
EMAIL='admin@gramatike.local'
PASSWORD='ChangeMe123'

def ensure():
    app=create_app()
    with app.app_context():
        u=User.query.filter_by(username=USERNAME).first()
        if u:
            changed = False
            if not u.is_superadmin:
                u.is_superadmin=True
                u.is_admin=True
                changed = True
            # Garante que a senha definida esteja correta (hash)
            try:
                if not u.check_password(PASSWORD):
                    u.set_password(PASSWORD)
                    changed = True
            except Exception:
                u.set_password(PASSWORD)
                changed = True
            if changed:
                db.session.commit()
                print('Superadmin ajustado (nível e/ou senha atualizada).')
            else:
                print('Superadmin já existe e está configurade.')
        else:
            u=User(username=USERNAME,email=EMAIL,is_admin=True)
            u.is_superadmin=True
            u.set_password(PASSWORD)
            db.session.add(u)
            db.session.commit()
            print('Superadmin criado.')

if __name__=='__main__':
    ensure()
