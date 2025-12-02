import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.responses import Response

def on_request(request, env, db):
    # Exemplo: renderiza a home
    template = env.get_template('index.html')
    html = template.render(title='Gramátike', usuario=None)
    return Response(html, media_type="text/html")

# Cloudflare Pages Functions handler
async def on_request_cf(request, env, context):
    # Binding DB: context.env['DB']
    # Setup Jinja2
    templates_path = os.path.join(os.path.dirname(__file__), '../gramatike_app/templates')
    env_jinja = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(['html', 'xml'])
    )
    # Exemplo: home
    return on_request(request, env_jinja, context.env['DB'])

def main(request, env, context):
    return on_request_cf(request, env, context)

handler = main
