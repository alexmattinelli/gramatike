import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.responses import Response
from datetime import datetime

async def on_request(request, env, context):
    db = context.env['DB']
    templates_path = os.path.join(os.path.dirname(__file__), '../gramatike_app/templates/admin')
    env_jinja = Environment(
        loader=FileSystemLoader(templates_path),
        autoescape=select_autoescape(['html', 'xml'])
    )
    # Busca dados principais do dashboard (simplificado, adapte conforme seu schema)
    usuaries = (await db.prepare("SELECT id, username, email, is_admin FROM user ORDER BY created_at DESC LIMIT 20").all())
    estudos = (await db.prepare("SELECT id, titulo, tipo, created_at FROM edu_content ORDER BY created_at DESC LIMIT 10").all())
    edu_latest = estudos[0] if estudos else None
    topics = (await db.prepare("SELECT id, nome FROM edu_topic ORDER BY id").all())
    sections = (await db.prepare("SELECT id, nome, topic_id FROM exercise_section ORDER BY id").all())
    sections_map = {s['id']: s for s in sections}
    reports = (await db.prepare("SELECT id, motivo, created_at FROM report ORDER BY created_at DESC LIMIT 10").all())
    now = datetime.utcnow()
    current_year = now.year
    edu_topics = topics
    novidades = (await db.prepare("SELECT id, titulo, created_at FROM edu_novidade ORDER BY created_at DESC LIMIT 5").all())
    divulgacoes = (await db.prepare("SELECT id, titulo, created_at FROM divulgacao ORDER BY created_at DESC LIMIT 5").all())
    blocked_words = (await db.prepare("SELECT id, term, category FROM blocked_word ORDER BY id").all())
    users_pagination = usuaries  # Simplificado
    reports_pagination = reports
    blocked_words_pagination = blocked_words
    template = env_jinja.get_template('dashboard.html')
    html = template.render(
        usuaries=usuaries,
        estudos=estudos,
        edu_latest=edu_latest,
        topics=topics,
        sections=sections,
        sections_map=sections_map,
        reports=reports,
        now=now,
        current_year=current_year,
        edu_topics=edu_topics,
        novidades=novidades,
        divulgacoes=divulgacoes,
        blocked_words=blocked_words,
        users_pagination=users_pagination,
        reports_pagination=reports_pagination,
        blocked_words_pagination=blocked_words_pagination
    )
    return Response(html, media_type="text/html")

handler = on_request
