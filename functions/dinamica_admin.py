import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.responses import Response

async def on_request(request, env, context):
    templates_path = os.path.join(os.path.dirname(__file__), '../gramatike_app/templates')
    env_jinja = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env_jinja.get_template('dinamica_admin.html')
    html = template.render(title='Dinâmica Admin')
    return Response(html, media_type="text/html")

handler = on_request
