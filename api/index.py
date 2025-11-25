# api/index.py
# Flask WSGI entrypoint for serverless platforms (Cloudflare Pages/Workers, etc.)
# Uses WorkerEntrypoint pattern with ASGI adapter for Cloudflare Workers Python.

# Add project root to sys.path so Cloudflare Workers can find gramatike_app module
import os
import sys
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from gramatike_app import create_app
from asgiref.wsgi import WsgiToAsgi
from workers import WorkerEntrypoint
import asgi

# Cria o app Flask usando a factory
flask_app = create_app()

# Endpoint básico de saúde para teste
@flask_app.get("/api/health")
def _health():
    return {"status": "ok"}

# Converte Flask (WSGI) para ASGI para funcionar com Cloudflare Workers
app = WsgiToAsgi(flask_app)


class Default(WorkerEntrypoint):
    """Cloudflare Worker entry point that delegates to Flask via ASGI."""
    
    async def fetch(self, request):
        """Handle incoming requests by delegating to the Flask ASGI app."""
        return await asgi.fetch(app, request.js_object, self.env)
