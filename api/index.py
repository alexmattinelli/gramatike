# api/index.py
# Cloudflare Workers Python API entry point
# Uses native WorkerEntrypoint pattern (no FastAPI - not supported in Workers)
#
# NOTE: FastAPI is NOT supported in Cloudflare Workers Python deployment.
# See: https://github.com/cloudflare/workers-sdk/issues/5608
#
# This file provides an alternative entry point in the api/ directory.
# The main entry point is in index.py at the project root.

import json
from urllib.parse import urlparse
from workers import WorkerEntrypoint, Response


def json_response(data, status=200):
    """Create a JSON response."""
    return Response(
        json.dumps(data),
        status=status,
        headers={"Content-Type": "application/json"}
    )


class Default(WorkerEntrypoint):
    """Cloudflare Worker entry point for API endpoints."""

    async def fetch(self, request):
        """Handle incoming HTTP requests."""
        url = request.url
        
        # Parse path from URL
        path = "/"
        if url:
            parsed = urlparse(url)
            path = parsed.path or "/"

        # Route handling
        if path == "/" or path == "":
            return json_response({
                "message": "Bem-vindo ao Gramatike!",
                "status": "online",
                "version": "1.0.0",
                "platform": "Cloudflare Workers Python"
            })

        elif path == "/api/health":
            return json_response({
                "status": "ok",
                "platform": "Cloudflare Workers Python"
            })

        elif path == "/api/info":
            return json_response({
                "name": "Gramatike",
                "description": "Plataforma educacional de gramatica portuguesa",
                "platform": "Cloudflare Workers Python",
                "version": "1.0.0"
            })

        else:
            return json_response(
                {"error": "Rota nao encontrada", "path": path},
                status=404
            )
