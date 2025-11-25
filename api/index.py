# api/index.py
# Flask WSGI entrypoint for serverless platforms (Cloudflare Pages/Workers, etc.)
# Exposes `app` so the platform can detect and serve the Flask application.

# Add project root to sys.path so Cloudflare Workers can find gramatike_app module
import os
import sys
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from gramatike_app import create_app

# Cria o app Flask usando a factory
app = create_app()

# Endpoint básico de saúde para teste
@app.get("/api/health")
def _health():
    return {"status": "ok"}
