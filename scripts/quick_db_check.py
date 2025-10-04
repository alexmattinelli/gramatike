from gramatike_app import create_app, db
from gramatike_app.models import Divulgacao

app = create_app()
with app.app_context():
    total = db.session.query(Divulgacao).count()
    idx = db.session.query(Divulgacao).filter_by(area='edu', ativo=True, show_on_index=True).count()
    edu = db.session.query(Divulgacao).filter_by(area='edu', ativo=True, show_on_edu=True).count()
    print({'total': total, 'index_edu': idx, 'edu_page': edu})
