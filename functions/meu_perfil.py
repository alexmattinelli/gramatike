import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.responses import Response, PlainTextResponse

async def on_request(request, env, context):
    db = context.env['DB']
    # Aqui você pode usar autenticação customizada se necessário
    # Exemplo: pega usuário fixo (ajuste para login real)
    user_id = 1  # Troque para pegar do contexto/session
    usuario = await db.prepare("SELECT * FROM user WHERE id=?").bind(user_id).first()
    if not usuario:
        return PlainTextResponse("Usuário não encontrado", status_code=404)
    templates_path = os.path.join(os.path.dirname(__file__), '../gramatike_app/templates')
    env_jinja = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env_jinja.get_template('meu_perfil.html')
    html = template.render(usuario=usuario)
    return Response(html, media_type="text/html")

handler = on_request
