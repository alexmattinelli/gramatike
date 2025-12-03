import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.responses import Response

def on_request(request, env, db):
    # Exemplo: renderiza a página de login
    template = env.get_template('login.html')
    html = template.render(title='Entrar', erro=None)
    return Response(html, media_type="text/html")

async def on_request_cf(request, env, context):
    templates_path = os.path.join(os.path.dirname(__file__), '../gramatike_app/templates')
    env_jinja = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(['html', 'xml'])
    )
    return on_request(request, env_jinja, context.env['DB'])

def main(request, env, context):
    return on_request_cf(request, env, context)

handler = main
