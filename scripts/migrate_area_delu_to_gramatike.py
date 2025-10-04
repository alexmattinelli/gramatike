#!/usr/bin/env python
import os
import sys
from datetime import datetime

# Ensure project root on path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Precarrega 'config' para que gramatike_app.__init__ consiga importar
import importlib.util
config_path = os.path.join(ROOT, 'config.py')
if 'config' not in sys.modules and os.path.exists(config_path):
    spec = importlib.util.spec_from_file_location('config', config_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    sys.modules['config'] = module

from gramatike_app import create_app
from gramatike_app.models import db, Divulgacao


def run():
    try:
        app = create_app()
        with app.app_context():
            total = Divulgacao.query.filter_by(area='delu').count()
            if total == 0:
                print('Nenhum registro com area=delu encontrado. Nada a migrar.')
                return
            print(f'Encontrados {total} registros com area=delu. Migrando para area=gramatike...')
            updated = 0
            batch = Divulgacao.query.filter_by(area='delu').all()
            for d in batch:
                d.area = 'gramatike'
                d.updated_at = datetime.utcnow()
                updated += 1
            db.session.commit()
            print(f'Migração concluída. Atualizados: {updated}.')
            return
    except Exception as e:
        print(f"Falha usando Flask/SQLAlchemy: {e}\nTentando fallback via sqlite3...")
    # Fallback: tentar migrar diretamente via sqlite3
    import sqlite3
    # Preferir DATABASE_URL se setado e sqlite
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/app.db')
    if db_url.startswith('sqlite:///'):
        rel = db_url.replace('sqlite:///', '', 1)
        db_path = rel if os.path.isabs(rel) else os.path.join(ROOT, rel)
    elif db_url.startswith('sqlite:'):
        # Outros formatos sqlite:
        db_path = db_url.split(':', 1)[-1]
    else:
        print('DATABASE_URL não é sqlite; fallback não suportado. Configure e rode pelo app.')
        return
    if not os.path.exists(db_path):
        print(f'Banco não encontrado em {db_path}. Abortando.')
        return
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("UPDATE divulgacao SET area='gramatike' WHERE area='delu'")
        conn.commit()
        print(f'Fallback OK. Linhas alteradas: {conn.total_changes}.')
    finally:
        conn.close()


if __name__ == '__main__':
    run()
