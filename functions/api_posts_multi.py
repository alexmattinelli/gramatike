import os
from starlette.responses import JSONResponse
from datetime import datetime

async def on_request(request, env, context):
    db = context.env['DB']
    # Aceita apenas POST
    if request.method != 'POST':
        return JSONResponse({'error': 'Método não permitido'}, status_code=405)
    # Lê dados do corpo (form-data ou JSON)
    data = await request.form() if request.headers.get('content-type','').startswith('multipart') else await request.json()
    conteudo = (data.get('conteudo') or '').strip()
    if not conteudo:
        return JSONResponse({'success': False, 'error': 'conteudo_vazio'}, status_code=400)
    # TODO: Moderação de texto (implemente se necessário)
    # TODO: Upload de imagens (integre com R2 se necessário)
    usuario = data.get('usuario') or 'anon'
    usuario_id = int(data.get('usuario_id') or 1)
    imagens = data.get('imagens') or ''
    now = datetime.utcnow().isoformat()
    sql = "INSERT INTO post (usuario, usuario_id, conteudo, imagem, data) VALUES (?, ?, ?, ?, ?)"
    await db.prepare(sql).bind(usuario, usuario_id, conteudo, imagens, now).run()
    # Recupera o ID do post criado
    post_id = (await db.prepare('SELECT last_insert_rowid() as id').first())['id']
    return JSONResponse({'success': True, 'id': post_id, 'imagens': imagens}, status_code=201)

handler = on_request
