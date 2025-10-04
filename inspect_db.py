from gramatike_app import create_app, db
from sqlalchemy import inspect, text
app = create_app()
with app.app_context():
    insp = inspect(db.engine)
    tables = insp.get_table_names()
    for table in ['user','post','divulgacao','edu_content']:
        if table in tables:
            cols = [c['name'] for c in insp.get_columns(table)]
            print(table, 'columns:', cols)
    # show alembic version if exists
    if 'alembic_version' in tables:
        v = db.session.execute(text('select version_num from alembic_version')).scalar()
        print('alembic_version:', v)
