from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, current_user, login_required
from gramatike_app.forms import LoginForm, RegistrationForm
from gramatike_app.models import User, db, Post, PostImage
from datetime import datetime
from gramatike_app import db
from gramatike_app.utils.emailer import send_email, render_welcome_email

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    return render_template('index.html', admin=current_user.is_admin)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.feed'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            # Tenta buscar usuário - pode falhar se tabelas não existem
            user = User.query.filter_by(username=form.username.data).first()
        except Exception as db_error:
            current_app.logger.error(f"Erro de banco de dados no login: {db_error}")
            flash('Sistema temporariamente indisponível. Por favor, tente novamente mais tarde.', 'error')
            return render_template('login.html', form=form)
        
        from datetime import datetime
        if user is None or not user.check_password(form.password.data):
            flash('Usuárie ou senha inválidos', 'error')
            return redirect(url_for('main.login'))
        # Verificações de moderação
        if getattr(user, 'is_banned', False):
            flash(f'Conta banida: {user.ban_reason or "motivo não especificado"}', 'error')
            return redirect(url_for('main.login'))
        if getattr(user, 'suspended_until', None):
            if user.suspended_until and datetime.utcnow() < user.suspended_until:
                ate = user.suspended_until.strftime('%d/%m %H:%M')
                flash(f'Conta suspensa até {ate}.', 'error')
                return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('main.feed'))
    return render_template('login.html', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.feed'))
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data)
            # Definir senha com hash seguro
            try:
                user.set_password(form.password.data)
            except Exception:
                flash('Falha ao definir senha. Tente novamente.', 'error')
                return redirect(url_for('main.register'))
            db.session.add(user)
            db.session.commit()
            # E-mail de boas-vindas (não bloqueante)
            try:
                html = render_welcome_email(user.username or user.email)
                send_email(user.email, 'Bem-vinde ao Gramátike', html)
            except Exception:
                pass
            flash('Registro feito com sucesso.', 'success')
            return redirect(url_for('main.login'))
        except Exception as db_error:
            current_app.logger.error(f"Erro ao registrar usuárie: {db_error}")
            db.session.rollback()
            flash('Sistema temporariamente indisponível. Por favor, tente novamente mais tarde.', 'error')
            return render_template('register.html', form=form)
    return render_template('register.html', form=form)

@bp.route('/perfil')
@login_required
def meu_perfil():
    return render_template('meu_perfil.html', usuarie=current_user)



@bp.route('/gramatike_edu')
def estudos():
    # Rota legada: redireciona para Educação unificada
    return redirect(url_for('main.educacao'))


@bp.route('/novo_post')
@login_required
def novo_post():
    return render_template('criar_post.html')

@bp.route('/api/posts', methods=['GET'])
def get_posts():
    posts = Post.query.order_by(Post.data.desc()).all()
    return jsonify([
        {
            'id': p.id,
            'usuarie': p.usuarie,
            'conteudo': p.conteudo,
            'imagem': p.imagem,
            'data': p.data.strftime('%d/%m/%Y %H:%M')
        } for p in posts
    ])

@bp.route('/api/posts', methods=['POST'])
def create_post():
    """Criação de post via JSON (legacy) ou multipart (novo com imagem).
    Se multipart for detectado (form-data), processa campo 'conteudo' e arquivo 'imagem'.
    Retorna JSON padronizado.
    """
    import os, uuid
    conteudo = None
    imagem_path = ''
    if request.content_type and 'multipart/form-data' in request.content_type.lower():
        conteudo = (request.form.get('conteudo') or '').strip()
        f = request.files.get('imagem')
        if f and f.filename:
            ext = f.filename.rsplit('.',1)[-1].lower()
            if ext in {'png','jpg','jpeg','webp','gif'}:
                # Limite simples 3MB
                f.seek(0, os.SEEK_END); size = f.tell(); f.seek(0)
                if size <= 3 * 1024 * 1024:
                    fname = f"post_{uuid.uuid4().hex[:10]}.{ext}"
                    target_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'posts')
                    os.makedirs(target_dir, exist_ok=True)
                    f.save(os.path.join(target_dir, fname))
                    imagem_path = f"uploads/posts/{fname}"
            # else: extensão ignorada silenciosamente
    else:
        data = request.json or {}
        conteudo = (data.get('conteudo') or '').strip()
        imagem_path = (data.get('imagem') or '').strip()
    if not conteudo:
        return jsonify({'success': False, 'error': 'conteudo_vazio'}), 400
    username = current_user.username if current_user.is_authenticated else 'Usuárie'
    post = Post(
        usuarie=username,
        usuario_id=current_user.id if current_user.is_authenticated else None,
        conteudo=conteudo,
        imagem=imagem_path,
        data=datetime.now()
    )
    db.session.add(post)
    db.session.commit()
    return jsonify({'success': True, 'id': post.id, 'imagem': imagem_path}), 201

