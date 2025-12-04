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
                try:
                    content_type = headers['content-type'] or ''
                except (KeyError, TypeError):
                    content_type = ''
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
            # Parse multipart/form-data manually since formData() is not available in Pyodide
            try:
                body_bytes = await request.arrayBuffer()
                if hasattr(body_bytes, 'to_py'):
                    body_bytes = body_bytes.to_py()
                # Convert to bytes if needed
                if hasattr(body_bytes, 'to_bytes'):
                    body_bytes = body_bytes.to_bytes()
                elif isinstance(body_bytes, memoryview):
                    body_bytes = bytes(body_bytes)
                
                # Try to decode as text for simple form parsing
                try:
                    body_text = body_bytes.decode('utf-8') if isinstance(body_bytes, bytes) else str(body_bytes)
                except (UnicodeDecodeError, AttributeError):
                    body_text = str(body_bytes)
                
                # Extract boundary from content-type
                boundary = None
                if 'boundary=' in content_type:
                    boundary = content_type.split('boundary=')[1].split(';')[0].strip()
                    if boundary.startswith('"') and boundary.endswith('"'):
                        boundary = boundary[1:-1]
                
                # Parse multipart data to extract 'conteudo' field
                if boundary and body_text:
                    # Split by boundary
                    parts = body_text.split('--' + boundary)
                    for part in parts:
                        if 'name="conteudo"' in part or "name='conteudo'" in part:
                            # Extract value after the double newline
                            if '\r\n\r\n' in part:
                                value = part.split('\r\n\r\n', 1)[1]
                                # Remove trailing boundary markers
                                if value.endswith('\r\n'):
                                    value = value[:-2]
                                if value.endswith('--'):
                                    value = value[:-2]
                                conteudo = value.strip()
                                break
                            elif '\n\n' in part:
                                value = part.split('\n\n', 1)[1]
                                if value.endswith('\n'):
                                    value = value[:-1]
                                if value.endswith('--'):
                                    value = value[:-2]
                                conteudo = value.strip()
                                break
            except Exception as e:
                print(f"[posts_multi] multipart parsing failed: {e}")
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
            # Default: try to parse as text and extract data
            print(f"[posts_multi] Unknown content-type: {content_type}, trying text parsing")
            try:
                body_text = await request.text()
                if hasattr(body_text, 'to_py'):
                    body_text = body_text.to_py()
                if body_text and isinstance(body_text, str):
                    # Try to parse as form-urlencoded
                    from urllib.parse import parse_qs
                    parsed = parse_qs(body_text)
                    conteudo_list = parsed.get('conteudo', [])
                    if conteudo_list:
                        conteudo = conteudo_list[0]
                    # If that fails, check if it's JSON
                    elif body_text.strip().startswith('{'):
                        try:
                            body_json = json.loads(body_text)
                            conteudo = body_json.get('conteudo')
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                print(f"[posts_multi] text parsing failed for unknown content-type: {e}")
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
