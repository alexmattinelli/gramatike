from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from gramatike_app.models import User, Estudo, EduContent, ExerciseTopic, ExerciseQuestion, EduTopic, ExerciseSection, Divulgacao
from gramatike_app.models import EduNovidade
from gramatike_app.models import Post, Report, Comentario
from gramatike_app.models import BlockedWord
from gramatike_app import db
# Lune admin/config removido
from gramatike_app.utils.moderation import refresh_custom_terms_cache
from gramatike_app.utils.storage import upload_bytes_to_supabase, build_apostila_path
from mimetypes import guess_type
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Exemplo de rota
@admin_bp.route('/')
@login_required
def dashboard():
    if not getattr(current_user, "is_admin", False):
        return "Acesso restrito", 403
    # Fallback automático para evitar erro se migração ainda não aplicada (SQLite)
    try:
        engine = db.get_engine()
        if engine.name == 'sqlite':
            with engine.connect() as conn:
                cols = conn.exec_driver_sql("PRAGMA table_info(edu_content)").fetchall()
                colnames = {c[1] for c in cols}
                if 'topic_id' not in colnames:
                    conn.exec_driver_sql("ALTER TABLE edu_content ADD COLUMN topic_id INTEGER")
                tbl = conn.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table' AND name='edu_topic'").fetchone()
                if not tbl:
                    conn.exec_driver_sql("""
                        CREATE TABLE edu_topic (
                            id INTEGER PRIMARY KEY,
                            area VARCHAR(40) NOT NULL,
                            nome VARCHAR(150) NOT NULL,
                            descricao TEXT,
                            created_at DATETIME,
                            CONSTRAINT uix_area_nome UNIQUE (area, nome)
                        )
                    """)
                    conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_edu_topic_area ON edu_topic(area)")
                    conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_edu_topic_created_at ON edu_topic(created_at)")
                # Fallbacks de moderação e denúncias
                # Tabela report: coluna category
                try:
                    rcols = conn.exec_driver_sql("PRAGMA table_info(report)").fetchall()
                    rnames = {c[1] for c in rcols}
                    if 'category' not in rnames:
                        conn.exec_driver_sql("ALTER TABLE report ADD COLUMN category VARCHAR(40)")
                except Exception as _er:
                    print('[WARN] fallback schema report.category:', _er)
                # Tabela user: colunas de moderação
                try:
                    ucols = conn.exec_driver_sql("PRAGMA table_info(user)").fetchall()
                    unames = {c[1] for c in ucols}
                    if 'is_banned' not in unames:
                        conn.exec_driver_sql("ALTER TABLE user ADD COLUMN is_banned BOOLEAN DEFAULT 0")
                    if 'banned_at' not in unames:
                        conn.exec_driver_sql("ALTER TABLE user ADD COLUMN banned_at DATETIME")
                    if 'ban_reason' not in unames:
                        conn.exec_driver_sql("ALTER TABLE user ADD COLUMN ban_reason TEXT")
                    if 'suspended_until' not in unames:
                        conn.exec_driver_sql("ALTER TABLE user ADD COLUMN suspended_until DATETIME")
                except Exception as _eu:
                    print('[WARN] fallback schema user moderation cols:', _eu)
                # Tabela blocked_word
                try:
                    tbl = conn.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table' AND name='blocked_word'").fetchone()
                    if not tbl:
                        conn.exec_driver_sql(
                            """
                            CREATE TABLE blocked_word (
                                id INTEGER PRIMARY KEY,
                                term VARCHAR(200) NOT NULL UNIQUE,
                                category VARCHAR(20),
                                created_at DATETIME,
                                created_by INTEGER
                            )
                            """
                        )
                        conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_blocked_word_category ON blocked_word(category)")
                        conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_blocked_word_created_at ON blocked_word(created_at)")
                except Exception as _bw:
                    print('[WARN] fallback schema blocked_word:', _bw)
    except Exception as _e:
        print('[WARN] fallback schema edu_content/topic_id:', _e)
    
    # Pagination for users
    users_page = request.args.get('users_page', 1, type=int)
    users_per_page = 10
    users_pagination = User.query.paginate(page=users_page, per_page=users_per_page, error_out=False)
    usuaries = users_pagination.items
    
    estudos = Estudo.query.order_by(Estudo.id.desc()).all()
    edu_latest = EduContent.query.order_by(EduContent.created_at.desc()).limit(12).all()
    edu_topics = EduTopic.query.order_by(EduTopic.area.asc(), EduTopic.nome.asc()).all()
    topics = ExerciseTopic.query.order_by(ExerciseTopic.nome.asc()).all()
    sections = ExerciseSection.query.order_by(ExerciseSection.topic_id.asc(), ExerciseSection.ordem.asc(), ExerciseSection.nome.asc()).all()
    # Mapa simples topic_id -> [{id,nome}]
    sections_map = {}
    for s in sections:
        sections_map.setdefault(s.topic_id, []).append({'id': s.id, 'nome': s.nome})
    from datetime import datetime
    
    # Pagination for reports
    reports_page = request.args.get('reports_page', 1, type=int)
    reports_per_page = 10
    reports_pagination = Report.query.order_by(Report.data.desc()).paginate(page=reports_page, per_page=reports_per_page, error_out=False)
    reports = reports_pagination.items
    
    now = datetime.utcnow()
    # Divulgações (cards de destaque curados manualmente)
    divulgacoes = Divulgacao.query.order_by(Divulgacao.area.asc(), Divulgacao.ordem.asc(), Divulgacao.created_at.desc()).all()
    novidades = EduNovidade.query.order_by(EduNovidade.created_at.desc()).limit(30).all()
    
    # Paginação para palavras bloqueadas
    moderation_page = request.args.get('moderation_page', 1, type=int)
    moderation_per_page = 10
    blocked_words_pagination = BlockedWord.query.order_by(BlockedWord.created_at.desc()).paginate(page=moderation_page, per_page=moderation_per_page, error_out=False)
    blocked_words = blocked_words_pagination.items
    
    return render_template('admin/dashboard.html', usuaries=usuaries, estudos=estudos, edu_latest=edu_latest, topics=topics, sections=sections, sections_map=sections_map, reports=reports, now=now, current_year=datetime.now().year, edu_topics=edu_topics, novidades=novidades, divulgacoes=divulgacoes, blocked_words=blocked_words, users_pagination=users_pagination, reports_pagination=reports_pagination, blocked_words_pagination=blocked_words_pagination)

