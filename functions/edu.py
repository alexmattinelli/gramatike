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
    edu_items = []
    try:
        sql = "SELECT id, titulo, resumo, tipo, created_at FROM edu_content ORDER BY created_at DESC LIMIT 20"
        result = await db.prepare(sql).all()
        edu_items = result
    except Exception as e:
        edu_items = []
    template = env_jinja.get_template('gramatike_edu.html')
    html = template.render(title='Gramátike Edu', edu_items=edu_items)
    return Response(html, media_type="text/html")

handler = on_request
