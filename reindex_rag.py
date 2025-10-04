from gramatike_app import create_app
from gramatike_app.utils.rag_embeddings import build_index_from_db, index_exists

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        print('INDEX_EXISTS_BEFORE =', index_exists())
        n, dim = build_index_from_db()
        print('REINDEXED:', n, 'chunks; dim =', dim)
