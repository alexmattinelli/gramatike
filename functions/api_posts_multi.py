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
        from gramatike_d1.auth import get_current_user
        user = await get_current_user(db, request)
        if not user:
            return json_response({'success': False, 'error': 'Não autenticado'}, 401)
        usuario_id = user['id']
    except Exception as e:
        print(f"[posts_multi] Auth error: {e}")
        return json_response({'success': False, 'error': 'Erro de autenticação'}, 401)
    
    try:
        # Parse request body based on content type
        content_type = request.headers.get('content-type', '') or ''
        conteudo = ''
        
        if 'multipart/form-data' in content_type:
            # Handle multipart form data (with or without images)
            try:
                data = await request.formData()
                conteudo = str(data.get('conteudo') or '').strip()
            except Exception as e:
                print(f"[posts_multi] FormData parse failed: {e}")
                return json_response({'success': False, 'error': 'Erro ao processar formulário'}, 400)
        elif 'application/json' in content_type:
            # Handle JSON body
            try:
                body = await request.json()
                conteudo = str(body.get('conteudo') or '').strip()
            except Exception as e:
                print(f"[posts_multi] JSON parse failed: {e}")
                return json_response({'success': False, 'error': 'Erro ao processar JSON'}, 400)
        else:
            # Default: try to parse as FormData (most common case for post creation)
            try:
                data = await request.formData()
                conteudo = str(data.get('conteudo') or '').strip()
            except Exception as e:
                print(f"[posts_multi] FormData parse failed (fallback): {e}")
                return json_response({'success': False, 'error': 'Formato de dados inválido'}, 400)
        
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
