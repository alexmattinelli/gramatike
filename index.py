# index.py
# Flask WSGI entrypoint for Cloudflare Workers/Pages (Python)
# This file is at the root level so it can directly import gramatike_app
# without sys.path manipulation (which doesn't work in Pyodide).

from gramatike_app import create_app

# Cria o app Flask usando a factory
app = create_app()

# Endpoint básico de saúde para teste
@app.get("/api/health")
def _health():
    return {"status": "ok"}
