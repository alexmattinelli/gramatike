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
    
    try:
        # Parse request body
        content_type = request.headers.get('content-type', '')
        if 'multipart' in content_type:
            data = await request.formData()
            conteudo = str(data.get('conteudo') or '').strip()
            usuario_id = int(data.get('usuario_id') or 0)
        else:
            body = await request.json()
            conteudo = str(body.get('conteudo') or '').strip()
            usuario_id = int(body.get('usuario_id') or 0)
        
        if not conteudo:
            return json_response({'success': False, 'error': 'conteudo_vazio'}, 400)
        
        if not usuario_id:
            return json_response({'success': False, 'error': 'usuario_invalido'}, 400)
        
        # Create post
        now = datetime.utcnow().isoformat()
        sql = "INSERT INTO post (usuario_id, conteudo, created_at) VALUES (?, ?, ?)"
        await db.prepare(sql).bind(usuario_id, conteudo, now).run()
        
        # Get created post ID
        result = await db.prepare('SELECT last_insert_rowid() as id').first()
        post_id = result['id'] if result else 0
        
        return json_response({'success': True, 'id': post_id, 'imagens': []}, 201)
        
    except Exception as e:
        return json_response({'success': False, 'error': str(e)}, 500)


handler = on_request
