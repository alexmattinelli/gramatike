from flask import Flask
# Carrega variáveis de .env o mais cedo possível (antes de importar Config)
try:
    import os as _os_dv
    from dotenv import load_dotenv  # type: ignore
    # raiz do projeto: um nível acima de gramatike_app/
    _ROOT_DV = _os_dv.path.dirname(_os_dv.path.dirname(_os_dv.path.abspath(__file__)))
    load_dotenv(_os_dv.path.join(_ROOT_DV, '.env'))
except Exception:
    pass

try:
    from config import Config
except Exception:
    # Fallback para execução fora da raiz do projeto (scripts, tasks)
    import importlib.util as _ilu
    import os as _os, sys as _sys
    _ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    _cfg = _os.path.join(_ROOT, 'config.py')
    if _os.path.exists(_cfg):
        _spec = _ilu.spec_from_file_location('config', _cfg)
        if _spec and _spec.loader:
            _mod = _ilu.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            _sys.modules['config'] = _mod
            Config = getattr(_mod, 'Config')
        else:
            raise
    else:
        raise
from flask_login import LoginManager
from gramatike_app.models import db
from flask_migrate import Migrate
from gramatike_app.models import User
import os
try:
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
except Exception:
    csrf = None
from sqlalchemy import inspect, text

login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = None  # remove 'Please log in to access this page.'
login_manager.login_message_category = 'info'