@bp.route('/api/posts_multi', methods=['POST'])
@login_required
def create_post_multi():
    """Criação de post com até 4 imagens (campo 'imagens'). Armazena caminhos separados por '|' em Post.imagem por simplicidade.
    Futuro: mover para tabela PostImage.
    """
    import os, uuid
    conteudo = (request.form.get('conteudo') or '').strip()
    if not conteudo:
        return jsonify({'success': False, 'error': 'conteudo_vazio'}), 400
    files = request.files.getlist('imagens') if 'imagens' in request.files else []
    paths = []
    meta = []
    # PIL may not be available in Pyodide/serverless environments
    try:
        from PIL import Image
        PIL_AVAILABLE = True
    except ImportError:
        PIL_AVAILABLE = False
    for idx, f in enumerate(files[:4]):
        if not f or not f.filename: continue
        ext = f.filename.rsplit('.',1)[-1].lower()
        if ext not in {'png','jpg','jpeg','webp','gif'}: continue
        f.seek(0, os.SEEK_END); size = f.tell(); f.seek(0)
        if size > 3 * 1024 * 1024: continue
        fname = f"post_{uuid.uuid4().hex[:10]}.{ext}"
        target_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'posts')
        os.makedirs(target_dir, exist_ok=True)
        full_path = os.path.join(target_dir, fname)
        f.save(full_path)
        # dimensões
        w = h = None
        if PIL_AVAILABLE:
            try:
                with Image.open(full_path) as im:
                    w, h = im.size
            except (IOError, OSError):
                # Invalid or corrupted image file
                pass
        paths.append(f"uploads/posts/{fname}")
        meta.append({'path': f"uploads/posts/{fname}", 'w': w, 'h': h})
    post = Post(
        usuarie=current_user.username,
        usuario_id=current_user.id,
        conteudo=conteudo,
        imagem='|'.join(paths),
        data=datetime.now()
    )
    db.session.add(post)
    db.session.flush()
    # Persistir imagens normalizadas
    for i, m in enumerate(meta):
        pi = PostImage(post_id=post.id, path=m['path'], ordem=i, width=m['w'], height=m['h'])
        db.session.add(pi)
    db.session.commit()
    return jsonify({'success': True, 'id': post.id, 'imagens': paths}), 201

@bp.route('/api/posts/<int:post_id>/thumbs/regenerar', methods=['POST'])
@login_required
def regenerate_post_thumbs(post_id):
    """Gera thumbnails (largura máx 420) para imagens de um post e salva em uploads/posts/thumbs."""
    import os
    # PIL may not be available in Pyodide/serverless environments
    try:
        from PIL import Image
    except ImportError:
        return jsonify({'error': 'Pillow not available in this environment', 'thumbs': []}), 200
    post = Post.query.get_or_404(post_id)
    if post.usuario_id != current_user.id and not (getattr(current_user,'is_admin',False) or getattr(current_user,'is_superadmin',False)):
        return jsonify({'error':'forbidden'}), 403
    basedir = os.path.join(current_app.root_path, 'static')
    out_dir = os.path.join(basedir, 'uploads', 'posts', 'thumbs')
    os.makedirs(out_dir, exist_ok=True)
    results = []
    images = []
    if post.imagens.count():
        images = [pi.path for pi in post.imagens]
    else:
        images = [p for p in (post.imagem or '').split('|') if p]
    for p in images:
        src_path = os.path.join(basedir, p.replace('/', os.sep))
        if not os.path.isfile(src_path):
            continue
        try:
            with Image.open(src_path) as im:
                im.thumbnail((420, 420))
                base = os.path.basename(p)
                name, ext = os.path.splitext(base)
                out_name = f"{name}_th{ext or '.jpg'}"
                out_path = os.path.join(out_dir, out_name)
                im.save(out_path)
                rel = f"uploads/posts/thumbs/{out_name}"
                results.append(rel)
        except Exception:
            continue
    return jsonify({'ok': True, 'thumbs': results})

@bp.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/esqueci_senha')
def esqueci_senha():
    return render_template('esqueci_senha.html')

@bp.route('/comentar', methods=['POST'])
def comentar():
    # lógica para salvar o comentário
    return redirect(url_for('main.feed'))

main_perfil_bp = Blueprint('main_perfil', __name__)

@main_perfil_bp.route('/main_perfil')
@login_required
def main_perfil():
    return render_template('meu_perfil.html', usuarie=current_user)

