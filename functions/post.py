import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.responses import Response, PlainTextResponse

async def on_request(request, env, context):
    db = context.env['DB']
    templates_path = os.path.join(os.path.dirname(__file__), '../gramatike_app/templates')
    env_jinja = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(['html', 'xml'])
    )
    # Extrai o id do post da URL
    try:
        post_id = int(request.url.path.split('/')[-1])
    except Exception:
        return PlainTextResponse("ID de post inválido", status_code=400)
    post = None
    try:
        sql = "SELECT id, titulo, conteudo, created_at FROM post WHERE id=?"
        result = await db.prepare(sql).bind(post_id).first()
        post = result
    except Exception as e:
        post = None
    if not post:
        return PlainTextResponse("Post não encontrado", status_code=404)
    template = env_jinja.get_template('post_detail.html')
    html = template.render(title=post['titulo'], post=post)
    return Response(html, media_type="text/html")

handler = on_request
