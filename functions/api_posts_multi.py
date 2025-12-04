"""
API Posts Multi handler for Cloudflare Workers
Handles multi-image post creation
"""
import json
from datetime import datetime

try:
    from workers import Response
except ImportError:
    from starlette.responses import Response

from gramatike_d1.auth import get_current_user


def json_response(data, status=200):
    """Create a JSON response."""
    return Response(
        json.dumps(data, ensure_ascii=False),
        status=status,
        headers={'Content-Type': 'application/json; charset=utf-8'}
    )


async def on_request(request, env, context):
    """Handle post creation with multiple images."""
    
    method = getattr(request, 'method', 'GET')
    if method != 'POST':
        return json_response({'error': 'Método não permitido'}, 405)
    
    db = getattr(env, 'DB', None) if env else None
    if not db:
        return json_response({'error': 'Serviço indisponível'}, 503)
    
    # Get current user from session
    try:
        user = await get_current_user(db, request)
        if not user:
            return json_response({'success': False, 'error': 'Não autenticado'}, 401)
        usuario_id = user['id']
    except Exception as e:
        print(f"[posts_multi] Auth error: {e}")
        return json_response({'success': False, 'error': 'Erro de autenticação'}, 401)
    
    try:
        # Get content-type header to determine parsing method
        # In Cloudflare Workers, body can only be consumed ONCE
        content_type = ''
        try:
            headers = request.headers
            if hasattr(headers, 'get'):
                content_type = headers.get('content-type', '') or ''
            elif hasattr(headers, '__getitem__'):
                content_type = headers.get('content-type', '') or ''
            # Handle JsProxy
            if hasattr(content_type, 'to_py'):
                content_type = content_type.to_py()
            content_type = str(content_type).lower() if content_type else ''
        except Exception as ct_err:
            print(f"[posts_multi] Error getting content-type: {ct_err}")
            content_type = ''
        
        print(f"[posts_multi] Content-Type: {content_type}")
        
        # Parse request body based on content-type
        # IMPORTANT: Only use ONE parsing method to avoid "body already used" error
        conteudo = None
        
        if 'multipart/form-data' in content_type:
            # Use formData() for multipart/form-data
            try:
                data = await request.formData()
                conteudo_raw = data.get('conteudo')
                
                # Convert JsProxy to Python string if needed
                if conteudo_raw is not None:
                    if hasattr(conteudo_raw, 'to_py'):
                        try:
                            conteudo = conteudo_raw.to_py()
                        except (TypeError, AttributeError):
                            conteudo = str(conteudo_raw) if conteudo_raw else None
                    else:
                        conteudo = str(conteudo_raw) if conteudo_raw else None
            except Exception as e:
                print(f"[posts_multi] FormData parse failed: {e}")
                return json_response({'success': False, 'error': 'Erro ao processar formulário'}, 400)
        
        elif 'application/json' in content_type:
            # Use json() for application/json
            try:
                body = await request.json()
                if hasattr(body, 'to_py'):
                    body = body.to_py()
                conteudo = body.get('conteudo') if isinstance(body, dict) else None
            except Exception as e:
                print(f"[posts_multi] JSON parse failed: {e}")
                return json_response({'success': False, 'error': 'Erro ao processar JSON'}, 400)
        
        else:
            # Default: try formData() as it's most common for this endpoint
            print(f"[posts_multi] Unknown content-type: {content_type}, trying formData()")
            try:
                data = await request.formData()
                conteudo_raw = data.get('conteudo')
                
                if conteudo_raw is not None:
                    if hasattr(conteudo_raw, 'to_py'):
                        try:
                            conteudo = conteudo_raw.to_py()
                        except (TypeError, AttributeError):
                            conteudo = str(conteudo_raw) if conteudo_raw else None
                    else:
                        conteudo = str(conteudo_raw) if conteudo_raw else None
            except Exception as e:
                print(f"[posts_multi] formData() failed for unknown content-type: {e}")
                return json_response({'success': False, 'error': 'Tipo de conteúdo não suportado'}, 400)
        
        # Validate content
        if conteudo is not None:
            conteudo = str(conteudo).strip()
        
        if not conteudo:
            return json_response({'success': False, 'error': 'conteudo_vazio'}, 400)
        
        # Create post
        now = datetime.utcnow().isoformat()
        sql = "INSERT INTO post (usuario_id, conteudo, created_at) VALUES (?, ?, ?)"
        await db.prepare(sql).bind(usuario_id, conteudo, now).run()
        
        # Get created post ID
        result = await db.prepare('SELECT last_insert_rowid() as id').first()
        post_id = result['id'] if result else 0
        
        return json_response({'success': True, 'id': post_id, 'imagens': []}, 201)
        
    except Exception as e:
        print(f"[posts_multi] Unexpected error: {e}")
        return json_response({'success': False, 'error': str(e)}, 500)


handler = on_request