@admin_bp.route('/moderation/blocked_words/add', methods=['POST'])
@login_required
def add_blocked_word():
    if not getattr(current_user, 'is_admin', False):
        return redirect(url_for('main.index'))
    term = (request.form.get('term') or '').strip()
    category = (request.form.get('category') or 'custom').strip().lower()
    if not term:
        flash('Informe um termo para bloquear.')
        return redirect(url_for('admin.dashboard', _anchor='geral'))
    # Evita duplicados (case-insensitive)
    exists = BlockedWord.query.filter(db.func.lower(BlockedWord.term) == term.lower()).first()
    if exists:
        flash('Termo já existe na lista.')
        return redirect(url_for('admin.dashboard', _anchor='geral'))
    bw = BlockedWord(term=term, category=category if category in ('profanity','hate','nudity','custom') else 'custom', created_by=current_user.id)
    db.session.add(bw)
    db.session.commit()
    refresh_custom_terms_cache()
    flash('Termo adicionado à lista de bloqueio.')
    return redirect(url_for('admin.dashboard', _anchor='geral'))

@admin_bp.route('/moderation/blocked_words/<int:bid>/delete', methods=['POST'])
@login_required
def delete_blocked_word(bid: int):
    if not getattr(current_user, 'is_admin', False):
        return redirect(url_for('main.index'))
    bw = BlockedWord.query.get_or_404(bid)
    db.session.delete(bw)
    db.session.commit()
    refresh_custom_terms_cache()
    flash('Termo removido da lista de bloqueio.')
    return redirect(url_for('admin.dashboard', _anchor='geral'))

@admin_bp.route('/stats/users.json')
@login_required
def stats_users():
    if not current_user.is_admin:
        return {"error":"forbidden"}, 403
    from sqlalchemy import func
    # Agrupar por dia e calcular crescimento acumulado
    # Filtra registros com created_at NULL para evitar problemas no agrupamento
    rows = db.session.query(func.date(User.created_at), func.count(User.id)).filter(User.created_at.isnot(None)).group_by(func.date(User.created_at)).order_by(func.date(User.created_at)).all()
    
    # Calculate cumulative growth
    cumulative = []
    total = 0
    for r in rows:
        total += r[1]
        cumulative.append(total)
    
    return {"labels":[str(r[0]) for r in rows], "data":cumulative}

@admin_bp.route('/stats/content.json')
@login_required
def stats_content():
    if not current_user.is_admin:
        return {"error":"forbidden"}, 403
    from sqlalchemy import func
    from gramatike_app.models import EduContent
    # Agrupar conteúdo Edu por tipo
    rows = db.session.query(EduContent.tipo, func.count(EduContent.id)).group_by(EduContent.tipo).all()
    return {"labels":[r[0].capitalize() for r in rows], "data":[r[1] for r in rows]}

@admin_bp.route('/stats/posts.json')
@login_required
def stats_posts():
    if not current_user.is_admin:
        return {"error":"forbidden"}, 403
    from sqlalchemy import func
    from gramatike_app.models import Post
    from datetime import datetime, timedelta
    # Posts dos últimos 7 dias
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    rows = db.session.query(func.date(Post.data), func.count(Post.id)).filter(Post.data >= seven_days_ago).group_by(func.date(Post.data)).order_by(func.date(Post.data)).all()
    return {"labels":[str(r[0]) for r in rows], "data":[r[1] for r in rows]}

@admin_bp.route('/stats/activity.json')
@login_required
def stats_activity():
    if not current_user.is_admin:
        return {"error":"forbidden"}, 403
    from sqlalchemy import func
    from gramatike_app.models import Post, EduContent, Comentario
    # Contagem de diferentes tipos de atividade
    post_count = db.session.query(func.count(Post.id)).scalar() or 0
    edu_count = db.session.query(func.count(EduContent.id)).scalar() or 0
    comment_count = db.session.query(func.count(Comentario.id)).scalar() or 0
    user_count = db.session.query(func.count(User.id)).scalar() or 0
    
    return {
        "labels": ["Posts", "Conteúdo Edu", "Comentários", "Usuáries"],
        "data": [post_count, edu_count, comment_count, user_count]
    }

@admin_bp.route('/postar_estudo', methods=['POST'])
@login_required
def postar_estudo():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    titulo = request.form['titulo']
    conteudo = request.form['conteudo']
    estudo = Estudo(titulo=titulo, conteudo=conteudo)
    db.session.add(estudo)
    db.session.commit()
    flash('Conteúdo postado com sucesso!')
    return redirect(url_for('admin.dashboard'))

# Rotas de Promoção removidas — conceito unificado em Divulgação

