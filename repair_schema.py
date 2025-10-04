from gramatike_app import create_app, db
from sqlalchemy import inspect, text
from datetime import datetime
import os

TARGET_REV = 'c1d2e3f4g5h6'  # ajuste se existir em migrations/versions

LOG_PATH = os.path.join(os.path.dirname(__file__), 'repair_schema.log')

def log(msg):
    ts = datetime.utcnow().isoformat()
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass

app = create_app()
with app.app_context():
    log('Iniciando reparo de schema')
    insp = inspect(db.engine)
    tables = insp.get_table_names()
    log(f'Tabelas encontradas: {tables}')

    def has_column(table, name):
        return any(c['name'] == name for c in insp.get_columns(table))

    # user.created_at
    if 'user' in tables and not has_column('user', 'created_at'):
        log('> Adicionando user.created_at')
        db.session.execute(text('ALTER TABLE user ADD COLUMN created_at DATETIME'))
        db.session.execute(text('UPDATE user SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL'))
        try:
            db.session.execute(text('CREATE INDEX IF NOT EXISTS ix_user_created_at ON user (created_at)'))
        except Exception:
            pass

    # post soft delete columns
    if 'post' in tables:
        if not has_column('post', 'is_deleted'):
            log('> Adicionando post.is_deleted')
            db.session.execute(text('ALTER TABLE post ADD COLUMN is_deleted BOOLEAN DEFAULT 0'))
            db.session.execute(text('UPDATE post SET is_deleted = 0 WHERE is_deleted IS NULL'))
            try:
                db.session.execute(text('CREATE INDEX IF NOT EXISTS ix_post_is_deleted ON post (is_deleted)'))
            except Exception:
                pass
        if not has_column('post', 'deleted_at'):
            log('> Adicionando post.deleted_at')
            db.session.execute(text('ALTER TABLE post ADD COLUMN deleted_at DATETIME'))
        if not has_column('post', 'deleted_by'):
            log('> Adicionando post.deleted_by')
            db.session.execute(text('ALTER TABLE post ADD COLUMN deleted_by INTEGER'))

    # divulgacao show_on flags (Lune flag descontinuado)
    if 'divulgacao' in tables:
        if not has_column('divulgacao', 'show_on_edu'):
            log('> Adicionando divulgacao.show_on_edu')
            db.session.execute(text('ALTER TABLE divulgacao ADD COLUMN show_on_edu BOOLEAN DEFAULT 1'))
        if not has_column('divulgacao', 'show_on_index'):
            log('> Adicionando divulgacao.show_on_index')
            db.session.execute(text('ALTER TABLE divulgacao ADD COLUMN show_on_index BOOLEAN DEFAULT 1'))

    # Ajustar versão Alembic se a revisão alvo existir
    import re
    versions_path = os.path.join(os.path.dirname(__file__), 'migrations', 'versions')
    existing_revisions = set()
    if os.path.isdir(versions_path):
        for fname in os.listdir(versions_path):
            m = re.match(r'([0-9a-f]+)_', fname)
            if m:
                existing_revisions.add(m.group(1))
    else:
        log(f'Diretório de versions não encontrado: {versions_path}')

    if 'alembic_version' in tables:
        try:
            cur_ver = db.session.execute(text('SELECT version_num FROM alembic_version')).scalar()
            log(f'Versão Alembic atual: {cur_ver}')
        except Exception:
            cur_ver = None
        if TARGET_REV in existing_revisions and cur_ver and cur_ver != TARGET_REV:
            log(f'> Atualizando alembic_version para {TARGET_REV}')
            db.session.execute(text('UPDATE alembic_version SET version_num = :v'), {'v': TARGET_REV})
        elif TARGET_REV not in existing_revisions:
            log(f'> Revision alvo {TARGET_REV} não existe; mantendo atual.')
    else:
        log('Tabela alembic_version inexistente.')
        if TARGET_REV in existing_revisions:
            log(f'> Criando tabela alembic_version e setando para {TARGET_REV}')
            db.session.execute(text('CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)'))
            db.session.execute(text('INSERT INTO alembic_version (version_num) VALUES (:v)'), {'v': TARGET_REV})
        elif existing_revisions:
            chosen = sorted(existing_revisions)[-1]
            log(f'> Criando tabela alembic_version e setando para head existente {chosen}')
            db.session.execute(text('CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)'))
            db.session.execute(text('INSERT INTO alembic_version (version_num) VALUES (:v)'), {'v': chosen})
        else:
            log('> Sem migrations detectadas; criando tabela alembic_version com placeholder base')
            db.session.execute(text('CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)'))
            db.session.execute(text("INSERT INTO alembic_version (version_num) VALUES ('base')"))

    db.session.commit()
    log('Reparo concluído.')

log('Fim do script.')
