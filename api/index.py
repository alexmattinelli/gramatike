# api/index.py
# Flask WSGI entrypoint for serverless platforms (Cloudflare Pages/Workers, etc.)
# Exposes `app` so the platform can detect and serve the Flask application.

from gramatike_app import create_app

# Cria o app Flask usando a factory
app = create_app()

# Endpoint básico de saúde para teste
@app.get("/api/health")
def _health():
    return {"status": "ok"}
