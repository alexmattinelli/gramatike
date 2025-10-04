import json
from gramatike_app import create_app

def test_rag_search_smoke():
    app = create_app()
    client = app.test_client()
    # Não garante resultados, mas garante que a rota responde
    rv = client.get('/api/rag/search?q=gramatica')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'items' in data
    assert isinstance(data['items'], list)
