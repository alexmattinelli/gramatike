"""
Cadastro (registration) page handler for Cloudflare Workers
"""
from urllib.parse import parse_qs

try:
    from workers import Response
except ImportError:
    from starlette.responses import Response

from ._template_processor import render_template, create_error_html, create_success_html


async def on_request(request, env, context):
    """Handle registration page requests."""
    
    flash_html = ''
    method = getattr(request, 'method', 'GET')
    
    if method == 'POST':
        try:
            body_text = await request.text()
            form_data = parse_qs(body_text)
            
            username = form_data.get('username', [''])[0].strip()
            email = form_data.get('email', [''])[0].strip()
            password = form_data.get('password', [''])[0]
            nome = form_data.get('nome', [''])[0].strip()
            
            if not username or not email or not password:
                flash_html = create_error_html('Preencha todos os campos obrigatórios')
            else:
                db = getattr(env, 'DB', None) if env else None
                if db:
                    try:
                        from gramatike_d1.auth import register, login, set_session_cookie
                        user_id, err = await register(db, username, email, password, nome)
                        if user_id:
                            # Auto-login after registration
                            token, _ = await login(db, request, email, password)
                            if token:
                                return Response(
                                    '',
                                    status=302,
                                    headers={
                                        'Location': '/',
                                        'Set-Cookie': set_session_cookie(token)
                                    }
                                )
                            flash_html = create_success_html('Conta criada! Faça login.')
                        else:
                            flash_html = create_error_html(err or 'Erro ao criar conta')
                    except Exception:
                        flash_html = create_error_html('Erro ao processar cadastro.')
                else:
                    flash_html = create_error_html('Serviço temporariamente indisponível.')
        except Exception:
            flash_html = create_error_html('Erro ao processar requisição.')
    
    html = render_template('cadastro.html', flash_html=flash_html)
    return Response(html, headers={'Content-Type': 'text/html; charset=utf-8'})


handler = on_request
