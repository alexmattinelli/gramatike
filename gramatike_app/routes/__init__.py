from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort, current_app, session
from flask import Response, stream_with_context, send_file
from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from datetime import datetime, timedelta
import os
import re
from werkzeug.utils import secure_filename
from mimetypes import guess_type
from gramatike_app.utils.storage import upload_bytes_to_supabase, build_avatar_path, build_post_image_path, build_apostila_path, build_divulgacao_path
from gramatike_app.models import User, db, Post, Curtida, Comentario, Report, EduContent, EduTopic, ExerciseTopic, ExerciseQuestion, ExerciseSection, SupportTicket, Divulgacao, post_likes, PostImage, Dynamic, DynamicResponse
from gramatike_app.utils.emailer import send_email, render_welcome_email, render_verify_email, render_reset_email, render_change_email_email
from gramatike_app.utils.tokens import generate_token, verify_token
from gramatike_app.utils.moderation import check_text, check_image_hint, refusal_message_pt
from gramatike_app.models import EduNovidade

# Helper: converter datas para horário de Brasília (America/Sao_Paulo)
def _to_brasilia(dt: datetime) -> datetime:
    try:
        if dt is None:
            return dt
        try:
            from zoneinfo import ZoneInfo  # Python 3.9+
        except Exception:
            return dt
        tz = ZoneInfo("America/Sao_Paulo")
        # Considera que valores sem tz vêm em UTC na base
        if dt.tzinfo is None:
            from datetime import timezone as _tz
            dt = dt.replace(tzinfo=_tz.utc)
        return dt.astimezone(tz)
    except Exception:
        return dt

def _ensure_edunovidade_table(seed=False):
    """Garante que a tabela edu_novidade exista (SQLite fallback) e opcionalmente faz seed do guia básico."""
    try:
        engine = db.get_engine()
        if engine.name == 'sqlite':
            with engine.connect() as conn:
                tbl = conn.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table' AND name='edu_novidade'").fetchone()
                if not tbl:
                    conn.exec_driver_sql("""
                        CREATE TABLE edu_novidade (
                            id INTEGER PRIMARY KEY,
                            titulo VARCHAR(200) NOT NULL,
                            descricao VARCHAR(500),
                            link VARCHAR(600),
                            created_at DATETIME,
                            author_id INTEGER
                        )
                    """)
                    conn.exec_driver_sql("CREATE INDEX IF NOT EXISTS ix_edu_novidade_created_at ON edu_novidade(created_at)")
        if seed:
            # Se vazio tenta criar a novidade do guia (apenas uma vez)
            if not EduNovidade.query.first():
                from gramatike_app.models import EduContent
                guia = (EduContent.query
                            .filter(EduContent.titulo.ilike('%guia básico de gênero neutro%'))
                            .order_by(EduContent.created_at.desc())
                            .first())
                if guia:
                    n = EduNovidade(titulo=guia.titulo,
                                     descricao=(guia.resumo or (guia.corpo[:200] + ('…' if guia.corpo and len(guia.corpo)>200 else '')) if guia.corpo else ''),
                                     link=guia.url,
                                     created_at=guia.created_at,
                                     author_id=guia.author_id)
                    db.session.add(n)
                    db.session.commit()
    except Exception as _e:
        current_app.logger.warning(f"ensure_edunovidade_table failed: {_e}")
bp = Blueprint('main', __name__)
@bp.route('/api/gramatike/search')
def api_gramatike_search():
    """Busca somente posts do perfil @gramatike (unificado).
    Parâmetros: ?q= termo opcional & limit= N (máx 40)
    Retorna lista JSON: { items: [ {id,title,snippet,tags,url,created_at} ] }
    """
    q = (request.args.get('q') or '').strip()
    limit = min(int(request.args.get('limit', 15) or 15), 40)
    include_edu = request.args.get('include_edu') == '1'
    
    items = []
    try:
        # Obtém id do usuário @gramatike se existir
        gk_user = User.query.filter(User.username == 'gramatike').first()
        post_query = Post.query.filter(((Post.is_deleted == False) | (Post.is_deleted.is_(None))))
        if gk_user:
            post_query = post_query.filter((Post.usuario_id == gk_user.id) | (Post.usuario == 'gramatike'))
        else:
            # fallback: filtra por nome textual
            post_query = post_query.filter(Post.usuario == 'gramatike')
        if q:
            like = f"%{q}%"
            post_query = post_query.filter(Post.conteudo.ilike(like))
        posts = post_query.order_by(Post.data.desc().nullslast()).limit(limit).all()
        for p in posts:
            base = (p.conteudo or '').strip()
            snippet = base[:200] + ('…' if len(base) > 200 else '')
            items.append({
                'id': p.id,
                'title': (base[:60] + '…') if len(base) > 60 else (base or 'Post'),
                'snippet': snippet,
                'tags': _extract_tags(base),
                'url': f"/post/{p.id}",
                'created_at': p.data.isoformat() if p.data else None,
                'source': 'post'
            })

        # Novidades (Postar Novidade) – sempre incluir (até 10) para aparecer no feed principal
        _ensure_edunovidade_table(seed=True)
        try:
            novidades_rows = EduNovidade.query.order_by(EduNovidade.created_at.desc()).limit(10).all()
            for n in novidades_rows:
                desc = (n.descricao or '')
                snippet = desc[:200] + ('…' if len(desc) > 200 else '')
                items.append({
                    'id': f"nov-{n.id}",
                    'title': (n.titulo[:60] + '…') if len(n.titulo) > 60 else n.titulo,
                    'snippet': snippet,
                    'tags': [],
                    'url': url_for('main.novidade_detail', novidade_id=n.id),
                    'created_at': n.created_at.isoformat() if n.created_at else None,
                    'source': 'novidade'
                })
        except Exception as _en:
            current_app.logger.warning(f"novidades load failed: {_en}")

        # Incluir Dinâmicas ativas (MVP) — aparecem no feed do Gramátike Edu
        try:
            dyn_rows = Dynamic.query.filter_by(active=True).order_by(Dynamic.created_at.desc()).limit(10).all()
            for d in dyn_rows:
                items.append({
                    'id': f"dyn-{d.id}",
                    'title': (d.titulo[:60] + '…') if len(d.titulo) > 60 else d.titulo,
                    'snippet': (d.descricao or ''),
                    'tags': [d.tipo],
                    'url': url_for('main.dinamica_view', dyn_id=d.id),
                    'created_at': d.created_at.isoformat() if d.created_at else None,
                    'source': 'dinamica'
                })
        except Exception as _edyn:
            current_app.logger.warning(f"dyn feed failed: {_edyn}")

        # --- (Ajuste) Itens EduContent removidos do feed padrão para evitar poluição / repetição de ARTIGOS ---
        # Para reativar inclusão opcional enviar ?include_edu=1
        if include_edu:
            from sqlalchemy import or_
            keywords = ['genero neutro', 'gênero neutro', 'linguagem neutra', 'rita von hunty', 'rita von']
            edu_query = EduContent.query.filter(EduContent.tipo.in_(['artigo','apostila','video','podcast']))
            clauses = []
            for kw in keywords:
                like_kw = f"%{kw}%"
                clauses.append(EduContent.titulo.ilike(like_kw))
                clauses.append(EduContent.resumo.ilike(like_kw))
                clauses.append(EduContent.corpo.ilike(like_kw))
            if clauses:
                edu_query = edu_query.filter(or_(*clauses))
            if q:
                q_like = f"%{q}%"
                edu_query = edu_query.filter(
                    or_(EduContent.titulo.ilike(q_like), EduContent.resumo.ilike(q_like), EduContent.corpo.ilike(q_like))
                )
            edu_items = edu_query.order_by(EduContent.created_at.desc().nullslast()).limit(12).all()
            for c in edu_items:
                text_base = (c.resumo or c.corpo or '')
                snippet = text_base[:200] + ('…' if len(text_base) > 200 else '')
                items.append({
                    'id': f"edu-{c.id}",
                    'title': (c.titulo[:60] + '…') if len(c.titulo) > 60 else c.titulo,
                    'snippet': snippet,
                    'tags': _extract_tags(text_base)[:6],
                    'url': _build_media_url(c),
                    'created_at': c.created_at.isoformat() if c.created_at else None,
                    'source': c.tipo
                })

        # Ordena combinando (mais recente primeiro) se tiver datas
        try:
            items.sort(key=lambda x: x.get('created_at') or '', reverse=True)
        except Exception:
            pass
    except Exception as e:
        current_app.logger.warning(f"api_gramatike_search failed: {e}")
    
    return jsonify({'items': items})

def _extract_tags(text: str):
    if not text: return []
    try:
        import re
        tags = re.findall(r"#(\w{2,30})", text)
        out = []
        for t in tags:
            t = t.lower()
            if t not in out:
                out.append(t)
        return out[:8]
    except Exception:
        return []

def _build_media_url(c: EduContent):
    try:
        if c.tipo == 'podcast':
            return '/podcasts'
        if c.tipo == 'video':
            return '/videos'
        return f"/edu/{c.id}"
    except Exception:
        return f"/edu/{getattr(c,'id',0)}"

# Coletor de relatórios CSP (Report-Only e enforce). Apenas loga por enquanto.
@bp.route('/api/csp-report', methods=['POST'])
def api_csp_report():
    try:
        payload = request.get_json(silent=True) or {}
        current_app.logger.warning(f"CSP report: {payload}")
    except Exception as _e:
        current_app.logger.warning(f"CSP report parse failed: {_e}")
    # retorna 204 para não poluir a rede
    return ('', 204)
# (RAG endpoints removidos)

# Reenvio de verificação de e-mail
@bp.route('/api/email/resend-verification', methods=['POST'])
@login_required
def resend_verification_email():
    try:
        if getattr(current_user, 'email_confirmed', False):
            return '', 204
        token = generate_token({'uid': current_user.id, 'scope': 'verify'})
        verify_url = url_for('main.verify_email', token=token, _external=True)
        html_v = render_verify_email(current_user.username or current_user.email, verify_url)
        send_email(current_user.email, 'Confirme seu e-mail', html_v)
        return '', 204
    except Exception as e:
        current_app.logger.error(f"resend verification failed: {e}")
        return jsonify({'error': 'send_failed'}), 500

## (Funções auxiliares Lune removidas)

# API para buscar usuário por username
@bp.route('/api/usuarios/username/<username>', methods=['GET'])
def buscar_usuario_por_username(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'erro': 'Usuárie não encontrade'}), 404
    return jsonify({'id': user.id, 'username': user.username, 'nome': user.nome})

@bp.route('/api/usuarios/search')
def search_usuarios():
    q = request.args.get('q','').strip()
    if not q:
        return jsonify([])
    from sqlalchemy import or_
    like = f"%{q}%"
    users = User.query.filter(or_(User.username.ilike(like), User.nome.ilike(like))).order_by(User.username.asc()).limit(20).all()
    return jsonify([
        {'id':u.id,'username':u.username,'nome':u.nome} for u in users
    ])
