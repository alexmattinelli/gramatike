#!/usr/bin/env python3
import json
from gramatike_app import create_app, db


def run():
    app = create_app()
    with app.app_context():
        client = app.test_client()
        payload = {"conteudo": "Teste de integração: criar post via test_client", "imagem": ""}
        resp = client.post('/api/posts', json=payload)
        print('Status:', resp.status_code)
        try:
            print('JSON:', resp.get_json())
        except Exception:
            print('Response data:', resp.data.decode('utf-8', errors='replace'))


if __name__ == '__main__':
    run()
