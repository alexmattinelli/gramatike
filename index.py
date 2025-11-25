# index.py
# Flask WSGI entrypoint for Cloudflare Workers/Pages (Python)
# This file uses the WorkerEntrypoint pattern with ASGI adapter
# to make Flask work with Cloudflare's async Python runtime.

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
