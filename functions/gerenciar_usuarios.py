import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.responses import Response

async def on_request(request, env, context):
    templates_path = os.path.join(os.path.dirname(__file__), '../gramatike_app/templates')
    env_jinja = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env_jinja.get_template('gerenciar_usuarios.html')
    html = template.render(title='Gerenciar Usuários')
    return Response(html, media_type="text/html")

handler = on_request