def create_app():
    import os as _os_paths
    _pkg_dir = _os_paths.path.dirname(_os_paths.path.abspath(__file__))
    app = Flask(
        __name__,
        template_folder=_os_paths.path.join(_pkg_dir, 'templates'),
        static_folder=_os_paths.path.join(_pkg_dir, 'static')
    )
    app.config.from_object(Config)
    # Não sobrescrever valores vindos de Config/ambiente; apenas definir padrão se ausente
    app.config.setdefault('SECRET_KEY', os.getenv('SECRET_KEY', 'change-me'))
    app.config.setdefault('SQLALCHEMY_DATABASE_URI', Config.SQLALCHEMY_DATABASE_URI)
    # Removido bind legado 'delu'
    app.config['SQLALCHEMY_BINDS'] = {}
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Cookies mais seguros
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    # Se estiver atrás de HTTPS, ative abaixo
    app.config['SESSION_COOKIE_SECURE'] = False

    # Carrega configurações opcionais de e-mail a partir de variáveis de ambiente
    try:
        _mail_env_map = {
            'MAIL_SERVER': os.getenv('MAIL_SERVER'),
            'MAIL_PORT': os.getenv('MAIL_PORT'),
            'MAIL_USE_TLS': os.getenv('MAIL_USE_TLS'),
            'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
            'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
            'MAIL_DEFAULT_SENDER': os.getenv('MAIL_DEFAULT_SENDER'),
            'MAIL_SENDER_NAME': os.getenv('MAIL_SENDER_NAME'),
        }
        if _mail_env_map['MAIL_PORT'] is not None:
            try:
                _mail_env_map['MAIL_PORT'] = int(_mail_env_map['MAIL_PORT'])
            except Exception:
                pass
        if _mail_env_map['MAIL_USE_TLS'] is not None:
            _mail_env_map['MAIL_USE_TLS'] = str(_mail_env_map['MAIL_USE_TLS']).lower() in ('1', 'true', 'yes', 'on')
        for _k, _v in _mail_env_map.items():
            if _v is not None:
                app.config[_k] = _v
    except Exception as _e:
        try:
            app.logger.debug(f'Ignorando erro ao carregar MAIL_* do ambiente: {_e}')
        except Exception:
            pass

    db.init_app(app)
    # Garante diretório do SQLite (quando for sqlite:///path)
    try:
        uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if uri.startswith('sqlite:///'):
            import os as _os
            db_path = uri.replace('sqlite:///', '', 1)
            db_dir = _os.path.dirname(db_path)
            if db_dir and not _os.path.exists(db_dir):
                _os.makedirs(db_dir, exist_ok=True)
    except Exception as _e:
        app.logger.warning(f'Não foi possível garantir diretório do banco: {_e}')
    # Proteção CSRF para formulários
    if csrf is not None:
        try:
            csrf.init_app(app)
        except Exception as _e:
            app.logger.warning(f'CSRFProtect indisponível: {_e}')
    login_manager.init_app(app)
    migrate = Migrate(app, db)
    with app.app_context():
        try:
            db.create_all()
        except Exception as _e:
            try:
                app.logger.error(f'Falha ao criar/checar tabelas: {_e}')
            except Exception:
                pass
        # Filtro Jinja: fromjson (carrega JSON serializado em dict)
        def _fromjson_filter(value):
            try:
                import json as _json
                return _json.loads(value) if value else {}
            except Exception:
                return {}
        app.jinja_env.filters['fromjson'] = _fromjson_filter
        # Auto-reparo mínimo de schema para colunas novas que não existam ainda (ex: created_at, soft delete)
        # Isso é um fallback emergencial até que as migrations Alembic sejam aplicadas corretamente.
        insp = inspect(db.engine)
        tables = set(insp.get_table_names())
        try:
            def has_column(table, col):
                return any(c['name'] == col for c in insp.get_columns(table))

            # user.created_at
            if 'user' in tables and not has_column('user', 'created_at'):
                db.session.execute(text('ALTER TABLE user ADD COLUMN created_at DATETIME'))
                db.session.execute(text('UPDATE user SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL'))
                # índice é opcional; em SQLite criar se desejar
                try:
                    db.session.execute(text('CREATE INDEX IF NOT EXISTS ix_user_created_at ON user (created_at)'))
                except Exception:
                    pass
                app.logger.warning('Auto-reparo: adicionada coluna user.created_at')

            # user.email_confirmed e email_confirmed_at
            if 'user' in tables:
                if not has_column('user', 'email_confirmed'):
                    try:
                        db.session.execute(text('ALTER TABLE user ADD COLUMN email_confirmed BOOLEAN'))
                        db.session.execute(text('UPDATE user SET email_confirmed = 0 WHERE email_confirmed IS NULL'))
                        app.logger.warning('Auto-reparo: adicionada coluna user.email_confirmed')
                    except Exception as e:
                        app.logger.error(f'Falha adicionando email_confirmed: {e}')
                if not has_column('user', 'email_confirmed_at'):
                    try:
                        db.session.execute(text('ALTER TABLE user ADD COLUMN email_confirmed_at DATETIME'))
                        app.logger.warning('Auto-reparo: adicionada coluna user.email_confirmed_at')
                    except Exception as e:
                        app.logger.error(f'Falha adicionando email_confirmed_at: {e}')

            # post soft delete cols
            if 'post' in tables:
                if not has_column('post', 'is_deleted'):
                    db.session.execute(text('ALTER TABLE post ADD COLUMN is_deleted BOOLEAN'))
                    db.session.execute(text('UPDATE post SET is_deleted = 0 WHERE is_deleted IS NULL'))
                    try:
                        db.session.execute(text('CREATE INDEX IF NOT EXISTS ix_post_is_deleted ON post (is_deleted)'))
                    except Exception:
                        pass
                    app.logger.warning('Auto-reparo: adicionada coluna post.is_deleted')
                if not has_column('post', 'deleted_at'):
                    db.session.execute(text('ALTER TABLE post ADD COLUMN deleted_at DATETIME'))
                    app.logger.warning('Auto-reparo: adicionada coluna post.deleted_at')
                if not has_column('post', 'deleted_by'):
                    db.session.execute(text('ALTER TABLE post ADD COLUMN deleted_by INTEGER'))
                    app.logger.warning('Auto-reparo: adicionada coluna post.deleted_by')

            # divulgacao: acrescentar colunas novas se a tabela já existir sem elas
            if 'divulgacao' in tables:
                try:
                    if not has_column('divulgacao','edu_content_id'):
                        db.session.execute(text('ALTER TABLE divulgacao ADD COLUMN edu_content_id INTEGER'))
                        app.logger.warning('Auto-reparo: adicionada coluna divulgacao.edu_content_id')
                    if not has_column('divulgacao','post_id'):
                        db.session.execute(text('ALTER TABLE divulgacao ADD COLUMN post_id INTEGER'))
                        app.logger.warning('Auto-reparo: adicionada coluna divulgacao.post_id')
                    if not has_column('divulgacao','created_at'):
                        db.session.execute(text('ALTER TABLE divulgacao ADD COLUMN created_at DATETIME'))
                        app.logger.warning('Auto-reparo: adicionada coluna divulgacao.created_at')
                    if not has_column('divulgacao','updated_at'):
                        db.session.execute(text('ALTER TABLE divulgacao ADD COLUMN updated_at DATETIME'))
                        app.logger.warning('Auto-reparo: adicionada coluna divulgacao.updated_at')
                    # Novos destinos: show_on_*
                    if not has_column('divulgacao','show_on_edu'):
                        db.session.execute(text('ALTER TABLE divulgacao ADD COLUMN show_on_edu BOOLEAN'))
                        db.session.execute(text('UPDATE divulgacao SET show_on_edu = 1 WHERE show_on_edu IS NULL'))
                        try:
                            db.session.execute(text('CREATE INDEX IF NOT EXISTS ix_divulgacao_show_on_edu ON divulgacao (show_on_edu)'))
                        except Exception:
                            pass
                        app.logger.warning('Auto-reparo: adicionada coluna divulgacao.show_on_edu')
                    if not has_column('divulgacao','show_on_index'):
                        db.session.execute(text('ALTER TABLE divulgacao ADD COLUMN show_on_index BOOLEAN'))
                        db.session.execute(text('UPDATE divulgacao SET show_on_index = 1 WHERE show_on_index IS NULL'))
                        try:
                            db.session.execute(text('CREATE INDEX IF NOT EXISTS ix_divulgacao_show_on_index ON divulgacao (show_on_index)'))
                        except Exception:
                            pass
                        app.logger.warning('Auto-reparo: adicionada coluna divulgacao.show_on_index')
                    # coluna show_on_lune descontinuada
                except Exception as e:
                    app.logger.error(f'Falha auto-reparo divulgacao: {e}')

            db.session.commit()
            # exercise_section e exercise_question.section_id
            tables = set(insp.get_table_names())
            if 'exercise_topic' in tables:
                if 'exercise_section' not in tables:
                    try:
                        db.session.execute(text('''
                            CREATE TABLE exercise_section (
                                id INTEGER PRIMARY KEY,
                                topic_id INTEGER NOT NULL,
                                nome VARCHAR(180) NOT NULL,
                                descricao TEXT,
                                ordem INTEGER,
                                created_at DATETIME,
                                CONSTRAINT uix_topic_section_nome UNIQUE (topic_id, nome)
                            )
                        '''))
                        db.session.execute(text('CREATE INDEX IF NOT EXISTS ix_exercise_section_topic_id ON exercise_section(topic_id)'))
                        app.logger.warning('Auto-reparo: criada tabela exercise_section')
                    except Exception as e:
                        app.logger.error(f'Falha criando exercise_section: {e}')
                # coluna section_id em exercise_question
                if 'exercise_question' in tables and not has_column('exercise_question','section_id'):
                    try:
                        db.session.execute(text('ALTER TABLE exercise_question ADD COLUMN section_id INTEGER'))
                        app.logger.warning('Auto-reparo: adicionada coluna exercise_question.section_id')
                    except Exception as e:
                        app.logger.error(f'Falha adicionando section_id: {e}')
                db.session.commit()
        except Exception as e:
            # Evita travar startup se algo falhar; loga e segue.
            app.logger.error(f'Falha no auto-reparo de schema: {e}')

        # Normalização de usernames que começam com '@' (ex: '@gramatike' -> 'gramatike')
        try:
            from gramatike_app.models import User as _User
            usuarios_at = _User.query.filter(_User.username.like('@%')).all()
            changed = 0
            for u in usuarios_at:
                novo = u.username.lstrip('@')
                if not _User.query.filter_by(username=novo).first():
                    u.username = novo
                    changed += 1
            if changed:
                db.session.commit()
                app.logger.warning(f'Usernames normalizados (removido @ inicial) total={changed}')
        except Exception as e:
            app.logger.error(f'Falha normalizando usernames com @: {e}')

    # Registre os blueprints
    from gramatike_app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    # Blueprint admin
    from gramatike_app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    # Isentar rotas de API de CSRF (para chamadas JSON/fetch) mantendo proteção nos formulários
    if csrf is not None:
        try:
            with app.app_context():
                for rule in app.url_map.iter_rules():
                    if rule.rule.startswith('/api/'):
                        view_func = app.view_functions.get(rule.endpoint)
                        if view_func:
                            try:
                                csrf.exempt(view_func)
                            except Exception:
                                pass
        except Exception as _e:
            app.logger.warning(f'Falha ao isentar APIs de CSRF: {_e}')

    # Importe o login.py
    import gramatike_app.login

    # Geração automática de ícones PWA (caso ausentes)
    def _ensure_pwa_icons():
        try:
            import os
            from PIL import Image, ImageDraw, ImageFont
            base_dir = os.path.join(app.root_path, 'static', 'img', 'icons')
            os.makedirs(base_dir, exist_ok=True)
            targets = [(192, 'icon-192.png'), (512, 'icon-512.png')]
            for size, name in targets:
                path = os.path.join(base_dir, name)
                need = False
                try:
                    im = Image.open(path)
                    im.verify()
                    # se tamanho errado, regera
                    im = Image.open(path)
                    if im.size != (size, size):
                        need = True
                except Exception:
                    need = True
                if not need:
                    continue
                # cria gradiente simples
                im = Image.new('RGBA', (size, size), (155,93,229,255))
                draw = ImageDraw.Draw(im)
                # canto arredondado via máscara simples
                try:
                    r = int(size*0.225)
                    mask = Image.new('L', (size, size), 0)
                    mdraw = ImageDraw.Draw(mask)
                    mdraw.rounded_rectangle([0,0,size,size], radius=r, fill=255)
                    bg = Image.new('RGBA', (size, size))
                    # gradiente diagonal
                    for y in range(size):
                        for x in range(size):
                            t = (x+y)/(2*size)
                            # interpola roxo -> rosa -> amarelo
                            if t < 0.5:
                                u = t*2
                                r1,g1,b1 = (155,93,229)
                                r2,g2,b2 = (247,168,184)
                            else:
                                u = (t-0.5)*2
                                r1,g1,b1 = (247,168,184)
                                r2,g2,b2 = (255,219,79)
                            rr = int(r1 + (r2-r1)*u)
                            gg = int(g1 + (g2-g1)*u)
                            bb = int(b1 + (b2-b1)*u)
                            bg.putpixel((x,y), (rr,gg,bb,255))
                    im = Image.composite(bg, im, mask)
                except Exception:
                    pass
                # círculo suave
                try:
                    c = int(size*0.5)
                    radii = [int(size*0.37), int(size*0.27)]
                    for idx,rad in enumerate(radii):
                        alpha = int(48 if idx==0 else 38)
                        draw.ellipse([c-rad, c-rad, c+rad, c+rad], fill=(255,255,255,alpha))
                except Exception:
                    pass
                # letra L estilizada central
                try:
                    txt = 'L'
                    # tenta uma fonte padrão; fallback para default
                    font_size = int(size*0.5)
                    try:
                        font = ImageFont.truetype("arial.ttf", font_size)
                    except Exception:
                        font = ImageFont.load_default()
                    tw, th = draw.textsize(txt, font=font)
                    draw.text(((size-tw)//2, (size-th)//2), txt, fill=(255,255,255,255), font=font)
                except Exception:
                    pass
                im.convert('RGB').save(path, format='PNG')
        except Exception as _e:
            app.logger.warning(f"Falha ao gerar ícones PWA: {_e}")

    try:
        _ensure_pwa_icons()
    except Exception:
        pass

    # --- Security headers ---
    @app.after_request
    def add_security_headers(resp):
        resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
        resp.headers.setdefault('X-Frame-Options', 'DENY')
        resp.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        resp.headers.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
        # CSP brando para não quebrar inline scripts atuais; ajuste futuramente para remover 'unsafe-inline'
        # Permitir Google Fonts e imagens externas (ex.: Supabase Storage)
        csp = (
            "default-src 'self'; "
            "img-src 'self' https: data: blob:; "
            "media-src 'self' https: data:; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'; "
            "report-uri /api/csp-report;"
        )
        resp.headers.setdefault('Content-Security-Policy', csp)
        # Report-Only mais estrito para avaliar remoção de inline no futuro (não bloqueia, apenas reporta)
        ro_csp = (
            "default-src 'self'; "
            "img-src 'self' https: data: blob:; "
            "media-src 'self' https: data:; "
            "style-src 'self' https://fonts.googleapis.com; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            "script-src 'self'; connect-src 'self' https:; "
            "frame-ancestors 'none'; report-uri /api/csp-report;"
        )
        resp.headers.setdefault('Content-Security-Policy-Report-Only', ro_csp)
        return resp

    # Simples tratador 500 para evitar página em branco
    @app.errorhandler(500)
    def _handle_500(e):
        try:
            app.logger.error(f"Erro 500: {e}")
        except Exception:
            pass
        return ("Erro interno no servidor.", 500, {'Content-Type': 'text/plain; charset=utf-8'})

    # --- Rate limiting simples por endpoint/IP ---
    # Formato: endpoint -> (limite, janela_em_segundos)
    app.config.setdefault('RATE_LIMITS', {
        'main.create_post': (10, 60),          # 10 posts/min por IP/usuárie
        'main.comentarios': (20, 60),          # 20 comentários/min
    'main.login': (10, 300),               # 10 tentativas/5min para reduzir falsos positivos ao digitar senha
        'main.admin_divulgacao_upload': (5, 300), # 5 uploads/5min
    })
    # Por padrão, limite aplica a todos os métodos; para endpoints sensíveis, restringimos a POST
    app.config.setdefault('RATE_LIMIT_METHODS', {
        'main.login': {'POST'},
        'main.create_post': {'POST'},
        'main.comentarios': {'POST'},
        'main.admin_divulgacao_upload': {'POST'},
        # entradas Lune removidas
    })
    from time import time
    from collections import defaultdict
    app.rate_counters = defaultdict(list)

    @app.before_request
    def simple_rate_limiter():
        try:
            from flask import request
            endpoint = request.endpoint or ''
            rules = app.config.get('RATE_LIMITS', {})
            if endpoint not in rules:
                return None
            # Verifica método permitido para rate limit neste endpoint
            methods_map = app.config.get('RATE_LIMIT_METHODS', {})
            allowed = methods_map.get(endpoint)
            if allowed and request.method not in allowed:
                return None
            limit, window = rules[endpoint]
            # Chave por IP + usuário (se autenticado)
            ip = request.headers.get('X-Forwarded-For', request.remote_addr) or '0.0.0.0'
            user_part = ''
            try:
                from flask_login import current_user
                if getattr(current_user, 'is_authenticated', False):
                    user_part = f"u{current_user.id}"
            except Exception:
                pass
            key = f"{endpoint}:{ip}:{user_part}"
            now = time()
            bucket = app.rate_counters[key]
            # remove timestamps fora da janela
            cutoff = now - window
            i = 0
            for i in range(len(bucket)):
                if bucket[i] >= cutoff:
                    break
            if i > 0:
                del bucket[:i]
            # verifica limite
            if len(bucket) >= limit:
                from flask import jsonify
                retry_after = max(1, int(bucket[0] + window - now))
                resp = jsonify({'error': 'rate_limited', 'retry_after': retry_after})
                resp.status_code = 429
                resp.headers['Retry-After'] = str(retry_after)
                return resp
            bucket.append(now)
        except Exception:
            # Em caso de erro, não bloquear requisição
            return None
        return None

    return app