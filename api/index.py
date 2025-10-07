# api/index.py
# Vercel Python entrypoint for Flask (WSGI)
# Exposes `app` so Vercel can detect and serve the Flask application.

from gramatike_app import create_app

# Cria o app Flask usando a factory
app = create_app()

# Endpoint básico de saúde para teste
@app.get("/api/health")
def _health():
    return {"status": "ok"}
