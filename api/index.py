# Vercel Python entrypoint for Flask (WSGI)
# Exposes `app` so Vercel can detect and serve the Flask application.

from gramatike_app import create_app

# Create the Flask WSGI app
app = create_app()

# Basic health endpoint to help verify function is alive on Vercel
@app.get("/api/health")
def _health():
	return {"status": "ok"}

# Optional alias used by some runtimes
handler = app
