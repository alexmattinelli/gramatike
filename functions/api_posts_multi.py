"""
API Posts Multi handler for Cloudflare Workers
Handles multi-image post creation
"""
import json
import traceback
from datetime import datetime
from urllib.parse import parse_qs

try:
    from workers import Response
except ImportError:
    from starlette.responses import Response

from gramatike_d1.auth import get_current_user
from gramatike_d1.db import sanitize_params, safe_get


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
            # Parse multipart/form-data using text() since arrayBuffer() is not available
            try:
                # Use text() which is available in Cloudflare Workers Python
                body_text = await request.text()
                if hasattr(body_text, 'to_py'):
                    body_text = body_text.to_py()
                
                # Extract boundary from content-type header
                boundary = None
                if 'boundary=' in content_type:
                    boundary = content_type.split('boundary=')[1].split(';')[0].strip()
                    if boundary.startswith('"') and boundary.endswith('"'):
                        boundary = boundary[1:-1]
                
                print(f"[posts_multi] Boundary: {boundary}")
                
                if not boundary:
                    print("[posts_multi] No boundary found in content-type")
                    return json_response({'success': False, 'error': 'Erro ao processar formulário: boundary não encontrado'}, 400)
                
                # Split by boundary and find the 'conteudo' field
                parts = body_text.split('--' + boundary)
                print(f"[posts_multi] Found {len(parts)} parts")
                
                for part in parts:
                    # Skip empty parts and closing boundary
                    if not part or part.strip() == '--':
                        continue
                    
                    if 'name="conteudo"' in part or "name='conteudo'" in part:
                        # This is the conteudo field - extract the value
                        if '\r\n\r\n' in part:
                            value = part.split('\r\n\r\n', 1)[1]
                        elif '\n\n' in part:
                            value = part.split('\n\n', 1)[1]
                        else:
                            continue
                        
                        # Clean up trailing characters
                        value = value.rstrip('\r\n')
                        if value.endswith('--'):
                            value = value[:-2]
                        value = value.rstrip('\r\n')
                        
                        conteudo = value.strip()
                        print(f"[posts_multi] Found conteudo: {conteudo[:50]}..." if len(conteudo) > 50 else f"[posts_multi] Found conteudo: {conteudo}")
                        break
                
                if conteudo is None:
                    print("[posts_multi] Could not find 'conteudo' field in multipart data")
                    
            except Exception as e:
                print(f"[posts_multi] multipart parsing failed: {e}")
                print(f"[posts_multi] Traceback: {traceback.format_exc()}")
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
        
        # Create post - include usuario (username) from user table
        # Sanitize all values to prevent D1_TYPE_ERROR from undefined values
        now = datetime.utcnow().isoformat()
        s_usuario_id, s_conteudo, s_now = sanitize_params(usuario_id, conteudo, now)
        
        sql = """
            INSERT INTO post (usuario_id, usuario, conteudo, data)
            SELECT ?, username, ?, ?
            FROM user WHERE id = ?
        """
        await db.prepare(sql).bind(s_usuario_id, s_conteudo, s_now, s_usuario_id).run()
        
        # Get created post ID
        result = await db.prepare('SELECT last_insert_rowid() as id').first()
        post_id = safe_get(result, 'id', 0)
        
        return json_response({'success': True, 'id': post_id, 'imagens': []}, 201)
        
    except Exception as e:
        print(f"[posts_multi] Unexpected error: {e}")
        return json_response({'success': False, 'error': str(e)}, 500)


handler = on_request
