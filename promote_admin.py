from gramatike_app import create_app
from gramatike_app.models import db, User
import argparse

def promote(username: str, superadmin: bool=False):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f'Usuárie "{username}" não encontrade.')
            return
        changed = False
        if superadmin and not getattr(user, 'is_superadmin', False):
            user.is_superadmin = True
            user.is_admin = True
            changed = True
        elif not user.is_admin:
            user.is_admin = True
            changed = True
        if changed:
            db.session.commit()
            nivel = 'superadmin' if superadmin else 'admin'
            print(f'Usuárie "{username}" promovide a {nivel} com sucesso!')
        else:
            print(f'Nenhuma alteração necessária para "{username}".')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', default='alex.mattinelli')
    parser.add_argument('--superadmin', action='store_true')
    args = parser.parse_args()
    promote(args.username, args.superadmin)
