# index.py
# Cloudflare Workers Python entry point
# Uses native WorkerEntrypoint pattern (no FastAPI - not supported in Workers)
# Docs: https://developers.cloudflare.com/workers/languages/python/
#
# NOTE: FastAPI is NOT supported in Cloudflare Workers Python deployment.
# See: https://github.com/cloudflare/workers-sdk/issues/5608
#
# This minimal handler provides basic API endpoints for the Cloudflare Workers.
# The full Flask application continues to run on other platforms.

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


def html_response(content, status=200):
    """Create an HTML response."""
    return Response(
        content,
        status=status,
        headers={"Content-Type": "text/html; charset=utf-8"}
    )


class Default(WorkerEntrypoint):
    """Cloudflare Worker entry point - minimal handler for Python Workers."""

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
            return html_response(self._home_page())

        elif path == "/api/health":
            return json_response({
                "status": "ok",
                "platform": "Cloudflare Workers Python",
                "message": "Gramatike API esta online"
            })

        elif path == "/api/info":
            return json_response({
                "name": "Gramatike",
                "description": "Plataforma educacional de gramatica portuguesa",
                "platform": "Cloudflare Workers Python",
                "version": "1.0.0"
            })

        elif path == "/login":
            return html_response(self._login_page())

        elif path == "/cadastro":
            return html_response(self._cadastro_page())

        elif path == "/educacao":
            return html_response(self._educacao_page())

        else:
            return json_response(
                {"error": "Rota nao encontrada", "path": path},
                status=404
            )

    def _home_page(self):
        """Generate home page HTML."""
        return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gramatike - Gramatica Portuguesa</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #9b5de5, #f15bb5, #fee440);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 24px;
            padding: 48px;
            max-width: 500px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
        }
        h1 { color: #9b5de5; font-size: 2.5em; margin-bottom: 16px; }
        p { color: #666; font-size: 1.1em; line-height: 1.6; margin-bottom: 24px; }
        .status { 
            background: #e8f5e9; 
            color: #2e7d32; 
            padding: 12px 24px; 
            border-radius: 12px;
            display: inline-block;
            margin-bottom: 24px;
        }
        .links { margin-top: 24px; }
        .links a {
            display: inline-block;
            background: #9b5de5;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            margin: 8px;
            transition: transform 0.2s, background 0.2s;
        }
        .links a:hover {
            background: #7b4bc9;
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Gramatike</h1>
        <p>Plataforma educacional de gramatica portuguesa</p>
        <div class="status">Sistema online</div>
        <p>Bem-vinde ao Gramatike! Esta e a versao do Cloudflare Workers.</p>
        <div class="links">
            <a href="/api/health">API Health</a>
            <a href="/api/info">API Info</a>
            <a href="/educacao">Educacao</a>
        </div>
    </div>
</body>
</html>"""

    def _login_page(self):
        """Generate login page HTML."""
        return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Gramatike</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #9b5de5, #f15bb5);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 24px;
            padding: 48px;
            max-width: 400px;
            width: 90%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
        }
        h1 { color: #9b5de5; margin-bottom: 24px; }
        .info { color: #666; margin-bottom: 24px; }
        a { color: #9b5de5; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Login</h1>
        <p class="info">Versao Cloudflare Workers - em desenvolvimento.</p>
        <p><a href="/">Voltar ao inicio</a></p>
    </div>
</body>
</html>"""

    def _cadastro_page(self):
        """Generate registration page HTML."""
        return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cadastro - Gramatike</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #9b5de5, #f15bb5);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 24px;
            padding: 48px;
            max-width: 400px;
            width: 90%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
        }
        h1 { color: #9b5de5; margin-bottom: 24px; }
        .info { color: #666; margin-bottom: 24px; }
        a { color: #9b5de5; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Cadastro</h1>
        <p class="info">Versao Cloudflare Workers - em desenvolvimento.</p>
        <p><a href="/">Voltar ao inicio</a></p>
    </div>
</body>
</html>"""

    def _educacao_page(self):
        """Generate education hub page HTML."""
        return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Educacao - Gramatike</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #9b5de5, #fee440);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 24px;
            padding: 48px;
            max-width: 600px;
            width: 90%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
        }
        h1 { color: #9b5de5; margin-bottom: 24px; }
        .info { color: #666; margin-bottom: 24px; line-height: 1.6; }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin: 24px 0;
        }
        .feature {
            background: #f8f4ff;
            padding: 20px;
            border-radius: 12px;
        }
        .feature h3 { color: #9b5de5; margin-bottom: 8px; }
        .feature p { color: #666; font-size: 0.9em; }
        a { color: #9b5de5; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Gramatike Educacao</h1>
        <p class="info">Aprenda gramatica portuguesa de forma divertida e inclusiva!</p>
        <div class="features">
            <div class="feature">
                <h3>Artigos</h3>
                <p>Conteudo educacional</p>
            </div>
            <div class="feature">
                <h3>Apostilas</h3>
                <p>Material de estudo</p>
            </div>
            <div class="feature">
                <h3>Podcasts</h3>
                <p>Aprenda ouvindo</p>
            </div>
            <div class="feature">
                <h3>Exercicios</h3>
                <p>Pratique gramatica</p>
            </div>
        </div>
        <p class="info">Esta e a versao Cloudflare Workers - em desenvolvimento.</p>
        <p><a href="/">Voltar ao inicio</a></p>
    </div>
</body>
</html>"""