# === Novidades Gramátike ===
@admin_bp.route('/novidades/create', methods=['POST'])
@login_required
def novidades_create():
    if not getattr(current_user, 'is_admin', False):
        return redirect(url_for('main.index'))
    titulo = (request.form.get('titulo') or '').strip()
    descricao = (request.form.get('descricao') or '').strip() or None
    link = (request.form.get('link') or '').strip() or None
    if not titulo:
        flash('Título é obrigatório para novidade.')
        return redirect(url_for('admin.dashboard', _anchor='gramatike'))
    n = EduNovidade(titulo=titulo, descricao=descricao, link=link, author_id=current_user.id)
    db.session.add(n)
    db.session.commit()
    flash('Novidade adicionada.')
    return redirect(url_for('admin.dashboard', _anchor='gramatike'))

@admin_bp.route('/novidades/<int:nid>/edit', methods=['POST'])
@login_required
def novidades_edit(nid):
    if not getattr(current_user, 'is_admin', False):
        return redirect(url_for('main.index'))
    n = EduNovidade.query.get_or_404(nid)
    n.titulo = (request.form.get('titulo') or '').strip()
    n.descricao = (request.form.get('descricao') or '').strip() or None
    n.link = (request.form.get('link') or '').strip() or None
    if not n.titulo:
        flash('Título é obrigatório para novidade.')
        return redirect(url_for('main.novidade_detail', novidade_id=nid))
    db.session.commit()
    flash('Novidade atualizada.')
    return redirect(url_for('main.novidade_detail', novidade_id=nid))

@admin_bp.route('/novidades/<int:nid>/delete', methods=['POST'])
@login_required
def novidades_delete(nid):
    if not getattr(current_user, 'is_admin', False):
        return redirect(url_for('main.index'))
    n = EduNovidade.query.get_or_404(nid)
    db.session.delete(n)
    db.session.commit()
    flash('Novidade removida.')
    return redirect(url_for('admin.dashboard', _anchor='gramatike'))

