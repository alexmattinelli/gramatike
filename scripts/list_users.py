import sys
import os

# Ensure project root on sys.path
try:
	_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
	if _ROOT not in sys.path:
		sys.path.insert(0, _ROOT)
except Exception:
	pass

from gramatike_app import create_app
from gramatike_app.models import db, User


def main():
	app = create_app()
	with app.app_context():
		users = User.query.order_by(User.id.asc()).all()
		rows = [(u.id, u.username, u.email, getattr(u, 'is_admin', False), getattr(u, 'is_superadmin', False)) for u in users]
		print("Users:", rows)


if __name__ == "__main__":
	main()

