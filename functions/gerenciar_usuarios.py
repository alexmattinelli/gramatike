"""
Gerenciar Usuários page handler for Cloudflare Workers
"""
try:
    from workers import Response
except ImportError:
    from starlette.responses import Response

from ._template_processor import render_template


async def on_request(request, env, context):
    """Handle gerenciar usuários page requests."""
    html = render_template('gerenciar_usuarios.html')
    return Response(html, headers={'Content-Type': 'text/html; charset=utf-8'})


handler = on_request