# --- Novas rotas EDU ---
@admin_bp.route('/edu/publicar', methods=['POST'])
@login_required
def edu_publicar():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    tipo = request.form.get('tipo')
    titulo = request.form.get('titulo', '').strip()
    resumo = request.form.get('resumo', '').strip() or None
    corpo = request.form.get('corpo', '').strip() or None
    url_field = request.form.get('url', '').strip() or None
    file_path = None
    extra = None
    extra_dict = {}
    # Autor/Canal opcional (guardado em extra.author)
    autor = request.form.get('autor', '').strip() or None
    
    # Validação de limite de palavras para artigos (5000 palavras)
    if tipo == 'artigo' and corpo:
        word_count = len(corpo.split())
        if word_count > 5000:
            flash(f'O artigo excede o limite de 5000 palavras (atual: {word_count} palavras). Por favor, reduza o conteúdo.')
            return redirect(url_for('admin.dashboard', _anchor='edu'))
    
    # Upload de apostila (PDF ou URL)
    if tipo == 'apostila':
        pdf_file = request.files.get('pdf')
        # Se forneceu URL, usa a URL
        if url_field:
            file_path = url_field
        elif pdf_file and pdf_file.filename.lower().endswith('.pdf'):
            import uuid
            fname = f"{uuid.uuid4().hex}.pdf"
            
            # Tenta upload para Supabase primeiro
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)
            ctype, _ = guess_type(fname)
            remote_path = build_apostila_path(fname)
            public_url = upload_bytes_to_supabase(remote_path, pdf_bytes, content_type=ctype or 'application/pdf')
            
            if public_url:
                # Sucesso no Supabase - usa URL pública
                file_path = public_url
                # Nota: thumbnail generation para PDFs no Supabase requer processamento adicional
                # Por ora, não geramos thumbnail quando usando Supabase
            else:
                # Fallback: salvar localmente (pode não funcionar em serverless)
                upload_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads', 'apostilas')
                upload_dir = os.path.normpath(upload_dir)
                os.makedirs(upload_dir, exist_ok=True)
                save_path = os.path.join(upload_dir, fname)
                pdf_file.save(save_path)
                # Caminho público relativo
                file_path = f"uploads/apostilas/{fname}"
                # Tenta gerar miniatura (primeira página) usando PyMuPDF
                try:
                    import fitz  # PyMuPDF
                    doc = fitz.open(save_path)
                    if doc.page_count > 0:
                        page = doc.load_page(0)
                        # Zoom visando largura ~280px (ajuste fino)
                        zoom = 0.4
                        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
                        th_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads', 'apostilas', 'thumbs')
                        th_dir = os.path.normpath(th_dir)
                        os.makedirs(th_dir, exist_ok=True)
                        th_name = f"{os.path.splitext(fname)[0]}.png"
                        th_path = os.path.join(th_dir, th_name)
                        pix.save(th_path)
                        extra_dict['thumb'] = f"uploads/apostilas/thumbs/{th_name}"
                    doc.close()
                except Exception as _e:
                    # Se falhar, segue sem thumb
                    print('[WARN] PDF thumbnail generation failed:', _e)
        else:
            flash('É necessário enviar um arquivo PDF ou um link (URL) para apostila.')
            return redirect(url_for('admin.dashboard', _anchor='edu'))
    # Metadados/embeds para mídias
    if tipo == 'podcast':
        import re, json
        if url_field:
            # Se veio o iframe inteiro, extrai o src
            m_iframe = re.search(r'src="https?://open\.spotify\.com/embed/(episode|show)/([A-Za-z0-9]+)[^"]*"', url_field, re.I)
            # Aceita paths com locale (ex.: /intl-pt/episode/..)
            m_link = re.search(r'spotify\.com/(?:[^/]+/)?(episode|show)/([A-Za-z0-9]+)', url_field, re.I)
            m = m_iframe or m_link
            if m:
                kind, sid = m.group(1), m.group(2)
                # Usa formato oficial com utm_source=generator
                embed_url = f"https://open.spotify.com/embed/{kind}/{sid}?utm_source=generator"
                extra_dict["spotify_embed"] = embed_url
            # Se link direto mp3, deixar em url mesmo (player HTML5 usará c.url)
    if tipo == 'video':
        import re, json, os, uuid
        if url_field:
            yt = re.search(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([A-Za-z0-9_-]{6,})', url_field)
            vimeo = re.search(r'vimeo\.com/(?:video/)?(\d+)', url_field)
            tiktok = re.search(r'tiktok\.com/@[\w\.-]+/video/(\d+)', url_field)
            if yt:
                vid = yt.group(1)
                extra_dict["video_embed"] = f"https://www.youtube.com/embed/{vid}"
            elif vimeo:
                vid = vimeo.group(1)
                extra_dict["video_embed"] = f"https://player.vimeo.com/video/{vid}"
            elif tiktok:
                # Para TikTok, usar embed nativo via blockquote + script; armazenar a URL original
                extra_dict["tiktok_url"] = url_field
        # Upload de thumbnail opcional
        thumb_file = request.files.get('thumb')
        if thumb_file and getattr(thumb_file, 'filename', ''):
            fn = thumb_file.filename.lower()
            if any(fn.endswith(ext) for ext in ['.png','.jpg','.jpeg','.webp','.gif']):
                upload_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads', 'videos', 'thumbs')
                upload_dir = os.path.normpath(upload_dir)
                os.makedirs(upload_dir, exist_ok=True)
                save_name = f"{uuid.uuid4().hex}{os.path.splitext(fn)[1]}"
                save_path = os.path.join(upload_dir, save_name)
                thumb_file.save(save_path)
                extra_dict['thumb'] = f"uploads/videos/thumbs/{save_name}"
    if not (tipo and titulo):
        flash('Tipo e título obrigatórios.')
        return redirect(url_for('admin.dashboard', _anchor='edu'))
    topic_id = request.form.get('topic_id') or None
    # Serializa extra_dict se tiver conteúdo
    if autor:
        extra_dict['author'] = autor
    if extra_dict:
        import json as _json
        extra = _json.dumps(extra_dict)
    try:
        content = EduContent(tipo=tipo, titulo=titulo, resumo=resumo, corpo=corpo, url=url_field, file_path=file_path, extra=extra, author_id=current_user.id, topic_id=topic_id)
        db.session.add(content)
        db.session.commit()
        flash('Conteúdo publicado!')
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        # Mensagens de erro mais detalhadas
        if 'too long' in error_msg.lower() or 'data too long' in error_msg.lower():
            flash(f'Erro: Campo muito longo. Verifique os limites: Resumo (1000 caracteres), Título (220 caracteres). Detalhes: {error_msg}')
        elif 'resumo' in error_msg.lower():
            flash(f'Erro no campo Resumo: {error_msg}. Limite: 1000 caracteres.')
        elif 'titulo' in error_msg.lower():
            flash(f'Erro no campo Título: {error_msg}. Limite: 220 caracteres.')
        else:
            flash(f'Erro ao publicar conteúdo: {error_msg}')
    return redirect(url_for('admin.dashboard', _anchor='edu'))

@admin_bp.route('/promover_admin', methods=['POST'])
@login_required
def promover_admin():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    ident = request.form.get('ident','').strip()
    if not ident:
        flash('Informe username ou email.')
        return redirect(url_for('admin.dashboard', _anchor='geral'))
    # Buscar por username primeiro, depois email
    user = User.query.filter_by(username=ident).first()
    if not user:
        user = User.query.filter_by(email=ident).first()
    if not user:
        flash('Usuárie não encontrade.')
        return redirect(url_for('admin.dashboard', _anchor='geral'))
    if getattr(user, 'is_superadmin', False):
        flash('Superadmin já possui privilégios máximos.')
        return redirect(url_for('admin.dashboard', _anchor='geral'))
    if user.is_admin:
        flash('Essa pessoa já é admin.')
        return redirect(url_for('admin.dashboard', _anchor='geral'))
    user.is_admin = True
    db.session.commit()
    flash(f"{user.username} agora é admin.")
    return redirect(url_for('admin.dashboard', _anchor='geral'))

@admin_bp.route('/edu/topic', methods=['POST'])
@login_required
def edu_create_topic():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    nome = request.form.get('nome','').strip()
    descricao = request.form.get('descricao','').strip() or None
    if not nome:
        flash('Nome do tópico obrigatório.')
        return redirect(url_for('admin.dashboard', _anchor='edu'))
    if ExerciseTopic.query.filter_by(nome=nome).first():
        flash('Tópico já existe.')
        return redirect(url_for('admin.dashboard', _anchor='edu'))
    t = ExerciseTopic(nome=nome, descricao=descricao)
    db.session.add(t)
    db.session.commit()
    flash('Tópico criado.')
    return redirect(url_for('admin.dashboard', _anchor='edu'))

@admin_bp.route('/edu/topico', methods=['POST'])
@login_required
def edu_topic_create():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    area = request.form.get('area','').strip()
    nome = request.form.get('nome','').strip()
    descricao = request.form.get('descricao','').strip() or None
    if not (area and nome):
        flash('Área e nome são obrigatórios.')
        return redirect(url_for('admin.dashboard', _anchor='edu'))
    if EduTopic.query.filter_by(area=area, nome=nome).first():
        flash('Já existe tópico com esse nome nessa área.')
        return redirect(url_for('admin.dashboard', _anchor='edu'))
    t = EduTopic(area=area, nome=nome, descricao=descricao)
    db.session.add(t)
    db.session.commit()
    flash('Tópico criado.')
    return redirect(url_for('admin.dashboard', _anchor='edu'))

@admin_bp.route('/edu/topico/<int:topic_id>', methods=['POST'])
@login_required
def edu_topic_update(topic_id):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    topic = EduTopic.query.get_or_404(topic_id)
    nome = request.form.get('nome','').strip()
    descricao = request.form.get('descricao','').strip() or None
    if not nome:
        flash('Nome do tópico é obrigatório.')
        return redirect(url_for('admin.dashboard', _anchor='edu'))
    # Check if another topic with same name exists in same area
    existing = EduTopic.query.filter_by(area=topic.area, nome=nome).first()
    if existing and existing.id != topic_id:
        flash('Já existe tópico com esse nome nessa área.')
        return redirect(url_for('admin.dashboard', _anchor='edu'))
    topic.nome = nome
    topic.descricao = descricao
    db.session.commit()
    flash('Tópico atualizado com sucesso.')
    return redirect(url_for('admin.dashboard', _anchor='edu'))

@admin_bp.route('/edu/buscar')
@login_required
def edu_buscar():
    if not current_user.is_admin:
        return {"error":"forbidden"}, 403
    area = request.args.get('area')
    q = request.args.get('q','').strip()
    query = EduContent.query
    if area:
        # map area to tipo(s)
        area_map = {
            'artigos': ['artigo'],
            'apostilas': ['apostila'],
            'exercicios': ['exercicio'],
            'podcasts': ['podcast'],
            'redacao': ['redacao_tema'],
            'videos': ['video']
        }
        tipos = area_map.get(area.lower())
        if tipos:
            query = query.filter(EduContent.tipo.in_(tipos))
    if q:
        from sqlalchemy import or_
        like = f"%{q}%"
        query = query.filter(or_(EduContent.titulo.ilike(like), EduContent.resumo.ilike(like)))
    rows = query.order_by(EduContent.created_at.desc()).limit(100).all()
    return {"results":[{"id":c.id,"titulo":c.titulo,"tipo":c.tipo,"resumo":c.resumo,"topic": c.topic.nome if c.topic else None} for c in rows]}

@admin_bp.route('/edu/content/<int:content_id>.json')
@login_required
def get_edu_content(content_id: int):
    if not current_user.is_admin:
        return {"error":"forbidden"}, 403
    c = EduContent.query.get_or_404(content_id)
    def _parse_extra(text):
        try:
            import json
            return json.loads(text) if text else None
        except Exception:
            return None
    ex = _parse_extra(c.extra)
    return {
        "id": c.id,
        "tipo": c.tipo,
        "titulo": c.titulo,
        "resumo": c.resumo,
        "url": c.url,
        "topic_id": c.topic_id,
        "extra": ex
    }

@admin_bp.route('/edu/content/<int:content_id>/update', methods=['POST'])
@login_required
def update_edu_content(content_id: int):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    c = EduContent.query.get_or_404(content_id)
    titulo = request.form.get('titulo','').strip() or c.titulo
    resumo = request.form.get('resumo','').strip() or None
    url_field = request.form.get('url','').strip() or None
    topic_id = request.form.get('topic_id') or None
    c.titulo = titulo
    c.resumo = resumo
    c.url = url_field
    c.topic_id = int(topic_id) if topic_id else None
    # Atualiza extras conforme tipo
    import json, re, os, uuid
    def _parse_extra(text):
        try:
            return json.loads(text) if text else {}
        except Exception:
            return {}
    extra = _parse_extra(c.extra)
    # Atualiza autor/canal se enviado
    autor = request.form.get('autor','').strip()
    if autor:
        extra['author'] = autor
    else:
        extra.pop('author', None)
    if c.tipo == 'podcast' and url_field:
        m_iframe = re.search(r'src=\"https?://open\.spotify\.com/embed/(episode|show)/([A-Za-z0-9]+)[^\"]*\"', url_field, re.I)
        m_link = re.search(r'spotify\.com/(?:[^/]+/)?(episode|show)/([A-Za-z0-9]+)', url_field, re.I)
        m = m_iframe or m_link
        if m:
            kind, sid = m.group(1), m.group(2)
            embed_url = f"https://open.spotify.com/embed/{kind}/{sid}?utm_source=generator"
            extra['spotify_embed'] = embed_url
    if c.tipo == 'video':
        # Detectar embeds
        if url_field:
            yt = re.search(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|shorts/))([A-Za-z0-9_-]{6,})', url_field)
            vimeo = re.search(r'vimeo\.com/(?:video/)?(\d+)', url_field)
            tiktok = re.search(r'tiktok\.com/@[\w\.-]+/video/(\d+)', url_field)
            if yt:
                extra['video_embed'] = f"https://www.youtube.com/embed/{yt.group(1)}"
                extra.pop('tiktok_url', None)
            elif vimeo:
                extra['video_embed'] = f"https://player.vimeo.com/video/{vimeo.group(1)}"
                extra.pop('tiktok_url', None)
            elif tiktok:
                extra['tiktok_url'] = url_field
                extra.pop('video_embed', None)
        # Thumb: remover se pedido
        if request.form.get('remove_thumb') == '1':
            # apagar arquivo local se existir e for local
            old = extra.get('thumb')
            if old and not str(old).startswith('http'):
                try:
                    path = os.path.join(os.path.dirname(__file__), '..', 'static', old)
                    path = os.path.normpath(path)
                    if os.path.exists(path):
                        os.remove(path)
                except Exception:
                    pass
            extra.pop('thumb', None)
        # Substituir thumb se enviada
        thumb_file = request.files.get('thumb')
        if thumb_file and getattr(thumb_file,'filename',''):
            fn = thumb_file.filename.lower()
            if any(fn.endswith(ext) for ext in ['.png','.jpg','.jpeg','.webp','.gif']):
                upload_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads', 'videos', 'thumbs')
                upload_dir = os.path.normpath(upload_dir)
                os.makedirs(upload_dir, exist_ok=True)
                save_name = f"{uuid.uuid4().hex}{os.path.splitext(fn)[1]}"
                save_path = os.path.join(upload_dir, save_name)
                thumb_file.save(save_path)
                extra['thumb'] = f"uploads/videos/thumbs/{save_name}"
    c.extra = json.dumps(extra) if extra else None
    try:
        db.session.commit()
        # Sempre retornar JSON pois esta rota é usada apenas via AJAX
        return {'success': True, 'message': 'Conteúdo atualizado.'}, 200
    except Exception as e:
        db.session.rollback()
        from flask import current_app
        current_app.logger.error(f'Erro ao atualizar conteúdo {content_id}: {str(e)}')
        return {'success': False, 'message': f'Erro ao salvar: {str(e)}'}, 500

