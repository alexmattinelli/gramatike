import requests
import json

# Testar se a aplicação está rodando e se a API está funcionando
try:
    # Tentar fazer uma requisição GET para a API de posts
    response = requests.get('http://localhost:5000/api/posts')
    print(f"Status da requisição: {response.status_code}")
    
    if response.status_code == 200:
        posts = response.json()
        print(f"Posts retornados: {len(posts)}")
        for post in posts:
            print(f"- {post.get('usuario', 'N/A')}: {post.get('conteudo', 'N/A')[:50]}...")
    else:
        print(f"Erro na requisição: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("Não foi possível conectar à aplicação. Ela está rodando em localhost:5000?")
except Exception as e:
    print(f"Erro inesperado: {e}")
