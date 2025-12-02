import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.responses import Response, PlainTextResponse

async def on_request(request, env, context):
    db = context.env['DB']
    # Extrai o username da URL: /perfil/<username>
    try:
        username = request.url.path.split('/')[-1]
    except Exception:
        return PlainTextResponse("Usuário inválido", status_code=400)
    templates_path = os.path.join(os.path.dirname(__file__), '../gramatike_app/templates')
    env_jinja = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(['html', 'xml'])
    )
    usuario = await db.prepare("SELECT * FROM user WHERE username=?").bind(username).first()
    if not usuario:
        return PlainTextResponse("Usuário não encontrado", status_code=404)
    template = env_jinja.get_template('perfil.html')
    html = template.render(usuario=usuario)
    return Response(html, media_type="text/html")

handler = on_request