@admin_bp.route('/edu/content/<int:content_id>/delete', methods=['POST'])
@login_required
def delete_edu_content(content_id: int):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    c = EduContent.query.get_or_404(content_id)
    # Se for vídeo, tentar remover thumb local
    try:
        import json, os
        ex = json.loads(c.extra) if c.extra else {}
        th = ex.get('thumb')
        if th and not str(th).startswith('http'):
            path = os.path.join(os.path.dirname(__file__), '..', 'static', th)
            path = os.path.normpath(path)
            if os.path.exists(path):
                os.remove(path)
        # Se for apostila, remover também o PDF salvo em file_path
        if c.tipo == 'apostila' and c.file_path:
            pdf_path = os.path.join(os.path.dirname(__file__), '..', 'static', c.file_path)
            pdf_path = os.path.normpath(pdf_path)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
    except Exception:
        pass
    db.session.delete(c)
    db.session.commit()
    flash('Conteúdo excluído.')
    # Tenta voltar para a página de origem (pública) se informado
    next_url = request.form.get('next') or request.referrer
    try:
        if next_url:
            return redirect(next_url)
    except Exception:
        pass
    return redirect(url_for('admin.dashboard', _anchor='edu'))

@admin_bp.route('/edu/question', methods=['POST'])
@login_required
def edu_create_question():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    topic_id = request.form.get('topic_id')
    section_id = request.form.get('section_id') or None
    enunciado = request.form.get('enunciado','').strip()
    resposta = request.form.get('resposta','').strip() or None
    dificuldade = request.form.get('dificuldade','').strip() or None
    tipo = request.form.get('tipo','').strip() or None
    opcoes = request.form.get('opcoes','').strip() or None
    if not (topic_id and enunciado):
        flash('Selecione tópico e informe enunciado.')
        return redirect(url_for('admin.dashboard', _anchor='edu'))
    q = ExerciseQuestion(topic_id=topic_id, section_id=section_id, enunciado=enunciado, resposta=resposta, dificuldade=dificuldade, tipo=tipo, opcoes=opcoes)
    db.session.add(q)
    db.session.commit()
    flash('Questão adicionada.')
    return redirect(url_for('admin.dashboard', _anchor='edu'))

