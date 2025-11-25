# index.py
# FastAPI entrypoint for Cloudflare Workers/Pages (Python)
# This file uses the WorkerEntrypoint pattern with ASGI.
#
# Note: This application was migrated from Flask to FastAPI
# because Flask is not supported on Cloudflare Workers Python (Pyodide).

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from workers import WorkerEntrypoint

# Create FastAPI app
app = FastAPI(
    title="Gramátike",
    description="Portuguese grammar education platform",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Home page."""
    return JSONResponse({
        "message": "Bem-vindo ao Gramátike!",
        "status": "online",
        "version": "1.0.0",
        "note": "Esta aplicação foi migrada para FastAPI para compatibilidade com Cloudflare Workers Python."
    })


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/info")
async def info():
    """Application information."""
    return {
        "name": "Gramátike",
        "framework": "FastAPI",
        "platform": "Cloudflare Workers Python",
        "description": "Plataforma educacional de gramática portuguesa"
    }


class Default(WorkerEntrypoint):
    """Cloudflare Worker entry point that delegates to FastAPI via ASGI."""
    
    async def fetch(self, request):
        """Handle incoming requests by delegating to the FastAPI ASGI app."""
        import asgi
        return await asgi.fetch(app, request.js_object, self.env)