# --- Rotas de seguir/deixar de seguir e APIs de seguidores/seguindo ---
@bp.route('/api/seguir/<int:user_id>', methods=['POST'])
@login_required
def seguir_usuario(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        return jsonify({'erro': 'Você não pode seguir a si mesmo.'}), 400
    if not current_user.seguindo.filter_by(id=user.id).first():
        current_user.seguindo.append(user)
        db.session.commit()
    return '', 204

@bp.route('/api/seguir/<int:user_id>', methods=['DELETE'])
@login_required
def deixar_de_seguir_usuario(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        return jsonify({'erro': 'Você não pode deixar de seguir a si mesmo.'}), 400
    if current_user.seguindo.filter_by(id=user.id).first():
        current_user.seguindo.remove(user)
        db.session.commit()
    return '', 204

@bp.route('/api/seguidores/<int:user_id>', methods=['GET'])
def listar_seguidores(user_id):
    user = User.query.get_or_404(user_id)
    seguidores = [{'id': u.id, 'username': u.username, 'nome': u.nome} for u in user.seguidores]
    return jsonify(seguidores)

@bp.route('/api/seguindo/<int:user_id>', methods=['GET'])
def listar_seguindo(user_id):
    user = User.query.get_or_404(user_id)
    seguindo = [{'id': u.id, 'username': u.username, 'nome': u.nome} for u in user.seguindo]
    return jsonify(seguindo)

@bp.route('/api/amigues', methods=['GET'])
@login_required
def api_amigues():
    """Retorna lista de amigues (seguimento mútuo)."""
    try:
        user = current_user
        seguindo_ids = {u.id for u in user.seguindo}
        # amigues = usuários que seguem o user E são seguidos por ele
        mutual = [u for u in user.seguidores if u.id in seguindo_ids]
        out = []
        for m in mutual:
            out.append({
                'id': m.id,
                'username': m.username,
                'nome': m.nome,
                'foto_perfil': m.foto_perfil or 'img/perfil.png'
            })
        # Ordena alfabeticamente por username
        out.sort(key=lambda x: (x['username'] or '').lower())
        return jsonify(out)
    except Exception as e:
        current_app.logger.warning(f"api_amigues failed: {e}")
        return jsonify([])

@bp.route('/api/notifications', methods=['GET'])
@login_required
def api_notifications():
    """Retorna notificações do usuário (novos seguidores e curtidas)."""
    try:
        user = current_user
        notifications = []
        
        # Get recent followers (last 10)
        recent_followers = user.seguidores.order_by(User.id.desc()).limit(10).all()
        for follower in recent_followers:
            notifications.append({
                'type': 'follower',
                'user_id': follower.id,
                'username': follower.username,
                'nome': follower.nome or follower.username,
                'foto_perfil': follower.foto_perfil or 'img/perfil.png',
                'message': f'{follower.nome or follower.username} começou a te seguir',
                'link': f'/perfil/{follower.username}',
                'time': 'recente'
            })
        
        # Get recent likes on user's posts (last 10)
        user_posts = Post.query.filter_by(usuario_id=user.id, is_deleted=False).all()
        user_post_ids = [p.id for p in user_posts]
        
        if user_post_ids:
            # Query post_likes for likes on user's posts
            recent_likes = db.session.query(post_likes).filter(
                post_likes.c.post_id.in_(user_post_ids)
            ).order_by(post_likes.c.post_id.desc()).limit(20).all()
            
            # Get unique likers (avoid duplicates)
            seen_users = set()
            for like in recent_likes:
                user_id = like.user_id
                post_id = like.post_id
                
                if user_id == user.id:  # Skip self-likes
                    continue
                    
                if user_id in seen_users:
                    continue
                seen_users.add(user_id)
                
                liker = User.query.get(user_id)
                post = Post.query.get(post_id)
                
                if liker and post and len(notifications) < 20:
                    notifications.append({
                        'type': 'like',
                        'user_id': liker.id,
                        'username': liker.username,
                        'nome': liker.nome or liker.username,
                        'foto_perfil': liker.foto_perfil or 'img/perfil.png',
                        'message': f'{liker.nome or liker.username} curtiu sua publicação',
                        'link': f'/post/{post_id}',
                        'time': 'recente'
                    })
                    
                if len(notifications) >= 15:
                    break
        
        return jsonify(notifications[:15])  # Limit to 15 notifications
    except Exception as e:
        current_app.logger.warning(f"api_notifications failed: {e}")
        return jsonify([])

# ROTA ALTERNATIVA: Postagens do usuário logado
@bp.route('/api/posts/me', methods=['GET'])
@login_required
def get_posts_me():
    user = current_user
    posts = Post.query.filter(
        ((Post.usuario_id == user.id) | (Post.usuario == user.username)) & ((Post.is_deleted == False) | (Post.is_deleted.is_(None)))
    ).order_by(Post.data.desc()).all()
    result = []
    for p in posts:
        try:
            data_str = p.data.strftime('%d/%m/%Y %H:%M') if p.data else ''
        except Exception as e:
            data_str = ''
        result.append({
            'id': p.id,
            'usuario': user.username,
            'conteudo': p.conteudo or '',
            'imagem': p.imagem or '',
            'data': data_str,
            'foto_perfil': user.foto_perfil or 'img/perfil.png',
            'bio': user.bio or '',
            'can_delete': True
        })
    return jsonify(result)

# API: Postagens de um usuário específico (pública)
@bp.route('/api/posts/usuario/<int:user_id>', methods=['GET'])
def get_posts_usuario(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter(
        ((Post.usuario_id == user.id) | (Post.usuario == user.username)) & ((Post.is_deleted == False) | (Post.is_deleted.is_(None)))
    ).order_by(Post.data.desc()).all()
    result = []
    for p in posts:
        try:
            data_str = p.data.strftime('%d/%m/%Y %H:%M') if p.data else ''
        except Exception:
            data_str = ''
        result.append({
            'id': p.id,
            'usuario': user.username,
            'conteudo': p.conteudo or '',
            'imagem': p.imagem or '',
            'data': data_str,
            'foto_perfil': user.foto_perfil or 'img/perfil.png',
            'bio': user.bio or '',
            'can_delete': (current_user.is_authenticated and (current_user.id == user.id or getattr(current_user,'is_admin',False)))
        })
    return jsonify(result)


## (Removido bloco duplicado de imports e novo Blueprint que sobrescrevia rotas anteriores)

# ROTA PARA EDIÇÃO DE PERFIL
@bp.route('/api/editar-perfil', methods=['POST'], endpoint='editar_perfil_api')
@login_required
def editar_perfil():
    user = current_user
    # Bloqueio de operação se banido/suspenso
    if getattr(user, 'is_banned', False):
        return jsonify({'erro': 'Conta bloqueada.'}), 403
    try:
        if getattr(user, 'suspended_until', None):
            from datetime import datetime as _dt
            if user.suspended_until and user.suspended_until > _dt.utcnow():
                return jsonify({'erro': 'Conta suspensa temporariamente.'}), 403
    except Exception:
        pass
    nome = request.form.get('nome')
    username = request.form.get('username')
    email = request.form.get('email')
    genero = request.form.get('genero')
    pronome = request.form.get('pronome') or request.form.get('pronomes')
    bio = request.form.get('bio')
    foto = request.files.get('foto_perfil')
    data_nascimento_str = request.form.get('data_nascimento')
    # Campos de senha (opcionais)
    current_password = request.form.get('current_password')
    new_password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')

    if nome:
        user.nome = nome
    # Atualiza username se enviado (normaliza removendo '@' inicial) e se não estiver em uso
    if username is not None:
        novo_username = (username or '').strip().lstrip('@')
        if novo_username and novo_username != user.username:
            # Validate username - no spaces allowed and length requirements
            if ' ' in novo_username:
                return jsonify({'erro': 'Nome de usuário não pode conter espaços.'}), 400
            
            if len(novo_username) < 5:
                return jsonify({'erro': 'Nome de usuário deve ter no mínimo 5 caracteres.'}), 400
            
            if len(novo_username) > 45:
                return jsonify({'erro': 'Nome de usuário deve ter no máximo 45 caracteres.'}), 400
            ok_u, cat_u, matched_u = check_text(novo_username)
            if not ok_u:
                return jsonify({'erro': refusal_message_pt(cat_u, matched_u)}), 400
            # checar unicidade
            existente = User.query.filter(User.username == novo_username, User.id != user.id).first()
            if existente:
                return jsonify({'erro': 'Este nome de usuário já está em uso.'}), 400
            user.username = novo_username
    if email is not None:
        novo_email = (email or '').strip()
        if novo_email and novo_email != user.email:
            existente = User.query.filter(User.email == novo_email, User.id != user.id).first()
            if existente:
                return jsonify({'erro': 'Este e-mail já está em uso.'}), 400
            # Admins/superadmins podem alterar diretamente sem confirmação
            if getattr(user, 'is_superadmin', False) or getattr(user, 'is_admin', False):
                try:
                    user.email = novo_email
                    try:
                        user.email_confirmed = False
                    except Exception:
                        pass
                except Exception as _e_dir:
                    return jsonify({'erro': f'Falha ao atualizar e-mail: {_e_dir}'}), 400
            else:
                # Para usuáries comuns: envia confirmação para o novo e-mail
                try:
                    token = generate_token({'uid': user.id, 'scope': 'change_email', 'new_email': novo_email})
                    confirm_url = url_for('main.confirm_change_email', token=token, _external=True)
                    html_c = render_change_email_email(user.username or user.email, confirm_url, novo_email)
                    # Tenta enviar para o novo e-mail; se falhar, apenas registra e segue com outras alterações
                    if not send_email(novo_email, 'Confirmar novo e-mail', html_c):
                        try:
                            current_app.logger.warning('Não foi possível enviar verificação para o novo e-mail; mantendo e-mail atual.')
                        except Exception:
                            pass
                except Exception as _e_email:
                    try:
                        current_app.logger.warning(f'Falha ao preparar/enviar confirmação de e-mail: {_e_email}')
                    except Exception:
                        pass
    if genero:
        user.genero = genero
    if pronome:
        user.pronome = pronome
    if bio is not None:
        ok_b, cat_b, matched_b = check_text(bio)
        if not ok_b:
            return jsonify({'erro': refusal_message_pt(cat_b, matched_b)}), 400
        user.bio = bio
    if data_nascimento_str:
        try:
            from datetime import datetime
            user.data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
        except Exception:
            user.data_nascimento = None
    if foto and foto.filename:
        # Upload de avatar: tentaSupabase primeiro; se falhar, tenta salvar localmente.
        try:
            filename = secure_filename(foto.filename)
            # Tenta enviar para Supabase Storage
            foto_bytes = foto.read()
            foto.seek(0)  # reposiciona para fallback local
            ctype, _ = guess_type(filename)
            remote_path = build_avatar_path(user.id, filename)
            public_url = upload_bytes_to_supabase(remote_path, foto_bytes, content_type=ctype or 'application/octet-stream')
            if public_url:
                # Guarda URL absoluta; os templates precisam aceitar URL externas
                user.foto_perfil = public_url
            else:
                # Fallback: salvar localmente (pode falhar em FS somente leitura)
                base_static = getattr(current_app, 'static_folder', None) or os.path.join('gramatike_app', 'static')
                pasta = os.path.join(base_static, 'img', 'perfil')
                os.makedirs(pasta, exist_ok=True)
                caminho = os.path.join(pasta, filename)
                foto.save(caminho)
                user.foto_perfil = f'img/perfil/{filename}'
        except Exception as _e_save:
            try:
                current_app.logger.warning(f'Falha no upload/salvamento de avatar: {_e_save}')
            except Exception:
                pass
    # Atualização de senha (opcional): só processa se usuário enviou nova senha
    if (new_password or password_confirm):
        if (new_password or '').strip() == '' or (password_confirm or '').strip() == '':
            return jsonify({'erro': 'Informe e confirme a nova senha.'}), 400
        if new_password != password_confirm:
            return jsonify({'erro': 'As senhas não coincidem.'}), 400
        # Requer senha atual correta
        if (current_password or '').strip() == '':
            return jsonify({'erro': 'Informe a senha atual.'}), 400
        if not user.check_password(current_password):
            return jsonify({'erro': 'Senha atual incorreta.'}), 400
        user.set_password(new_password)
    try:
        db.session.commit()
        return '', 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 400

@bp.route('/confirmar-email-novo')
def confirm_change_email():
    token = request.args.get('token','')
    data = verify_token(token, max_age=60*60*24)
    if not data or data.get('scope') != 'change_email':
        flash('Token inválido ou expirado.')
        return redirect(url_for('main.login'))
    uid = data.get('uid')
    new_email = (data.get('new_email') or '').strip()
    if not (uid and new_email):
        flash('Dados do token incompletos.')
        return redirect(url_for('main.login'))
    user = User.query.get(uid)
    if not user:
        flash('Usuárie não encontrade.')
        return redirect(url_for('main.login'))
    # Evita colidir com outro usuário que registrou este e-mail nesse meio tempo
    existente = User.query.filter(User.email == new_email, User.id != user.id).first()
    if existente:
        flash('Este e-mail já está em uso por outra conta.')
        return redirect(url_for('main.configuracoes'))
    user.email = new_email
    # Se o e-mail foi alterado, deve confirmar novamente
    try:
        user.email_confirmed = False
    except Exception:
        pass
    try:
        db.session.commit()
        flash('E-mail atualizado com sucesso! Faça login novamente se necessário.')
    except Exception as e:
        db.session.rollback()
        flash(f'Falha ao atualizar o e-mail: {e}')
    return redirect(url_for('main.configuracoes'))

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ...rotas principais...

# Rota para relatar post
@bp.route('/api/posts/<int:post_id>/relatar', methods=['POST'])
@login_required
def relatar_post(post_id):
    post = Post.query.get_or_404(post_id)
    # Não deixa relatar o próprio post
    if post.usuario == current_user.username:
        return jsonify({'error': 'Você não pode relatar seu próprio post.'}), 403
    # Verifica se já relatou
    ja_reportou = Report.query.filter_by(post_id=post_id, usuario_id=current_user.id).first()
    if ja_reportou:
        return jsonify({'error': 'Você já relatou este post.'}), 400
    payload = request.get_json(silent=True) or {}
    cat = (payload.get('category') or '').strip().lower() or None
    mot = (payload.get('motivo') or '').strip() or 'Relato via botão'
    report = Report(post_id=post_id, usuario_id=current_user.id, motivo=mot, category=cat)
    db.session.add(report)
    db.session.commit()
    return jsonify({'success': True})

# Painel admin para ver denúncias
@bp.route('/admin/denuncias')
@login_required
def admin_denuncias():
    if not getattr(current_user, 'is_admin', False):
        return 'Acesso restrito', 403
    denuncias = Report.query.order_by(Report.data.desc()).all()
    return render_template('admin/denuncias.html', denuncias=denuncias)

@bp.route('/admin/usuarios/<int:user_id>/ban', methods=['POST'])
@login_required
def admin_ban_user(user_id):
    if not (current_user.is_admin or getattr(current_user,'is_superadmin',False)):
        return 'Acesso restrito', 403
    u = User.query.get_or_404(user_id)
    u.is_banned = True
    u.banned_at = datetime.utcnow()
    u.suspended_until = None
    db.session.commit()
    return redirect(url_for('main.perfil', user_id=user_id))

@bp.route('/admin/usuarios/<int:user_id>/suspend', methods=['POST'])
@login_required
def admin_suspend_user(user_id):
    if not (current_user.is_admin or getattr(current_user,'is_superadmin',False)):
        return 'Acesso restrito', 403
    days = 7
    try:
        days = int(request.form.get('days') or 7)
    except Exception:
        days = 7
    u = User.query.get_or_404(user_id)
    u.is_banned = False
    u.suspended_until = datetime.utcnow() + timedelta(days=max(1, days))
    db.session.commit()
    return redirect(url_for('main.perfil', user_id=user_id))

@bp.route('/admin/denuncias/<int:report_id>/resolve', methods=['POST'])
@login_required
def admin_resolve_report(report_id):
    if not (current_user.is_admin or getattr(current_user,'is_superadmin',False)):
        return 'Acesso restrito', 403
    r = Report.query.get_or_404(report_id)
    r.resolved = True
    r.resolved_at = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('main.admin_denuncias'))

@bp.route('/')
@login_required
def index():
    """Página inicial com destaques dinâmicos.
    - Edu: divulgações curadas.
    - Trending: posts com mais likes últimos 7 dias.
    - Comentados: posts com mais comentários últimos 7 dias.
    """
    from sqlalchemy import func
    now = datetime.utcnow()
    window_ini = now - timedelta(days=7)

    # Divulgações curadas (admin) – sempre buscar frescos
    try:
        div_edu = (Divulgacao.query.filter_by(area='edu', ativo=True)
                   .filter(Divulgacao.show_on_index == True)
                   .order_by(Divulgacao.ordem.asc(), Divulgacao.created_at.desc())
                   .limit(6).all())
    except Exception:
        # Fallback caso coluna não exista ainda
        div_edu = (Divulgacao.query.filter_by(area='edu', ativo=True)
                   .order_by(Divulgacao.ordem.asc(), Divulgacao.created_at.desc())
                   .limit(6).all())
    # Removido fallback automático para EduContent: só mostra o que for publicado como Divulgacao

    # Subqueries para likes e comentários (Delu)
    likes_sub = (db.session.query(Post.id.label('pid'), func.count(post_likes.c.user_id).label('likes'))
                 .outerjoin(post_likes, post_likes.c.post_id == Post.id)
                 .filter(((Post.is_deleted == False) | (Post.is_deleted.is_(None))) & (Post.data >= window_ini))
                 .group_by(Post.id)
                 .subquery())
    comments_sub = (db.session.query(Comentario.post_id.label('pid'), func.count(Comentario.id).label('comments'))
                    .filter(Comentario.data >= window_ini)
                    .group_by(Comentario.post_id)
                    .subquery())

    # Trending por likes
    trending_posts = (db.session.query(Post, func.coalesce(likes_sub.c.likes, 0).label('lk'))
                      .outerjoin(likes_sub, likes_sub.c.pid == Post.id)
                      .filter(((Post.is_deleted == False) | (Post.is_deleted.is_(None))) & (Post.data >= window_ini))
                      .order_by(func.coalesce(likes_sub.c.likes, 0).desc(), Post.data.desc())
                      .limit(5)
                      .all())

    # Mais comentados
    commented_posts = (db.session.query(Post, func.coalesce(comments_sub.c.comments, 0).label('cm'))
                       .outerjoin(comments_sub, comments_sub.c.pid == Post.id)
                       .filter(((Post.is_deleted == False) | (Post.is_deleted.is_(None))) & (Post.data >= window_ini))
                       .order_by(func.coalesce(comments_sub.c.comments, 0).desc(), Post.data.desc())
                       .limit(5)
                       .all())

    def post_to_dict(p: Post, likes_count=0, comments_count=0):
        try:
            data_str = p.data.strftime('%d/%m %H:%M') if p.data else ''
        except Exception:
            data_str = ''
        texto = (p.conteudo or '').strip().replace('\n', ' ')
        excerpt = (texto[:80] + '…') if len(texto) > 80 else texto
        return {
            'id': p.id,
            'usuario': p.usuario or 'Usuárie',
            'excerpt': excerpt or '(sem texto)',
            'likes': likes_count,
            'comments': comments_count,
            'data': data_str
        }

    delu_trending = [post_to_dict(p, likes_count=lk) for p, lk in trending_posts]
    delu_commented = [post_to_dict(p, comments_count=cm) for p, cm in commented_posts]

    return render_template('index.html',
                           div_edu=div_edu,
                           delu_trending=delu_trending,
                           delu_commented=delu_commented)

# ------------------ Admin Divulgação ------------------
@bp.route('/admin/divulgacao')
@login_required
def admin_divulgacao_list():
    if not (current_user.is_admin or getattr(current_user,'is_superadmin',False)):
        return 'Acesso restrito', 403
    # Página dedicada removida: redireciona para o dashboard (aba Publi)
    return redirect(url_for('admin.dashboard') + '#publi')

@bp.route('/admin/divulgacao/new', methods=['POST'])
@login_required
def admin_divulgacao_new():
    if not (current_user.is_admin or getattr(current_user,'is_superadmin',False)):
        return jsonify({'error':'forbidden'}), 403
    data = request.form or request.json or {}
    # Se vier edu_content_id e não vier título/texto, tenta preencher automaticamente
    edu_content_id = data.get('edu_content_id') or None
    auto_titulo = data.get('titulo')
    auto_texto = data.get('texto')
    auto_link = data.get('link')
    if edu_content_id and (not auto_titulo or not auto_texto):
        try:
            ec = EduContent.query.get(int(edu_content_id))
            if ec:
                if not auto_titulo:
                    auto_titulo = ec.titulo
                if not auto_texto:
                    base = (ec.resumo or ec.corpo or '')
                    auto_texto = (base[:140] + '…') if len(base) > 140 else base
                if not auto_link:
                    auto_link = url_for('main.educacao')  # TODO: link específico por tipo futuramente
        except Exception:
            pass
    # Flags de destino (checkboxes opcionais) — suporta hidden + checkbox via getlist
    def _flag_multi(container, key, default):
        try:
            vals = container.getlist(key)
        except Exception:
            vals = []
        if not vals:
            v = container.get(key)
            if v is not None:
                vals = [v]
        if not vals:
            return default
        return any(str(x).lower() in ('1','true','on','yes') for x in vals)
    show_on_edu = _flag_multi(data, 'show_on_edu', True)
    show_on_index = _flag_multi(data, 'show_on_index', True)

    d = Divulgacao(
        # Área técnica padronizada em 'edu'; destino controlado por flags de exibição
        area='edu',
        titulo=auto_titulo or 'Sem título',
        texto=auto_texto or '',
        link=auto_link,
        imagem=data.get('imagem'),
        ordem=int(data.get('ordem') or 0),
        ativo=('ativo' in data and str(data.get('ativo')).lower() in ('1','true','on')) or True,
        show_on_edu=show_on_edu,
        show_on_index=show_on_index,
        edu_content_id=edu_content_id,
        post_id=data.get('post_id')
    )
    db.session.add(d)
    db.session.commit()
    return redirect(url_for('admin.dashboard') + '#publi')

@bp.route('/admin/divulgacao/<int:item_id>/update', methods=['POST'])
@login_required
def admin_divulgacao_update(item_id):
    if not (current_user.is_admin or getattr(current_user,'is_superadmin',False)):
        return 'Acesso restrito', 403
    d = Divulgacao.query.get_or_404(item_id)
    f = request.form or request.json or {}
    for field in ['titulo','texto','link','imagem']:
        if field in f and f.get(field) is not None:
            setattr(d, field, f.get(field))
    if 'ordem' in f:
        try: d.ordem = int(f.get('ordem'))
        except: pass
    if 'ativo' in f:
        d.ativo = str(f.get('ativo')).lower() in ('1','true','on')
    # Atualiza flags de destino (usar getlist para combinar hidden + checkbox)
    def _flag_multi(container, key, default):
        try:
            vals = container.getlist(key)
        except Exception:
            vals = []
        if not vals:
            v = container.get(key)
            if v is not None:
                vals = [v]
        if not vals:
            return default
        return any(str(x).lower() in ('1','true','on','yes') for x in vals)
    if 'show_on_edu' in f:
        d.show_on_edu = _flag_multi(f, 'show_on_edu', d.show_on_edu)
    if 'show_on_index' in f:
        d.show_on_index = _flag_multi(f, 'show_on_index', d.show_on_index)
    # campo show_on_lune descontinuado
    if 'edu_content_id' in f:
        d.edu_content_id = f.get('edu_content_id') or None
    if 'post_id' in f:
        d.post_id = f.get('post_id') or None
    db.session.commit()
    # Redireciona de volta se vier do dashboard (ou se 'next' for informado)
    try:
        nxt = (request.form.get('next') or request.referrer)
        if nxt:
            return redirect(nxt)
    except Exception:
        pass
    return redirect(url_for('main.admin_divulgacao_list'))

@bp.route('/admin/divulgacao/<int:item_id>/delete', methods=['POST'])
@login_required
def admin_divulgacao_delete(item_id):
    if not (current_user.is_admin or getattr(current_user,'is_superadmin',False)):
        return 'Acesso restrito', 403
    d = Divulgacao.query.get_or_404(item_id)
    db.session.delete(d)
    db.session.commit()
    try:
        nxt = (request.form.get('next') or request.referrer)
        if nxt:
            return redirect(nxt)
    except Exception:
        pass
    return redirect(url_for('admin.dashboard') + '#publi')

@bp.route('/admin/divulgacao/reorder', methods=['POST'])
@login_required
def admin_divulgacao_reorder():
    if not (current_user.is_admin or getattr(current_user,'is_superadmin',False)):
        return jsonify({'error':'forbidden'}), 403
    payload = request.get_json(silent=True) or {}
    items = payload.get('ordem') or []
    updated = 0
    for it in items:
        try:
            _id = int(it.get('id'))
            _ord = int(it.get('ordem'))
        except Exception:
            continue
        d = Divulgacao.query.get(_id)
        if not d:
            continue
        d.ordem = _ord
        updated += 1
    if updated:
        db.session.commit()
    return jsonify({'ok': True, 'updated': updated})

@bp.route('/admin/divulgacao/upload', methods=['POST'])
@login_required
def admin_divulgacao_upload():
    if not (current_user.is_admin or getattr(current_user,'is_superadmin',False)):
        return 'Acesso restrito', 403
    f = request.files.get('arquivo')
    if not f or not f.filename:
        flash('Nenhum arquivo enviado.')
        return redirect(url_for('admin.dashboard') + '#publi')
    import os, uuid
    ext = f.filename.rsplit('.',1)[-1].lower()
    if ext not in {'png','jpg','jpeg','webp','gif'}:
        flash('Extensão não permitida.')
        return redirect(url_for('admin.dashboard') + '#publi')
    # Limite simples de tamanho (2MB)
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(0)
    if size > 2 * 1024 * 1024:
        flash('Arquivo muito grande (máx 2MB).')
        return redirect(url_for('admin.dashboard') + '#publi')
    fname = f"div_{uuid.uuid4().hex[:10]}.{ext}"
    
    # Tenta upload para Supabase primeiro
    foto_bytes = f.read()
    f.seek(0)
    ctype, _ = guess_type(fname)
    remote_path = build_divulgacao_path(fname)
    public_url = upload_bytes_to_supabase(remote_path, foto_bytes, content_type=ctype or 'image/jpeg')
    
    if public_url:
        # Sucesso no Supabase - usa URL pública
        flash('Upload concluído.')
        session['last_divulgacao_image'] = public_url
        return redirect(url_for('admin.dashboard') + '#publi')
    else:
        # Fallback: salvar localmente (pode não funcionar em serverless)
        target_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'divulgacao')
        os.makedirs(target_dir, exist_ok=True)
        f.save(os.path.join(target_dir, fname))
        flash('Upload concluído.')
        # Devolve caminho relativo para uso rápido
        session['last_divulgacao_image'] = f"uploads/divulgacao/{fname}"
        return redirect(url_for('admin.dashboard') + '#publi')

@bp.route('/admin/divulgacao/aviso_rapido', methods=['POST'])
@login_required
def admin_divulgacao_aviso_rapido():
    """Cria uma Divulgação rápida a partir de título+mensagem gerando uma imagem simples com o texto.
    Campos: titulo, mensagem. Área é fixada em 'edu'.
    """
    if not (current_user.is_admin or getattr(current_user,'is_superadmin',False)):
        return 'Acesso restrito', 403
    titulo = (request.form.get('titulo') or '').strip()
    mensagem = (request.form.get('mensagem') or '').strip()
    # Área fixada em 'edu' — destinos são controlados pelos flags Exibir em
    area = 'edu'
    if not titulo and not mensagem:
        flash('Informe um título ou uma mensagem para o aviso.')
        return redirect(request.referrer or url_for('admin.dashboard'))
    # Gera imagem simples com Pillow
    try:
        from PIL import Image, ImageDraw, ImageFont
        import os, uuid, textwrap
        W, H = 1000, 500
        bg = (155, 93, 229)  # #9B5DE5
        fg = (255, 255, 255)
        im = Image.new('RGB', (W, H), color=bg)
        draw = ImageDraw.Draw(im)
        # Carrega fonte padrão (fallback)
        try:
            font_title = ImageFont.truetype("arial.ttf", 48)
            font_body = ImageFont.truetype("arial.ttf", 32)
        except Exception:
            font_title = ImageFont.load_default()
            font_body = ImageFont.load_default()
        # Texto com wrap
        maxw_title = W - 120
        maxw_body = W - 140
        lines_title = textwrap.wrap(titulo or '', width=24)[:2]
        lines_body = textwrap.wrap(mensagem or '', width=36)[:6]
        y = 70
        for lt in lines_title:
            bbox = draw.textbbox((0,0), lt, font=font_title)
            tw = bbox[2]-bbox[0]
            draw.text(((W-tw)//2, y), lt, fill=fg, font=font_title)
            y += (bbox[3]-bbox[1]) + 8
        y += 10
        for lb in lines_body:
            bbox = draw.textbbox((0,0), lb, font=font_body)
            tw = bbox[2]-bbox[0]
            draw.text(((W-tw)//2, y), lb, fill=fg, font=font_body)
            y += (bbox[3]-bbox[1]) + 4
        # Marca d'água simples
        wm = "gramatike.com.br"
        try:
            font_wm = ImageFont.truetype("arial.ttf", 18)
        except Exception:
            font_wm = ImageFont.load_default()
        wb = draw.textbbox((0,0), wm, font=font_wm)
        draw.text((W-wb[2]-24, H-wb[3]-20), wm, fill=(240,240,240), font=font_wm)
        # Salva - tenta Supabase primeiro
        fname = f"aviso_{uuid.uuid4().hex[:10]}.png"
        from io import BytesIO
        buffer = BytesIO()
        im.save(buffer, format='PNG')
        buffer.seek(0)
        
        remote_path = build_divulgacao_path(fname)
        public_url = upload_bytes_to_supabase(remote_path, buffer.read(), content_type='image/png')
        
        if public_url:
            # Sucesso no Supabase - usa URL pública
            rel = public_url
        else:
            # Fallback: salvar localmente (pode não funcionar em serverless)
            target_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'divulgacao')
            os.makedirs(target_dir, exist_ok=True)
            path = os.path.join(target_dir, fname)
            im.save(path, format='PNG')
            rel = f"uploads/divulgacao/{fname}"
    except Exception as e:
        current_app.logger.warning(f"falha ao gerar imagem do aviso: {e}")
        rel = None
    # Cria a divulgação
    # Flags de destino — suporta hidden + checkbox via getlist
    def _flag_multi(container, key, default):
        try:
            vals = container.getlist(key)
        except Exception:
            vals = []
        if not vals:
            v = container.get(key)
            if v is not None:
                vals = [v]
        if not vals:
            return default
        return any(str(x).lower() in ('1','true','on','yes') for x in vals)
    show_on_edu = _flag_multi(request.form, 'show_on_edu', True)
    show_on_index = _flag_multi(request.form, 'show_on_index', True)
    # show_on_lune removido

    d = Divulgacao(
        area=area,
        titulo=titulo or 'Aviso',
        texto=mensagem or '',
        link=None,
        imagem=rel,
        ordem=0,
        ativo=True,
        show_on_edu=show_on_edu,
        show_on_index=show_on_index,
    # show_on_lune removido
    )
    db.session.add(d)
    db.session.commit()
    # Volta ao painel (aba Publi)
    try:
        nxt = request.form.get('next') or request.referrer
        if nxt:
            return redirect(nxt)
    except Exception:
        pass
    return redirect(url_for('admin.dashboard'))

@bp.route('/admin/educontent/search')
@login_required
def admin_educontent_search():
    if not (current_user.is_admin or getattr(current_user,'is_superadmin',False)):
        return jsonify([])
    q = (request.args.get('q') or '').strip()
    query = EduContent.query
    if q:
        like = f"%{q}%"
        from sqlalchemy import or_
        query = query.filter(or_(EduContent.titulo.ilike(like), EduContent.resumo.ilike(like)))
    items = (query.order_by(EduContent.created_at.desc()).limit(15).all())
    out = []
    for c in items:
        base = (c.resumo or c.corpo or '')
        prev = (base[:120] + '…') if len(base) > 120 else base
        out.append({'id': c.id, 'titulo': c.titulo, 'tipo': c.tipo, 'preview': prev})
    return jsonify(out)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ident = (request.form.get('email') or '').strip()
        pwd = request.form.get('password') or ''
        from sqlalchemy import or_
        user = User.query.filter(or_(User.email == ident, User.username == ident)).first()
        # Verifica via hash seguro
        if user and user.check_password(pwd):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Login inválido.')
    return render_template('login.html')

@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    # Clear any pending flash messages before redirecting to login
    session.pop('_flashes', None)
    return redirect(url_for('main.login'))

@bp.route('/educacao')
def educacao():
    # Divulgações EDU ativas (inclui avisos rápidos) — somente marcadas para Educação
    try:
        divulgacoes = (Divulgacao.query.filter_by(area='edu', ativo=True)
                        .filter(Divulgacao.show_on_edu == True)
                        .order_by(Divulgacao.ordem.asc(), Divulgacao.created_at.desc())
                        .limit(10).all())
    except Exception:
        # Fallback caso coluna não exista ainda
        try:
            divulgacoes = (Divulgacao.query.filter_by(area='edu', ativo=True)
                            .order_by(Divulgacao.ordem.asc(), Divulgacao.created_at.desc())
                            .limit(10).all())
        except Exception:
            divulgacoes = []
    # Garante tabela e seed inicial se necessário
    _ensure_edunovidade_table(seed=True)
    try:
        novidades = EduNovidade.query.order_by(EduNovidade.created_at.desc()).limit(5).all()
    except Exception:
        novidades = []
    # Fallback: se não houver novidade cadastrada, tenta carregar o EduContent do Guia Básico
    if not novidades:
        try:
            from gramatike_app.models import EduContent
            guia = (EduContent.query
                    .filter(EduContent.titulo.ilike('%guia básico de gênero neutro%'))
                    .order_by(EduContent.created_at.desc())
                    .first())
            if guia:
                # Criamos um objeto simples compatível com o template
                from types import SimpleNamespace
                novidades = [SimpleNamespace(
                    titulo=guia.titulo,
                    descricao=(guia.resumo or (guia.corpo[:160] + ('…' if guia.corpo and len(guia.corpo)>160 else '')) if guia.corpo else ''),
                    link=guia.url,
                    created_at=guia.created_at
                )]
        except Exception as _e:
            pass
    return render_template('gramatike_edu.html', generated_at=datetime.utcnow(), novidades=novidades, divulgacoes=divulgacoes)

# Dinâmicas (criação) — por enquanto apenas admin
@bp.route('/dinamicas')
def dinamicas_home():
    is_admin = getattr(current_user, 'is_authenticated', False) and (getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_superadmin', False))
    my_dynamics = []
    if is_admin and getattr(current_user, 'is_authenticated', False):
        try:
            my_dynamics = Dynamic.query.filter_by(created_by=current_user.id).order_by(Dynamic.created_at.desc()).all()
        except Exception as _e:
            current_app.logger.warning(f"load my_dynamics failed: {_e}")
            my_dynamics = []
    return render_template('dinamicas.html', is_admin=is_admin, my_dynamics=my_dynamics)

@bp.route('/dinamicas/create', methods=['POST'])
@login_required
def dinamicas_create():
    if not (current_user.is_admin or getattr(current_user, 'is_superadmin', False)):
        flash('Apenas administradores podem criar dinâmicas.')
        return redirect(url_for('main.dinamicas_home'))
    tipo = (request.form.get('tipo') or '').strip().lower()
    titulo = (request.form.get('titulo') or '').strip()
    descricao = (request.form.get('descricao') or '').strip() or None
    import json as _json
    cfg = {}
    if tipo == 'poll':
        raw_opts = (request.form.get('opcoes') or '').strip()
        opts = [o.strip() for o in raw_opts.split('\n') if o.strip()]
        if len(opts) < 2:
            flash('Informe pelo menos duas opções para a enquete.')
            return redirect(url_for('main.dinamicas_home'))
        cfg['options'] = opts
    elif tipo == 'oneword':
        # sem config necessária
        pass
    elif tipo == 'form':
        # Suporta builder: config_json com { fields: [ {id,type,label,required,options?} ] }
        try:
            cfg_json = request.form.get('config_json')
            if cfg_json:
                parsed = _json.loads(cfg_json)
                # validação simples
                fields = parsed.get('fields') or []
                if not fields:
                    flash('Adicione pelo menos uma pergunta no formulário.')
                    return redirect(url_for('main.dinamicas_home'))
                # normalizar
                norm = []
                for q in fields:
                    qtype = (q.get('type') or 'short').lower()
                    if qtype not in ('short','paragraph','multiple_choice'):
                        qtype = 'short'
                    item = {
                        'id': int(q.get('id') or 0),
                        'type': qtype,
                        'label': (q.get('label') or '').strip(),
                        'required': bool(q.get('required'))
                    }
                    if qtype == 'multiple_choice':
                        opts = [str(o).strip() for o in (q.get('options') or []) if str(o).strip()]
                        if len(opts) < 2:
                            flash('Cada múltipla escolha precisa de pelo menos 2 opções.')
                            return redirect(url_for('main.dinamicas_home'))
                        item['options'] = opts
                    norm.append(item)
                cfg['fields'] = norm
            else:
                # fallback simples
                cfg['fields'] = [{'id':1,'type':'paragraph','label':'Resposta','required':True}]
        except Exception as _e:
            flash('Configuração inválida do formulário.')
            return redirect(url_for('main.dinamicas_home'))
    else:
        flash('Tipo inválido.')
        return redirect(url_for('main.dinamicas_home'))
    if not titulo:
        flash('Título é obrigatório.')
        return redirect(url_for('main.dinamicas_home'))
    d = Dynamic(tipo=tipo, titulo=titulo, descricao=descricao, config=_json.dumps(cfg) if cfg else None, created_by=current_user.id)
    db.session.add(d)
    db.session.commit()
    flash('Dinâmica criada.')
    return redirect(url_for('main.dinamicas_home'))

@bp.route('/dinamicas/<int:dyn_id>')
def dinamica_view(dyn_id: int):
    d = Dynamic.query.get_or_404(dyn_id)
    # Parse config
    import json as _json
    try:
        cfg = _json.loads(d.config) if d.config else {}
    except Exception:
        cfg = {}
    
    # Check if current user has already responded (only if authenticated)
    user_response = None
    if getattr(current_user, 'is_authenticated', False):
        prev = DynamicResponse.query.filter_by(dynamic_id=d.id, usuario_id=current_user.id).first()
        if prev:
            try:
                user_response = _json.loads(prev.payload) if prev.payload else {}
            except Exception:
                pass
    
    # Coletar agregados simples para oneword e poll
    agg = {}
    if d.tipo == 'oneword':
        # contar palavras (case-insensitive)
        from collections import Counter
        words = []
        
        for r in d.responses:
            try:
                pr = _json.loads(r.payload) if r.payload else {}
                # Collect word1, word2, word3
                for key in ['word1', 'word2', 'word3']:
                    w = (pr.get(key) or '').strip()
                    if w:
                        w_lower = w.lower()
                        words.append(w_lower)
                # For backwards compatibility with old 'word' format
                w = (pr.get('word') or '').strip()
                if w:
                    w_lower = w.lower()
                    words.append(w_lower)
            except Exception:
                pass
        agg['counts'] = Counter(words)
    elif d.tipo == 'poll':
        counts = []
        options = cfg.get('options') or []
        for _ in options:
            counts.append(0)
        for r in d.responses:
            try:
                pr = _json.loads(r.payload) if r.payload else {}
                idx = int(pr.get('option'))
                if 0 <= idx < len(options):
                    counts[idx] += 1
            except Exception:
                pass
        agg['counts'] = counts
    return render_template('dinamica_view.html', d=d, cfg=cfg, agg=agg, user_response=user_response)

@bp.route('/dinamicas/<int:dyn_id>/admin')
@login_required
def dinamica_admin(dyn_id: int):
    # Somente admin/superadmin
    if not (getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_superadmin', False)):
        abort(403)
    d = Dynamic.query.get_or_404(dyn_id)
    import json as _json
    try:
        cfg = _json.loads(d.config) if d.config else {}
    except Exception:
        cfg = {}
    # Carregar respostas com dados de usuário
    from gramatike_app.models import User
    rows = []
    for r in d.responses:
        try:
            payload = _json.loads(r.payload) if r.payload else {}
        except Exception:
            payload = {}
        u = User.query.get(r.usuario_id)
        rows.append({
            'id': r.id,
            'user': {'id': u.id if u else None, 'username': u.username if u else 'desconhecide', 'nome': u.nome if u else ''},
            'created_at': r.created_at,
            'payload': payload
        })
    # Agregados simples
    agg = {}
    if d.tipo == 'oneword':
        from collections import Counter
        words = []
        for row in rows:
            # Collect word1, word2, word3
            for key in ['word1', 'word2', 'word3']:
                w = (row['payload'].get(key) or '').strip().lower()
                if w:
                    words.append(w)
            # For backwards compatibility with old 'word' format
            w = (row['payload'].get('word') or '').strip().lower()
            if w:
                words.append(w)
        agg['counts'] = Counter(words)
    elif d.tipo == 'poll':
        counts = [0 for _ in (cfg.get('options') or [])]
        for row in rows:
            try:
                idx = int(row['payload'].get('option'))
                if 0 <= idx < len(counts):
                    counts[idx] += 1
            except Exception:
                pass
        agg['counts'] = counts
    return render_template('dinamica_admin.html', d=d, cfg=cfg, rows=rows, agg=agg)

@bp.route('/dinamicas/<int:dyn_id>/export.csv')
@login_required
def dinamica_export_csv(dyn_id: int):
    if not (getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_superadmin', False)):
        abort(403)
    d = Dynamic.query.get_or_404(dyn_id)
    # Tenta servir o arquivo existente; se não existir, gera on-the-fly
    import os, csv, io, json as _json
    base_dir = getattr(current_app, 'instance_path', None) or os.path.join(current_app.root_path, 'instance')
    target_dir = os.path.join(base_dir, 'dynamics')
    csv_path = os.path.join(target_dir, f"dyn_{d.id}.csv")
    try:
        if os.path.exists(csv_path):
            return send_file(csv_path, as_attachment=True, download_name=f"dinamica_{d.id}.csv")
    except Exception:
        pass
    # gerar CSV na memória
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['timestamp','dynamic_id','usuario_id','tipo','content'])
    cfg = {}
    try:
        cfg = _json.loads(d.config) if d.config else {}
    except Exception:
        cfg = {}
    by_id = {str(q.get('id')): q for q in (cfg.get('fields') or [])}
    for r in d.responses:
        try:
            payload = _json.loads(r.payload) if r.payload else {}
        except Exception:
            payload = {}
        content = ''
        if d.tipo == 'oneword':
            word1 = payload.get('word1', '')
            word2 = payload.get('word2', '')
            word3 = payload.get('word3', '')
            # For backwards compatibility
            old_word = payload.get('word', '')
            if old_word:
                content = old_word
            else:
                parts = [word1]
                if word2:
                    parts.append(word2)
                if word3:
                    parts.append(word3)
                content = ', '.join(parts)
        elif d.tipo == 'poll':
            opts = (cfg.get('options') or [])
            idx = payload.get('option')
            text = opts[idx] if isinstance(idx, int) and 0 <= idx < len(opts) else ''
            content = f"option_index={idx}; option_text={text}"
        else:
            parts = []
            for ans in (payload.get('answers') or []):
                q = by_id.get(str(ans.get('id')))
                label = (q.get('label') if q else f"q{ans.get('id')}") or f"q{ans.get('id')}"
                val = ans.get('value') or ''
                parts.append(f"{label}={val}")
            content = ' | '.join(parts)
        writer.writerow([getattr(r.created_at,'isoformat',lambda: '')(), d.id, r.usuario_id, d.tipo, content])
    output.seek(0)
    return Response(output.read(), mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename=dinamica_{d.id}.csv'})

@bp.route('/dinamicas/<int:dyn_id>/toggle-active', methods=['POST'])
@login_required
def dinamica_toggle_active(dyn_id: int):
    if not (getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_superadmin', False)):
        flash('Apenas administradores podem alterar dinâmicas.')
        return redirect(url_for('main.dinamicas_home'))
    d = Dynamic.query.get_or_404(dyn_id)
    if d.created_by != current_user.id:
        flash('Você só pode alterar suas próprias dinâmicas.')
        return redirect(url_for('main.dinamicas_home'))
    d.active = not d.active
    db.session.commit()
    status = 'ativada' if d.active else 'finalizada'
    flash(f'Dinâmica {status} com sucesso!')
    return redirect(url_for('main.dinamicas_home'))

@bp.route('/dinamicas/<int:dyn_id>/delete', methods=['POST'])
@login_required
def dinamica_delete(dyn_id: int):
    if not (getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_superadmin', False)):
        flash('Apenas administradores podem excluir dinâmicas.')
        return redirect(url_for('main.dinamicas_home'))
    d = Dynamic.query.get_or_404(dyn_id)
    if d.created_by != current_user.id:
        flash('Você só pode excluir suas próprias dinâmicas.')
        return redirect(url_for('main.dinamicas_home'))
    
    # Delete all responses first (cascade)
    DynamicResponse.query.filter_by(dynamic_id=d.id).delete()
    
    # Delete the dynamic
    db.session.delete(d)
    db.session.commit()
    
    flash('Dinâmica excluída com sucesso!')
    return redirect(url_for('main.dinamicas_home'))

@bp.route('/dinamicas/<int:dyn_id>/edit', methods=['GET'])
@login_required
def dinamica_edit(dyn_id: int):
    if not (getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_superadmin', False)):
        flash('Apenas administradores podem editar dinâmicas.')
        return redirect(url_for('main.dinamicas_home'))
    d = Dynamic.query.get_or_404(dyn_id)
    if d.created_by != current_user.id:
        flash('Você só pode editar suas próprias dinâmicas.')
        return redirect(url_for('main.dinamicas_home'))
    import json as _json
    cfg = {}
    try:
        cfg = _json.loads(d.config) if d.config else {}
    except Exception:
        cfg = {}
    return render_template('dinamica_edit.html', d=d, cfg=cfg)

@bp.route('/dinamicas/<int:dyn_id>/update', methods=['POST'])
@login_required
def dinamica_update(dyn_id: int):
    if not (getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_superadmin', False)):
        flash('Apenas administradores podem editar dinâmicas.')
        return redirect(url_for('main.dinamicas_home'))
    d = Dynamic.query.get_or_404(dyn_id)
    if d.created_by != current_user.id:
        flash('Você só pode editar suas próprias dinâmicas.')
        return redirect(url_for('main.dinamicas_home'))
    
    titulo = (request.form.get('titulo') or '').strip()
    descricao = (request.form.get('descricao') or '').strip() or None
    
    if not titulo:
        flash('Título é obrigatório.')
        return redirect(url_for('main.dinamica_edit', dyn_id=d.id))
    
    import json as _json
    cfg = {}
    
    # Atualizar configuração baseada no tipo
    if d.tipo == 'poll':
        raw_opts = (request.form.get('opcoes') or '').strip()
        opts = [o.strip() for o in raw_opts.split('\n') if o.strip()]
        if len(opts) < 2:
            flash('Informe pelo menos duas opções para a enquete.')
            return redirect(url_for('main.dinamica_edit', dyn_id=d.id))
        cfg['options'] = opts
    elif d.tipo == 'oneword':
        # sem config necessária
        pass
    elif d.tipo == 'form':
        try:
            cfg_json = request.form.get('config_json')
            if cfg_json:
                parsed = _json.loads(cfg_json)
                fields = parsed.get('fields') or []
                if not fields:
                    flash('Adicione pelo menos uma pergunta no formulário.')
                    return redirect(url_for('main.dinamica_edit', dyn_id=d.id))
                norm = []
                for q in fields:
                    qtype = (q.get('type') or 'short').lower()
                    if qtype not in ('short','paragraph','multiple_choice'):
                        qtype = 'short'
                    item = {
                        'id': int(q.get('id') or 0),
                        'type': qtype,
                        'label': (q.get('label') or '').strip(),
                        'required': bool(q.get('required'))
                    }
                    if qtype == 'multiple_choice':
                        opts = [str(o).strip() for o in (q.get('options') or []) if str(o).strip()]
                        if len(opts) < 2:
                            flash('Cada múltipla escolha precisa de pelo menos 2 opções.')
                            return redirect(url_for('main.dinamica_edit', dyn_id=d.id))
                        item['options'] = opts
                    norm.append(item)
                cfg['fields'] = norm
            else:
                # manter config existente
                try:
                    cfg = _json.loads(d.config) if d.config else {}
                except Exception:
                    cfg = {}
        except Exception as _e:
            flash('Configuração inválida do formulário.')
            return redirect(url_for('main.dinamica_edit', dyn_id=d.id))
    
    d.titulo = titulo
    d.descricao = descricao
    d.config = _json.dumps(cfg) if cfg else None
    db.session.commit()
    flash('Dinâmica atualizada com sucesso!')
    return redirect(url_for('main.dinamicas_home'))

@bp.route('/dinamicas/<int:dyn_id>/responder', methods=['POST'])
@login_required
def dinamica_responder(dyn_id: int):
    d = Dynamic.query.get_or_404(dyn_id)
    import json as _json
    payload = {}
    # Impedir múltiplas respostas por usuárie
    prev = DynamicResponse.query.filter_by(dynamic_id=d.id, usuario_id=current_user.id).first()
    if prev:
        flash('Você já respondeu esta dinâmica.')
        return redirect(url_for('main.dinamica_view', dyn_id=d.id))
    if d.tipo == 'oneword':
        word1 = (request.form.get('word1') or '').strip()
        word2 = (request.form.get('word2') or '').strip()
        word3 = (request.form.get('word3') or '').strip()
        
        if not word1:
            flash('Informe pelo menos a primeira palavra.')
            return redirect(url_for('main.dinamica_view', dyn_id=d.id))
        
        # Validate each word (allow compound words, but limit length)
        if len(word1) > 50:
            flash('Palavra 1 muito longa (máx 50 caracteres).')
            return redirect(url_for('main.dinamica_view', dyn_id=d.id))
        if word2 and len(word2) > 50:
            flash('Palavra 2 muito longa (máx 50 caracteres).')
            return redirect(url_for('main.dinamica_view', dyn_id=d.id))
        if word3 and len(word3) > 50:
            flash('Palavra 3 muito longa (máx 50 caracteres).')
            return redirect(url_for('main.dinamica_view', dyn_id=d.id))
        
        payload['word1'] = word1
        if word2:
            payload['word2'] = word2
        if word3:
            payload['word3'] = word3
    elif d.tipo == 'poll':
        try:
            idx = int(request.form.get('option'))
        except Exception:
            flash('Selecione uma opção.')
            return redirect(url_for('main.dinamica_view', dyn_id=d.id))
        # validar com base no config
        try:
            cfg = _json.loads(d.config) if d.config else {}
        except Exception:
            cfg = {}
        options = cfg.get('options') or []
        if not (0 <= idx < len(options)):
            flash('Opção inválida.')
            return redirect(url_for('main.dinamica_view', dyn_id=d.id))
        payload['option'] = idx
    elif d.tipo == 'form':
        # Construir payload com base nas fields do config
        try:
            cfg = _json.loads(d.config) if d.config else {}
        except Exception:
            cfg = {}
        fields = cfg.get('fields') or []
        answers = []
        for q in fields:
            qid = str(q.get('id'))
            qtype = q.get('type')
            key = f"q_{qid}"
            val = (request.form.get(key) or '').strip()
            if q.get('required') and not val:
                flash('Preencha as perguntas obrigatórias.')
                return redirect(url_for('main.dinamica_view', dyn_id=d.id))
            answers.append({'id': q.get('id'), 'type': qtype, 'value': val})
        payload['answers'] = answers
    else:
        flash('Tipo não suportado.')
        return redirect(url_for('main.dinamica_view', dyn_id=d.id))
    dr = DynamicResponse(dynamic_id=d.id, usuario_id=current_user.id, payload=_json.dumps(payload))
    db.session.add(dr)
    db.session.commit()
    # Salvar também em CSV por dinâmica ("planilha")
    try:
        import os, csv, datetime as _dt
        from flask import current_app as _app
        base_dir = getattr(_app, 'instance_path', None) or os.path.join(_app.root_path, 'instance')
        target_dir = os.path.join(base_dir, 'dynamics')
        os.makedirs(target_dir, exist_ok=True)
        csv_path = os.path.join(target_dir, f"dyn_{d.id}.csv")
        exists = os.path.exists(csv_path)
        with open(csv_path, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if not exists:
                writer.writerow(['timestamp','dynamic_id','usuario_id','tipo','content'])
            try:
                from zoneinfo import ZoneInfo
                stamp = _to_brasilia(_dt.datetime.utcnow()).isoformat()
            except Exception:
                stamp = _dt.datetime.utcnow().isoformat()
            # Montar conteúdo human-readable
            content = ''
            if d.tipo == 'oneword':
                word1 = payload.get('word1', '')
                word2 = payload.get('word2', '')
                word3 = payload.get('word3', '')
                # For backwards compatibility
                old_word = payload.get('word', '')
                if old_word:
                    content = old_word
                else:
                    parts = [word1]
                    if word2:
                        parts.append(word2)
                    if word3:
                        parts.append(word3)
                    content = ', '.join(parts)
            elif d.tipo == 'poll':
                try:
                    cfg = _json.loads(d.config) if d.config else {}
                except Exception:
                    cfg = {}
                opts = cfg.get('options') or []
                idx = payload.get('option')
                text = opts[idx] if isinstance(idx, int) and 0 <= idx < len(opts) else ''
                content = f"option_index={idx}; option_text={text}"
            else:
                # para forms, montar string com pares label=valor
                try:
                    cfg = _json.loads(d.config) if d.config else {}
                except Exception:
                    cfg = {}
                by_id = {}
                for q in (cfg.get('fields') or []):
                    by_id[str(q.get('id'))] = q
                parts = []
                for ans in (payload.get('answers') or []):
                    q = by_id.get(str(ans.get('id')))
                    label = (q.get('label') if q else f"q{ans.get('id')}") or f"q{ans.get('id')}"
                    val = ans.get('value') or ''
                    parts.append(f"{label}={val}")
                content = ' | '.join(parts)
            writer.writerow([stamp, d.id, current_user.id, d.tipo, content])
    except Exception as _csverr:
        current_app.logger.warning(f"CSV write failed for dynamic {d.id}: {_csverr}")
    flash('Resposta registrada!')
    return redirect(url_for('main.dinamica_view', dyn_id=d.id))

@bp.route('/estudos')
def estudos_legacy():
    # Compat: redireciona para a nova rota
    return redirect(url_for('main.educacao'))

@bp.route('/api/novidades')
def api_novidades():
    rows = EduNovidade.query.order_by(EduNovidade.created_at.desc()).limit(10).all()
    out = []
    for r in rows:
        out.append({
            'id': r.id,
            'titulo': r.titulo,
            'descricao': r.descricao,
            'link': r.link,
            'created_at': r.created_at.isoformat() if r.created_at else None
        })
    
    return jsonify({'items': out})

@bp.route('/novidade/<int:novidade_id>')
def novidade_detail(novidade_id):
    n = EduNovidade.query.get_or_404(novidade_id)
    is_admin = getattr(current_user, 'is_authenticated', False) and (
        getattr(current_user, 'is_admin', False) or 
        getattr(current_user, 'is_superadmin', False)
    )
    return render_template('novidade_detail.html', novidade=n, is_admin=is_admin)

## (Rotas Lune e legacy /delu removidas)

@bp.route('/novo_post')
@login_required
def novo_post():
    return render_template('criar_post.html')

@bp.route('/api/posts', methods=['GET'])
def api_posts_list():
    # Delegamos para a rota completa get_posts (definida abaixo) para evitar duplicação
    return get_posts()

@bp.route('/post/<int:post_id>')
def post_detail(post_id: int):
    p = Post.query.get_or_404(post_id)
    # Converter imagens em lista
    images = []
    if p.imagem:
        images = [seg for seg in (p.imagem or '').split('|') if seg]
    return render_template('post_detail.html', post=p, images=images)

@bp.route('/api/posts_multi', methods=['POST'])
@login_required
def api_posts_multi_create():
    import os, uuid
    from PIL import Image
    from io import BytesIO
    conteudo = (request.form.get('conteudo') or '').strip()
    if not conteudo:
        return jsonify({'success': False, 'error': 'conteudo_vazio'}), 400
    
    # Moderação de conteúdo
    ok, cat, matched_word = check_text(conteudo)
    if not ok:
        return jsonify({'error': 'conteudo_bloqueado', 'reason': cat, 'message': refusal_message_pt(cat, matched_word)}), 400
    
    files = request.files.getlist('imagens') if 'imagens' in request.files else []
    paths = []
    meta = []
    for idx, f in enumerate(files[:4]):
        if not f or not f.filename: continue
        ext = f.filename.rsplit('.',1)[-1].lower()
        if ext not in {'png','jpg','jpeg','webp','gif'}: continue
        f.seek(0, os.SEEK_END); size = f.tell(); f.seek(0)
        if size > 3 * 1024 * 1024: continue
        fname = f"post_{uuid.uuid4().hex[:10]}.{ext}"
        
        # Tenta upload para Supabase primeiro
        foto_bytes = f.read()
        f.seek(0)
        ctype, _ = guess_type(fname)
        remote_path = build_post_image_path(current_user.id, fname)
        public_url = upload_bytes_to_supabase(remote_path, foto_bytes, content_type=ctype or 'image/jpeg')
        
        if public_url:
            # Sucesso no Supabase - usa URL pública
            # Tenta extrair dimensões da imagem
            try:
                with Image.open(BytesIO(foto_bytes)) as im:
                    w, h = im.size
            except Exception:
                w = h = None
            paths.append(public_url)
            meta.append({'path': public_url, 'w': w, 'h': h})
        else:
            # Fallback: salvar localmente (pode não funcionar em serverless)
            target_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'posts')
            os.makedirs(target_dir, exist_ok=True)
            full_path = os.path.join(target_dir, fname)
            f.save(full_path)
            try:
                with Image.open(full_path) as im:
                    w, h = im.size
            except Exception:
                w = h = None
            rel = f"uploads/posts/{fname}"
            paths.append(rel)
            meta.append({'path': rel, 'w': w, 'h': h})
    post = Post(
        usuario=current_user.username,
        usuario_id=current_user.id,
        conteudo=conteudo,
        imagem='|'.join(paths),
        data=datetime.utcnow()
    )
    db.session.add(post)
    db.session.flush()
    for i,m in enumerate(meta):
        db.session.add(PostImage(post_id=post.id, path=m['path'], ordem=i, width=m['w'], height=m['h']))
    db.session.commit()
    return jsonify({'success': True, 'id': post.id, 'imagens': paths}), 201

## Rotas legacy de criação rápida removidas: /nova_postagem e /postar_estudo (agora gerenciadas pelo painel admin)

@bp.route('/apostilas')
def apostilas():
    q = request.args.get('q','').strip()
    topic_id = request.args.get('topic_id','').strip()
    page = max(int(request.args.get('page', 1) or 1), 1)
    per_page = 9
    query = EduContent.query.filter_by(tipo='apostila')
    if topic_id:
        query = query.filter_by(topic_id=int(topic_id))
    if q:
        from sqlalchemy import or_
        like = f"%{q}%"
        query = query.filter(or_(EduContent.titulo.ilike(like), EduContent.resumo.ilike(like)))
    total = query.count()
    conteudos = (query.order_by(EduContent.created_at.desc())
                      .offset((page-1)*per_page)
                      .limit(per_page)
                      .all())
    topics = EduTopic.query.filter_by(area='apostila').order_by(EduTopic.nome.asc()).all()
    last_page = (total + per_page - 1)//per_page
    return render_template('apostilas.html', conteudos=conteudos, topics=topics, q=q, topic_id=topic_id,
                           page=page, last_page=last_page, total=total, per_page=per_page)

@bp.route('/artigos')
def artigos():
    q = request.args.get('q','').strip()
    topic_id = request.args.get('topic_id','').strip()
    page = max(int(request.args.get('page', 1) or 1), 1)
    per_page = 9
    from sqlalchemy import or_
    query = EduContent.query.filter(EduContent.tipo=='artigo')
    if topic_id:
        query = query.filter_by(topic_id=int(topic_id))
    if q:
        like = f"%{q}%"
        query = query.filter(or_(EduContent.titulo.ilike(like), EduContent.resumo.ilike(like)))
    total = query.count()
    query = query.order_by(EduContent.created_at.desc())  # ordena mais recentes primeiro
    conteudos = (query.offset((page-1)*per_page)
                      .limit(per_page)
                      .all())
    topics = EduTopic.query.filter_by(area='artigo').order_by(EduTopic.nome.asc()).all()
    last_page = (total + per_page - 1)//per_page
    return render_template('artigos.html', conteudos=conteudos, topics=topics, q=q, topic_id=topic_id,
                           page=page, last_page=last_page, total=total, per_page=per_page)

@bp.route('/podcasts')
def podcasts():
    # Temporariamente desativado
    return render_template('maintenance.html', section='Podcasts'), 503

@bp.route('/redacao')
def redacao():
    # Temporariamente desativado
    return render_template('maintenance.html', section='Redação'), 503

@bp.route('/api/redacao/temas')
def api_redacao_temas():
    temas = EduContent.query.filter_by(tipo='redacao_tema').order_by(EduContent.created_at.desc()).all()
    result = [
        {
            'id': t.id,
            'titulo': t.titulo,
            'resumo': t.resumo,
            'corpo': t.corpo,
            'created_at': t.created_at.strftime('%Y-%m-%d %H:%M') if t.created_at else None
        } for t in temas
    ]
    
    return jsonify(result)

@bp.route('/exercicios')
def exercicios():
    q = request.args.get('q','').strip()
    topics = ExerciseTopic.query.order_by(ExerciseTopic.nome.asc()).all()
    # Carrega seções e questões por tópico
    data = []  # cada item: {topic, sections:[{section, questions}], unsectioned:[questions]} 
    from sqlalchemy import or_
    like = f"%{q}%" if q else None
    for t in topics:
        sections = ExerciseSection.query.filter_by(topic_id=t.id).order_by(ExerciseSection.ordem.asc(), ExerciseSection.nome.asc()).all()
        section_blocks = []
        for s in sections:
            q_query = s.questions.order_by(ExerciseQuestion.created_at.desc())
            if like:
                q_query = q_query.filter(ExerciseQuestion.enunciado.ilike(like))
            section_blocks.append({'section': s, 'questions': q_query.all()})
        # Questões sem seção
        unsec_q = ExerciseQuestion.query.filter_by(topic_id=t.id, section_id=None)
        if like:
            unsec_q = unsec_q.filter(ExerciseQuestion.enunciado.ilike(like))
        unsec_list = unsec_q.order_by(ExerciseQuestion.created_at.desc()).all()
        data.append({'topic': t, 'sections': section_blocks, 'unsectioned': unsec_list})
    # Only include topics that have questions in the navigation
    etopics = [bloco['topic'] for bloco in data if bloco['sections'] or bloco['unsectioned']]
    return render_template('exercicios.html', etopics=etopics, q=q, estrutura=data)

@bp.route('/videos')
def videos():
    # Temporariamente desativado
    return render_template('maintenance.html', section='Vídeos'), 503

@bp.route('/variacoes')
def variacoes():
    # Redireciona para a nova seção de vídeos
    return redirect(url_for('main.videos'))

@bp.route('/api/search/suggest')
def api_search_suggest():
    """Sugestões de busca simples: usuáries (@) e hashtags (#) a partir de prefixo.
    Retorna lista de objetos { value, type } onde type in { 'user','tag' }.
    """
    prefix = (request.args.get('q') or '').strip()
    if not prefix:
        return jsonify([])
    results = []
    try:
        from sqlalchemy import or_, func
        # Usuáries por prefixo de username
        u_like = f"{prefix.lstrip('@')}%"
        users = User.query.filter(User.username.ilike(u_like)).order_by(User.username.asc()).limit(5).all()
        for u in users:
            results.append({'value': f"@{u.username}", 'type': 'user'})
        # Hashtags por prefixo simples: varrer posts recentes e extrair tags
        like = f"%{prefix.lstrip('#')}%"
        recent_posts = Post.query.filter(((Post.is_deleted == False) | (Post.is_deleted.is_(None))) & (Post.conteudo.ilike(like)))\
                                  .order_by(Post.data.desc()).limit(100).all()
        import re as _re
        tags = {}
        for p in recent_posts:
            for m in _re.findall(r"#([\wá-úÁ-Ú0-9_]+)", p.conteudo or ''):
                if prefix.lstrip('#').lower() in m.lower():
                    tags[m.lower()] = m
        for t in list(tags.values())[:5]:
            results.append({'value': f"#{t}", 'type': 'tag'})
    except Exception as e:
        current_app.logger.warning(f"suggest failed: {e}")
    return jsonify(results[:10])

@bp.route('/api/posts', methods=['GET'])
def get_posts():
    """Retorna posts com filtros opcionais:
    q: termo (pode começar com # ou @)
    sort: recentes|populares
    tipo: todos|texto|imagem
    periodo: todos|24h|7d|30d
    """
    from sqlalchemy import or_, func
    q = (request.args.get('q') or '').strip()
    sort = (request.args.get('sort') or 'recentes').strip().lower()
    tipo = (request.args.get('tipo') or 'todos').strip().lower()
    periodo = (request.args.get('periodo') or 'todos').strip().lower()

    query = Post.query.filter((Post.is_deleted == False) | (Post.is_deleted.is_(None)))

    # Termo livre
    if q:
        patterns = {q}
        if q.startswith('#'):
            naked = q.lstrip('#')
            if naked:
                patterns.add(naked)
        if q.startswith('@'):
            uname = q.lstrip('@')
            if uname:
                patterns.add(uname)
        like_clauses = []
        for pattern in patterns:
            like = f"%{pattern}%"
            like_clauses.append(Post.conteudo.ilike(like))
            like_clauses.append(Post.usuario.ilike(like))
        query = query.filter(or_(*like_clauses))

    # Filtro por período
    if periodo in ('24h','7d','30d'):
        now = datetime.utcnow()
        delta = {'24h': timedelta(hours=24), '7d': timedelta(days=7), '30d': timedelta(days=30)}[periodo]
        query = query.filter(Post.data >= (now - delta))

    # Filtro por tipo (texto/imagem)
    if tipo == 'texto':
        query = query.filter(or_(Post.imagem.is_(None), Post.imagem == ''))
    elif tipo == 'imagem':
        query = query.filter(Post.imagem.isnot(None)).filter(Post.imagem != '')

    # Ordenação
    if sort == 'populares':
        likes_join = db.session.query(
            Post.id.label('pid'), func.count(User.id).label('lc')
        ).outerjoin(Post.likes).group_by(Post.id).subquery()
        query = query.outerjoin(likes_join, likes_join.c.pid == Post.id)
        query = query.order_by(func.coalesce(likes_join.c.lc, 0).desc(), Post.data.desc())
    else:
        query = query.order_by(Post.data.desc())

    posts = query.all()
    result = []
    for p in posts:
        try:
            dt_local = _to_brasilia(p.data) if p.data else None
            data_str = dt_local.strftime('%d/%m/%Y %H:%M') if dt_local else ''
        except Exception as e:
            print(f'[ERRO DATA POST] id={p.id} data={p.data} erro={e}')
            data_str = ''
        # Buscar o usuário autor do post
        autor = None
        if hasattr(p, 'usuario_id') and p.usuario_id:
            autor = User.query.get(p.usuario_id)
        elif hasattr(p, 'usuario') and p.usuario:
            autor = User.query.filter_by(username=p.usuario).first()
        foto_perfil = autor.foto_perfil if autor and autor.foto_perfil else 'img/perfil.png'
        liked = False
        try:
            from flask_login import current_user
            if current_user.is_authenticated:
                # Evita carregar toda a relação se já estiver associada; 'in' funciona com coleção
                liked = current_user in p.likes
        except Exception:
            pass
        imagens_concat = p.imagem or ''
        imagens_list = [seg for seg in imagens_concat.split('|') if seg]
        result.append({
            'id': p.id,
            'usuario': p.usuario or 'Usuárie',
            'conteudo': p.conteudo or '',
            'imagem': imagens_concat,
            'images': imagens_list,
            'data': data_str,
            'foto_perfil': foto_perfil,
            'liked': liked
        })
    print(f'[API /api/posts] {len(result)} posts retornados')
    return jsonify(result)

@bp.route('/api/posts', methods=['POST'])
@login_required
def create_post():
    data = request.json
    # Moderação de conteúdo
    ok, cat, matched_word = check_text(data.get('conteudo') or '')
    if not ok:
        return jsonify({'error': 'conteudo_bloqueado', 'reason': cat, 'message': refusal_message_pt(cat, matched_word)}), 400
    if (data.get('imagem') or ''):
        ok_img, cat_img, matched_img = check_image_hint(data.get('imagem'))
        if not ok_img:
            return jsonify({'error': 'imagem_bloqueada', 'reason': cat_img, 'message': refusal_message_pt(cat_img, matched_img)}), 400
    usuario_nome = current_user.username if hasattr(current_user, 'username') else data.get('usuario', 'Usuárie')
    usuario_id = current_user.id if hasattr(current_user, 'id') else None
    post = Post(
        usuario=usuario_nome,
        usuario_id=usuario_id,
        conteudo=data['conteudo'],
        imagem=data.get('imagem', ''),
        data=datetime.now()
    )
    db.session.add(post)
    db.session.commit()
    return jsonify({'success': True}), 201

@bp.route('/api/posts/<int:post_id>', methods=['DELETE'])
@login_required
def soft_delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.usuario_id != current_user.id and not current_user.is_admin:
        return jsonify({'error':'forbidden'}), 403
    post.is_deleted = True
    post.deleted_at = datetime.utcnow()
    post.deleted_by = current_user.id
    db.session.commit()
    return jsonify({'deleted': True})

@bp.route('/api/posts/<int:post_id>/restore', methods=['POST'])
@login_required
def restore_post(post_id):
    post = Post.query.get_or_404(post_id)
    if not current_user.is_admin:
        return jsonify({'error':'forbidden'}), 403
    post.is_deleted = False
    post.deleted_at = None
    post.deleted_by = None
    db.session.commit()
    return jsonify({'restored': True})

@bp.route('/api/posts/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    user = current_user
    if user in post.likes:
        post.likes.remove(user)
        db.session.commit()
        return jsonify({'liked': False})
    else:
        post.likes.append(user)
        db.session.commit()
        return jsonify({'liked': True})

@bp.route('/api/posts/<int:post_id>/likes', methods=['GET'])
def get_likes(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify([u.username for u in post.likes])

@bp.route('/api/posts/<int:post_id>/comentarios', methods=['GET', 'POST'])
@login_required
def comentarios(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        conteudo = request.json.get('conteudo')
        ok, cat, matched_word = check_text(conteudo or '')
        if not ok:
            return jsonify({'error': 'conteudo_bloqueado', 'reason': cat, 'message': refusal_message_pt(cat, matched_word)}), 400
        comentario = Comentario(
            usuario_id=current_user.id,
            conteudo=conteudo,
            post_id=post.id
        )
        db.session.add(comentario)
        db.session.commit()
        return jsonify({'ok': True})
    else:
        comentarios = Comentario.query.filter_by(post_id=post.id).order_by(Comentario.data.desc()).all()
        return jsonify([
            {
                'usuario': c.usuario.username if c.usuario and hasattr(c.usuario, 'username') else 'Usuárie',
                'conteudo': c.conteudo,
                'data': c.data.strftime('%d/%m/%Y %H:%M')
            }
            for c in comentarios
        ])

@bp.route('/configuracoes')
@login_required
def configuracoes():
    # Passa o usuário autenticado como 'user' para o template
    return render_template('configuracoes.html', user=current_user)

@bp.route('/suporte', methods=['GET','POST'])
def suporte():
    if request.method == 'POST':
        nome = request.form.get('nome') or (current_user.username if current_user.is_authenticated else None)
        email = request.form.get('email') or (getattr(current_user,'email', None) if current_user.is_authenticated else None)
        mensagem = request.form.get('mensagem','').strip()
        if not mensagem:
            flash('Mensagem obrigatória.')
            return redirect(url_for('main.suporte'))
        ticket = SupportTicket(usuario_id=current_user.id if current_user.is_authenticated else None,
                               nome=nome, email=email, mensagem=mensagem)
        db.session.add(ticket)
        db.session.commit()
        flash('Chamado enviado!')
        return redirect(url_for('main.suporte'))
    return render_template('suporte.html')

@bp.route('/admin/suporte')
@login_required
def admin_suporte_lista():
    if not (current_user.is_admin or getattr(current_user,'is_superadmin',False)):
        return 'Acesso restrito', 403
    tickets = SupportTicket.query.order_by(SupportTicket.created_at.desc()).limit(200).all()
    return render_template('admin/suporte_tickets.html', tickets=tickets)

@bp.route('/admin/suporte/<int:ticket_id>', methods=['POST'])
@login_required
def admin_suporte_responder(ticket_id):
    if not (current_user.is_admin or getattr(current_user,'is_superadmin',False)):
        return 'Acesso restrito', 403
    ticket = SupportTicket.query.get_or_404(ticket_id)
    resposta = request.form.get('resposta','').strip()
    status = request.form.get('status','').strip()
    if resposta:
        ticket.resposta = resposta
    if status:
        ticket.status = status
    from datetime import datetime as _dt
    ticket.updated_at = _dt.utcnow()
    db.session.commit()
    flash('Atualizado.')
    return redirect(url_for('main.admin_suporte_lista'))

@bp.route('/perfil')
@login_required
def meu_perfil():
    return render_template('meu_perfil.html', usuario=current_user)

@bp.route('/perfil/<int:user_id>')
@login_required
def perfil(user_id):
    usuario = User.query.get_or_404(user_id)
    return render_template('perfil.html', usuario=usuario)

## (Removida rota duplicada /api/seguir que usava métodos inexistentes seguir/deixar_de_seguir)

@bp.route('/esqueci_senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip()
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                try:
                    token = generate_token({'uid': user.id, 'scope': 'reset'})
                    reset_url = url_for('main.reset_senha', token=token, _external=True)
                    html = render_reset_email(user.username or user.email, reset_url)
                    send_email(user.email, 'Redefinir senha', html)
                    flash('Enviamos um link de recuperação, se o e-mail existir.')
                except Exception:
                    flash('Não foi possível enviar o e-mail agora. Tente mais tarde.')
            else:
                # Não revelar existência
                flash('Enviamos um link de recuperação, se o e-mail existir.')
        return redirect(url_for('main.esqueci_senha'))
    return render_template('esqueci_senha.html')

@bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        password = request.form['password']

        genero = request.form['genero']
        pronome = request.form['pronome']
        from datetime import datetime
        data_nascimento_str = request.form['data_nascimento']
        data_nascimento = None
        if data_nascimento_str:
            try:
                data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d').date()
            except Exception:
                data_nascimento = None

        # Validate username - no spaces allowed and length requirements
        if ' ' in username:
            flash('Nome de usuário não pode conter espaços.')
            return redirect(url_for('main.cadastro'))
        
        if len(username) < 5:
            flash('Nome de usuário deve ter no mínimo 5 caracteres.')
            return redirect(url_for('main.cadastro'))
        
        if len(username) > 45:
            flash('Nome de usuário deve ter no máximo 45 caracteres.')
            return redirect(url_for('main.cadastro'))

        # Verifica se o usuário já existe
        if User.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.')
            return redirect(url_for('main.cadastro'))

        # Cria o novo usuário
        novo_usuario = User(
            username=username,
            email=email,
            genero=genero,
            pronome=pronome,
            data_nascimento=data_nascimento
        )
        # Define senha com hash seguro
        try:
            novo_usuario.set_password(password)
        except Exception:
            flash('Falha ao definir senha. Tente novamente.')
            return redirect(url_for('main.cadastro'))
        db.session.add(novo_usuario)
        db.session.commit()
        # E-mails pós-cadastro (não bloqueantes)
        try:
            # Boas-vindas
            html = render_welcome_email(novo_usuario.username or novo_usuario.email)
            send_email(novo_usuario.email, 'Bem-vinde ao Gramátike', html)
            # Verificação de e-mail
            token = generate_token({'uid': novo_usuario.id, 'scope': 'verify'})
            verify_url = url_for('main.verify_email', token=token, _external=True)
            html_v = render_verify_email(novo_usuario.username or novo_usuario.email, verify_url)
            send_email(novo_usuario.email, 'Confirme seu e-mail', html_v)
        except Exception:
            pass
        flash('Cadastro realizado com sucesso! Faça login.')
        return redirect(url_for('main.login'))

    return render_template('cadastro.html')

@bp.route('/verificar-email')
def verify_email():
    token = request.args.get('token','')
    data = verify_token(token, max_age=60*60*24)
    if not data or data.get('scope') != 'verify':
        flash('Token inválido ou expirado.')
        return redirect(url_for('main.login'))
    user = User.query.get(data.get('uid'))
    if not user:
        flash('Usuárie não encontrade.')
        return redirect(url_for('main.login'))
    if not getattr(user, 'email_confirmed', False):
        user.email_confirmed = True
        from datetime import datetime as _dt
        user.email_confirmed_at = _dt.utcnow()
        db.session.commit()
    flash('E-mail confirmado com sucesso!')
    return redirect(url_for('main.login'))

@bp.route('/reset-senha', methods=['GET', 'POST'])
def reset_senha():
    token = request.args.get('token','') if request.method == 'GET' else (request.form.get('token') or '')
    data = verify_token(token, max_age=60*60)
    if not data or data.get('scope') != 'reset':
        flash('Token inválido ou expirado.')
        return redirect(url_for('main.login'))
    user = User.query.get(data.get('uid'))
    if not user:
        flash('Usuárie não encontrade.')
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        p1 = request.form.get('password') or ''
        p2 = request.form.get('password2') or ''
        if not p1 or p1 != p2:
            flash('As senhas não coincidem.')
            return redirect(url_for('main.reset_senha', token=token))
        # Define nova senha com hash seguro
        try:
            user.set_password(p1)
        except Exception:
            flash('Não foi possível atualizar a senha agora.')
            return redirect(url_for('main.reset_senha', token=token))
        db.session.commit()
        flash('Senha redefinida. Faça login.')
        return redirect(url_for('main.login'))
    return render_template('reset_senha.html', token=token)

@bp.route('/admin/usuarios', methods=['GET', 'POST'])
@login_required
def gerenciar_usuarios():
    if not current_user.is_admin:
        abort(403)
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = User.query.get(user_id)
        if getattr(user, 'is_superadmin', False) and not current_user.is_superadmin:
            flash('Você não pode alterar privilégios do superadmin.')
            return redirect(url_for('main.gerenciar_usuarios'))
        # Se for superadmin mexendo nele mesmo, ignora toggle para não remover acidentalmente
        if getattr(user, 'is_superadmin', False) and current_user.id == user.id:
            flash('Superadmin não pode remover seu próprio status de admin.')
            return redirect(url_for('main.gerenciar_usuarios'))
        user.is_admin = not user.is_admin
        db.session.commit()
        return redirect(url_for('main.gerenciar_usuarios'))
    usuarios = User.query.all()
    return render_template('gerenciar_usuarios.html', usuarios=usuarios)

## Rotas do Lune removidas: chat, stream, conversas, histórico, memórias, conhecimento, feedback, likes
"""
As rotas relacionadas ao Lune foram descontinuadas e removidas.
"""
def _placeholder_removed():
    data = request.get_json(silent=True) or {}
    return jsonify({'error':'lune_removed'}), 410

# Conversas: listar e carregar histórico (apenas para usuáries autenticades)
from sqlalchemy import func

## Todas as rotas do Lune removidas



## Palavras do Dia - Feature educacional inclusiva

@bp.route('/api/palavra-do-dia')
def api_palavra_do_dia():
    """Retorna a palavra do dia com base na data atual (rotação diária)."""
    from gramatike_app.models import PalavraDoDia
    from datetime import datetime
    
    # Busca palavras ativas ordenadas
    palavras = PalavraDoDia.query.filter_by(ativo=True).order_by(PalavraDoDia.ordem.asc()).all()
    
    if not palavras:
        return jsonify({'error': 'Nenhuma palavra cadastrada'}), 404
    
    # Calcula índice baseado no dia do ano para rotação diária
    dia_do_ano = datetime.utcnow().timetuple().tm_yday
    indice = dia_do_ano % len(palavras)
    palavra = palavras[indice]
    
    # Verifica se usuário já interagiu hoje
    ja_interagiu = False
    if current_user.is_authenticated:
        from gramatike_app.models import PalavraDoDiaInteracao
        hoje = datetime.utcnow().date()
        interacao_hoje = PalavraDoDiaInteracao.query.filter(
            PalavraDoDiaInteracao.palavra_id == palavra.id,
            PalavraDoDiaInteracao.usuario_id == current_user.id,
            func.date(PalavraDoDiaInteracao.created_at) == hoje
        ).first()
        ja_interagiu = interacao_hoje is not None
    
    result = {
        'id': palavra.id,
        'palavra': palavra.palavra,
        'significado': palavra.significado,
        'ja_interagiu': ja_interagiu
    }
    
    return jsonify(result)

@bp.route('/api/palavra-do-dia/interagir', methods=['POST'])
@login_required
def api_palavra_do_dia_interagir():
    """Registra interação do usuário com a palavra do dia."""
    from gramatike_app.models import PalavraDoDia, PalavraDoDiaInteracao
    from datetime import datetime
    
    data = request.get_json() or {}
    palavra_id = data.get('palavra_id')
    tipo = data.get('tipo')  # 'frase' ou 'significado'
    frase = data.get('frase', '').strip()
    
    if not palavra_id or not tipo:
        return jsonify({'error': 'Dados incompletos'}), 400
    
    if tipo not in ['frase', 'significado']:
        return jsonify({'error': 'Tipo inválido'}), 400
    
    palavra = PalavraDoDia.query.get_or_404(palavra_id)
    
    # Verifica se já interagiu hoje
    hoje = datetime.utcnow().date()
    interacao_existente = PalavraDoDiaInteracao.query.filter(
        PalavraDoDiaInteracao.palavra_id == palavra_id,
        PalavraDoDiaInteracao.usuario_id == current_user.id,
        func.date(PalavraDoDiaInteracao.created_at) == hoje
    ).first()
    
    if interacao_existente:
        return jsonify({'error': 'Você já interagiu com a palavra de hoje'}), 400
    
    # Valida frase se for tipo 'frase'
    if tipo == 'frase':
        if not frase:
            return jsonify({'error': 'Frase não pode estar vazia'}), 400
        if len(frase) > 500:
            return jsonify({'error': 'Frase muito longa (máximo 500 caracteres)'}), 400
    
    # Registra interação
    interacao = PalavraDoDiaInteracao(
        palavra_id=palavra_id,
        usuario_id=current_user.id,
        tipo=tipo,
        frase=frase if tipo == 'frase' else None
    )
    db.session.add(interacao)
    db.session.commit()
    
    return jsonify({'success': True, 'mensagem': 'Incrível! Hoje tu aprendeu uma nova forma de incluir todes 💜'})
