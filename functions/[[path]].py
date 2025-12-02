# Handler universal para rotas dinâmicas (fallback)
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.responses import Response, PlainTextResponse

def not_found():
    return PlainTextResponse("Página não encontrada", status_code=404)

def on_request(request, env, db):
    # Aqui você pode mapear rotas dinâmicas
    path = request.url.path
    if path == "/artigos":
        template = env.get_template('artigos.html')
        html = template.render(title='Artigos')
        return Response(html, media_type="text/html")
    if path == "/apostilas":
        template = env.get_template('apostilas.html')
        html = template.render(title='Apostilas')
        return Response(html, media_type="text/html")
    # ...adicione mais rotas conforme necessário...
    return not_found()

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
    
    # Convert Flask response to Cloudflare response
    headers = dict(response.headers)
    
    return WerkzeugResponse(
        response.get_data(),
        status=response.status_code,
        headers=headers
    )
