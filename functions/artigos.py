import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.responses import Response

async def on_request(request, env, context):
    db = context.env['DB']
    templates_path = os.path.join(os.path.dirname(__file__), '../gramatike_app/templates')
    env_jinja = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(['html', 'xml'])
    )
    # Exemplo de query D1 (ajuste conforme seu schema)
    artigos = []
    try:
        sql = "SELECT id, titulo, resumo, created_at FROM edu_content WHERE tipo='artigo' ORDER BY created_at DESC LIMIT 20"
        result = await db.prepare(sql).all()
        artigos = result
    except Exception as e:
        artigos = []
    template = env_jinja.get_template('artigos.html')
    html = template.render(title='Artigos', artigos=artigos)
    return Response(html, media_type="text/html")

handler = on_request