@admin_bp.route('/edu/question/<int:question_id>.json')
@login_required
def get_question_json(question_id: int):
    if not current_user.is_admin:
        return {"error":"forbidden"}, 403
    q = ExerciseQuestion.query.get_or_404(question_id)
    return {
        "id": q.id,
        "topic_id": q.topic_id,
        "section_id": q.section_id,
        "enunciado": q.enunciado,
        "resposta": q.resposta,
        "dificuldade": q.dificuldade,
        "tipo": q.tipo,
        "opcoes": q.opcoes
    }

@admin_bp.route('/edu/question/<int:question_id>/update', methods=['POST'])
@login_required
def update_question(question_id: int):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    q = ExerciseQuestion.query.get_or_404(question_id)
    q.enunciado = request.form.get('enunciado','').strip() or q.enunciado
    q.resposta = request.form.get('resposta','').strip() or None
    q.dificuldade = request.form.get('dificuldade','').strip() or None
    q.tipo = request.form.get('tipo','').strip() or q.tipo
    q.opcoes = request.form.get('opcoes','').strip() or None
    topic_id = request.form.get('topic_id')
    if topic_id:
        q.topic_id = int(topic_id)
    section_id = request.form.get('section_id')
    if section_id:
        q.section_id = int(section_id) if section_id != '' else None
    db.session.commit()
    flash('Questão atualizada.')
    next_url = request.form.get('next') or request.referrer or url_for('main.exercicios')
    return redirect(next_url)

