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


def ensure_user(username: str, email: str | None, password: str | None, admin: bool, superadmin: bool) -> int:
	app = create_app()
	with app.app_context():
		u = User.query.filter((User.username == username) | (User.email == email)).first() if email else User.query.filter_by(username=username).first()
		created = False
		if not u:
			if not email:
				# fallback email
				email = f"{username}@example.local"
			u = User(username=username, email=email)
			created = True
		# Apply flags
		if superadmin:
			u.is_superadmin = True
			u.is_admin = True
		elif admin:
			u.is_admin = True
		# Set password if provided
		if password:
			try:
				u.set_password(password)
			except Exception:
				# Ensure we can set even if previous state invalid
				from werkzeug.security import generate_password_hash
				u.password = generate_password_hash(password)
		# Persist
		if created:
			db.session.add(u)
		db.session.commit()
		nivel = 'superadmin' if superadmin else ('admin' if admin else 'user')
		print(f"OK: {('Criade' if created else 'Atualizade')} usuárie '{u.username}' <{u.email}>, nível={nivel}")
		return 0


if __name__ == "__main__":
	p = argparse.ArgumentParser()
	p.add_argument('--username', required=True)
	p.add_argument('--email')
	p.add_argument('--password')
	p.add_argument('--admin', action='store_true')
	p.add_argument('--superadmin', action='store_true')
	args = p.parse_args()
	raise SystemExit(ensure_user(args.username, args.email, args.password, args.admin, args.superadmin))

