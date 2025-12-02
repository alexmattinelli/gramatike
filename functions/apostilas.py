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
    apostilas = []
    try:
        sql = "SELECT id, titulo, resumo, created_at FROM edu_content WHERE tipo='apostila' ORDER BY created_at DESC LIMIT 20"
        result = await db.prepare(sql).all()
        apostilas = result
    except Exception as e:
        apostilas = []
    template = env_jinja.get_template('apostilas.html')
    html = template.render(title='Apostilas', apostilas=apostilas)
    return Response(html, media_type="text/html")

handler = on_request
