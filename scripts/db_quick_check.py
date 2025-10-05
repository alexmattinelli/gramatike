import sys
import os

try:
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
except Exception:
    pass

from gramatike_app import create_app
from gramatike_app.models import User


def main():
    app = create_app()
    with app.app_context():
        n = User.query.count()
        print(f"DB OK. User count: {n}")


if __name__ == "__main__":
    main()