@admin_bp.route('/edu/question/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_question(question_id: int):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    q = ExerciseQuestion.query.get_or_404(question_id)
    db.session.delete(q)
    db.session.commit()
    flash('Questão excluída.')
    next_url = request.form.get('next') or request.referrer or url_for('main.exercicios')
    return redirect(next_url)

@admin_bp.route('/exercicios/section', methods=['POST'])
@login_required
def exercicios_create_section():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    topic_id = request.form.get('topic_id')
    nome = request.form.get('nome','').strip()
    descricao = request.form.get('descricao','').strip() or None
    ordem = request.form.get('ordem') or 0
    if not (topic_id and nome):
        flash('Informe tópico e nome da sessão.')
        return redirect(url_for('admin.dashboard', _anchor='edu'))
    try:
        ordem = int(ordem)
    except ValueError:
        ordem = 0
    if ExerciseSection.query.filter_by(topic_id=topic_id, nome=nome).first():
        flash('Já existe sessão com esse nome neste tópico.')
        return redirect(url_for('admin.dashboard', _anchor='edu'))
    s = ExerciseSection(topic_id=topic_id, nome=nome, descricao=descricao, ordem=ordem)
    db.session.add(s)
    db.session.commit()
    flash('Sessão criada.')
    return redirect(url_for('admin.dashboard', _anchor='edu'))

@admin_bp.route('/exercicios/topic/<int:topic_id>', methods=['POST'])
@login_required
def exercicios_topic_update(topic_id):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    topic = ExerciseTopic.query.get_or_404(topic_id)
    nome = request.form.get('nome','').strip()
    descricao = request.form.get('descricao','').strip() or None
    if not nome:
        flash('Nome do tópico é obrigatório.')
        return redirect(url_for('admin.dashboard', _anchor='edu'))
    # Check if another topic with same name exists
    existing = ExerciseTopic.query.filter_by(nome=nome).first()
    if existing and existing.id != topic_id:
        flash('Já existe tópico com esse nome.')
        return redirect(url_for('admin.dashboard', _anchor='edu'))
    topic.nome = nome
    topic.descricao = descricao
    db.session.commit()
    flash('Tópico atualizado com sucesso.')
    return redirect(url_for('admin.dashboard', _anchor='edu'))

@admin_bp.route('/exercicios/section/<int:section_id>', methods=['POST'])
@login_required
def exercicios_section_update(section_id):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    section = ExerciseSection.query.get_or_404(section_id)
    nome = request.form.get('nome','').strip()
    descricao = request.form.get('descricao','').strip() or None
    ordem = request.form.get('ordem') or 0
    if not nome:
        flash('Nome da sessão é obrigatório.')
        return redirect(url_for('admin.dashboard', _anchor='edu'))
    try:
        ordem = int(ordem)
    except ValueError:
        ordem = 0
    # Check if another section with same name exists in same topic
    existing = ExerciseSection.query.filter_by(topic_id=section.topic_id, nome=nome).first()
    if existing and existing.id != section_id:
        flash('Já existe sessão com esse nome neste tópico.')
        return redirect(url_for('admin.dashboard', _anchor='edu'))
    section.nome = nome
    section.descricao = descricao
    section.ordem = ordem
    db.session.commit()
    flash('Sessão atualizada com sucesso.')
    return redirect(url_for('admin.dashboard', _anchor='edu'))

@admin_bp.route('/variacoes/salvar', methods=['POST'])
@login_required
def salvar_variacoes():
    # Rota legada descontinuada: agora usamos "Vídeos" em EDU
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    flash('A seção "Variações" foi substituída por "Vídeos". Publique vídeos em EDU > Vídeos.')
    return redirect(url_for('admin.dashboard', _anchor='edu'))

@admin_bp.route('/excluir_usuario/<int:user_id>', methods=['POST'])
@login_required
def excluir_usuario(user_id):
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)
    if getattr(user, 'is_superadmin', False):
        flash('Não é possível excluir o superadmin.')
        return redirect(url_for('admin.dashboard'))
    if user.id == current_user.id and not current_user.is_superadmin:
        flash('Você não pode excluir a si mesme.')
        return redirect(url_for('admin.dashboard'))
    db.session.delete(user)
    db.session.commit()
    flash('Usuárie excluíde.')
    return redirect(url_for('admin.dashboard'))

# --- Rotas de moderação ---
from datetime import datetime, timedelta

def _ensure_admin():
    if not getattr(current_user, 'is_admin', False):
        return False
    return True

def _can_act_on(user: User):
    # somente superadmin pode agir sobre superadmin
    if getattr(user, 'is_superadmin', False) and not current_user.is_superadmin:
        return False
    return True

@admin_bp.route('/user/<int:user_id>/suspend', methods=['POST'])
@login_required
def suspend_user(user_id):
    if not _ensure_admin():
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)
    if not _can_act_on(user):
        flash('Sem permissão para suspender este usuárie.')
        return redirect(url_for('admin.dashboard', _anchor='geral'))
    try:
        hours = int(request.form.get('hours', '0'))
    except ValueError:
        hours = 0
    if hours <= 0:
        flash('Informe horas > 0.')
        return redirect(url_for('admin.dashboard', _anchor='geral'))
    user.suspended_until = datetime.utcnow() + timedelta(hours=hours)
    db.session.commit()
    flash(f'Usuárie suspenso até {user.suspended_until.strftime("%d/%m %H:%M")}')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/<int:user_id>/unsuspend', methods=['POST'])
@login_required
def unsuspend_user(user_id):
    if not _ensure_admin():
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)
    if not _can_act_on(user):
        flash('Sem permissão.')
        return redirect(url_for('admin.dashboard'))
    user.suspended_until = None
    db.session.commit()
    flash('Suspensão removida.')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/<int:user_id>/ban', methods=['POST'])
@login_required
def ban_user(user_id):
    if not _ensure_admin():
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)
    if not _can_act_on(user):
        flash('Sem permissão.')
        return redirect(url_for('admin.dashboard'))
    motivo = request.form.get('reason', '').strip() or None
    user.is_banned = True
    user.banned_at = datetime.utcnow()
    user.ban_reason = motivo
    db.session.commit()
    flash('Usuárie banido.')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/<int:user_id>/unban', methods=['POST'])
@login_required
def unban_user(user_id):
    if not _ensure_admin():
        return redirect(url_for('main.index'))
    user = User.query.get_or_404(user_id)
    if not _can_act_on(user):
        flash('Sem permissão.')
        return redirect(url_for('admin.dashboard'))
    user.is_banned = False
    user.banned_at = None
    user.ban_reason = None
    db.session.commit()
    flash('Ban removido.')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/report/<int:report_id>/resolve', methods=['POST'])
