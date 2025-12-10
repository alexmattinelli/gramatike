"""
Login page handler for Cloudflare Workers
"""
from urllib.parse import parse_qs

try:
    from workers import Response
except ImportError:
    from starlette.responses import Response

from ._template_processor import render_template, create_error_html


async def on_request(request, env, context):
    """Handle login page requests."""
    
    error_html = ''
    method = getattr(request, 'method', 'GET')
    
    # Handle POST - login attempt
    if method == 'POST':
        try:
            body_text = await request.text()
            form_data = parse_qs(body_text)
            
            email = form_data.get('email', [''])[0].strip()
            password = form_data.get('password', [''])[0]
            
            if not email or not password:
                error_html = create_error_html('Preencha todos os campos')
            else:
                db = getattr(env, 'DB', None) if env else None
                if db:
                    try:
                        from gramatike_d1.auth import login, set_session_cookie
                        token, err = await login(db, request, email, password)
                        if token:
                            return Response(
                                '',
                                status=302,
                                headers={
                                    'Location': '/feed',
                                    'Set-Cookie': set_session_cookie(token)
                                }
                            )
                        else:
                            error_html = create_error_html(err or 'Credenciais inválidas')
                    except Exception as e:
                        error_html = create_error_html('Erro ao processar login.')
                else:
                    error_html = create_error_html('Serviço temporariamente indisponível.')
        except Exception:
            error_html = create_error_html('Erro ao processar requisição.')
    
    html = render_template('login.html', flash_html=error_html)
    return Response(html, headers={'Content-Type': 'text/html; charset=utf-8'})


handler = on_request