@login_required
def resolve_report(report_id):
    if not _ensure_admin():
        return redirect(url_for('main.index'))
    rep = Report.query.get_or_404(report_id)
    rep.resolved = True
    rep.resolved_at = datetime.utcnow()
    db.session.commit()
    flash('Denúncia marcada como resolvida.')
    return redirect(url_for('admin.dashboard', _anchor='gramatike'))

@admin_bp.route('/report/<int:report_id>/delete_post', methods=['POST'])
@login_required
def delete_report_post(report_id):
    if not _ensure_admin():
        return redirect(url_for('main.index'))
    rep = Report.query.get_or_404(report_id)
    post = Post.query.get(rep.post_id)
    if post:
        db.session.delete(post)
    rep.resolved = True
    rep.resolved_at = datetime.utcnow()
    db.session.commit()
    flash('Post excluído e denúncia resolvida.')
    return redirect(url_for('admin.dashboard', _anchor='gramatike'))

# --- Palavra do Dia Admin Routes ---

@admin_bp.route('/palavra-do-dia/create', methods=['POST'])
@login_required
def palavra_do_dia_create():
    """Criar uma nova palavra do dia."""
    if not _ensure_admin():
        return redirect(url_for('main.index'))
    
    from gramatike_app.models import PalavraDoDia
    from sqlalchemy import func
    
    palavra = request.form.get('palavra', '').strip()
    significado = request.form.get('significado', '').strip()
    
    if not palavra or not significado:
        flash('Palavra e significado são obrigatórios.', 'error')
        return redirect(url_for('admin.dashboard', _anchor='gramatike'))
    
    # Define ordem como próximo número disponível
    max_ordem = db.session.query(func.max(PalavraDoDia.ordem)).scalar() or 0
    
    nova_palavra = PalavraDoDia(
        palavra=palavra,
        significado=significado,
        ordem=max_ordem + 1,
        ativo=True,
        created_by=current_user.id
    )
    db.session.add(nova_palavra)
    db.session.commit()
    
    flash(f'Palavra "{palavra}" adicionada com sucesso!', 'success')
    return redirect(url_for('admin.dashboard', _anchor='gramatike'))

@admin_bp.route('/palavra-do-dia/list')
@login_required
def palavra_do_dia_list():
    """Listar todas as palavras do dia com contagem de interações."""
    if not _ensure_admin():
        return jsonify({'error': 'Não autorizado'}), 403
    
    from gramatike_app.models import PalavraDoDia, PalavraDoDiaInteracao
    
    palavras = PalavraDoDia.query.order_by(PalavraDoDia.ordem.asc()).all()
    
    result = []
    for p in palavras:
        interacoes_count = PalavraDoDiaInteracao.query.filter_by(palavra_id=p.id).count()
        result.append({
            'id': p.id,
            'palavra': p.palavra,
            'significado': p.significado,
            'ordem': p.ordem,
            'ativo': p.ativo,
            'interacoes_count': interacoes_count
        })
    
    return jsonify(result)

@admin_bp.route('/palavra-do-dia/<int:palavra_id>/toggle', methods=['POST'])
@login_required
def palavra_do_dia_toggle(palavra_id):
    """Ativar/desativar uma palavra do dia."""
    if not _ensure_admin():
        return redirect(url_for('main.index'))
    
    from gramatike_app.models import PalavraDoDia
    
    palavra = PalavraDoDia.query.get_or_404(palavra_id)
    palavra.ativo = not palavra.ativo
    db.session.commit()
    
    status = 'ativada' if palavra.ativo else 'desativada'
    flash(f'Palavra "{palavra.palavra}" {status} com sucesso!', 'success')
    return redirect(url_for('admin.dashboard', _anchor='gramatike'))

@admin_bp.route('/palavra-do-dia/<int:palavra_id>/delete', methods=['POST'])
@login_required
def palavra_do_dia_delete(palavra_id):
    """Excluir uma palavra do dia."""
    if not _ensure_admin():
        return redirect(url_for('main.index'))
    
    from gramatike_app.models import PalavraDoDia
    
    palavra = PalavraDoDia.query.get_or_404(palavra_id)
    db.session.delete(palavra)
    db.session.commit()
    
    flash(f'Palavra "{palavra.palavra}" excluída com sucesso!', 'success')
    return redirect(url_for('admin.dashboard', _anchor='gramatike'))

@admin_bp.route('/palavra-do-dia/respostas')
@login_required
def palavra_do_dia_respostas():
    """Listar respostas/interações das palavras do dia."""
    if not _ensure_admin():
        return jsonify({'error': 'Não autorizado'}), 403
    
    from gramatike_app.models import PalavraDoDiaInteracao, PalavraDoDia, User
    
    palavra_id = request.args.get('palavra_id', type=int)
    
    query = PalavraDoDiaInteracao.query
    if palavra_id:
        query = query.filter_by(palavra_id=palavra_id)
    
    interacoes = query.order_by(PalavraDoDiaInteracao.created_at.desc()).limit(100).all()
    
    result = []
    for i in interacoes:
        result.append({
            'id': i.id,
            'palavra': i.palavra.palavra if i.palavra else 'N/A',
            'usuario': i.usuario.username if i.usuario else 'N/A',
            'tipo': i.tipo,
            'frase': i.frase,
            'data': i.created_at.strftime('%d/%m/%Y %H:%M') if i.created_at else 'N/A'
        })
    
    return jsonify(result)

## Rotas de configuração/IA do Lune removidas

## Removido bloco inseguro de criação automática de admin hardcoded.
