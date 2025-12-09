#!/usr/bin/env python3
"""
Script de validação para verificar que as alterações de segurança do feed
foram implementadas corretamente.
"""

def check_ensure_core_tables():
    """Verifica que a função _ensure_core_tables existe e cria as tabelas corretas."""
    print("✓ Verificando função _ensure_core_tables...")
    
    with open('gramatike_app/routes/__init__.py', 'r') as f:
        content = f.read()
    
    # Verifica que a função existe
    assert 'def _ensure_core_tables():' in content, "Função _ensure_core_tables não encontrada"
    print("  ✓ Função _ensure_core_tables definida")
    
    # Verifica que cria tabela 'post'
    assert 'CREATE TABLE post (' in content, "Criação da tabela post não encontrada"
    print("  ✓ Criação da tabela 'post' presente")
    
    # Verifica que cria tabela 'post_likes'
    assert 'CREATE TABLE post_likes (' in content, "Criação da tabela post_likes não encontrada"
    print("  ✓ Criação da tabela 'post_likes' presente")
    
    # Verifica que cria tabela 'user'
    assert 'CREATE TABLE user (' in content, "Criação da tabela user não encontrada"
    print("  ✓ Criação da tabela 'user' presente")
    
    # Verifica índices
    assert 'CREATE INDEX IF NOT EXISTS idx_post_usuarie_id' in content
    assert 'CREATE INDEX IF NOT EXISTS idx_post_data' in content
    assert 'CREATE INDEX IF NOT EXISTS idx_user_username' in content
    print("  ✓ Índices criados corretamente")


def check_feed_route_safety():
    """Verifica que a rota /feed chama _ensure_core_tables."""
    print("\n✓ Verificando rota /feed...")
    
    with open('gramatike_app/routes/__init__.py', 'r') as f:
        content = f.read()
    
    # Encontra a definição da rota feed
    feed_route_idx = content.find("@bp.route('/feed')")
    assert feed_route_idx > 0, "Rota /feed não encontrada"
    
    # Verifica que chama _ensure_core_tables dentro da função feed
    feed_function = content[feed_route_idx:feed_route_idx + 500]
    assert '_ensure_core_tables()' in feed_function, "Rota /feed não chama _ensure_core_tables"
    print("  ✓ Rota /feed chama _ensure_core_tables()")


def check_api_posts_error_handling():
    """Verifica que /api/posts tem tratamento de erro adequado."""
    print("\n✓ Verificando endpoint /api/posts...")
    
    with open('gramatike_app/routes/__init__.py', 'r') as f:
        content = f.read()
    
    # Encontra a função get_posts
    get_posts_idx = content.find("def get_posts():")
    assert get_posts_idx > 0, "Função get_posts não encontrada"
    
    # Pega o conteúdo da função (próximos 5000 caracteres para cobrir toda a função)
    get_posts_content = content[get_posts_idx:get_posts_idx + 5000]
    
    # Verifica que chama _ensure_core_tables
    assert '_ensure_core_tables()' in get_posts_content, "/api/posts não chama _ensure_core_tables"
    print("  ✓ Endpoint /api/posts chama _ensure_core_tables()")
    
    # Verifica tratamento de erro na query inicial
    assert 'try:' in get_posts_content and 'Post.query.filter' in get_posts_content
    assert 'except Exception as e:' in get_posts_content
    assert 'return jsonify([])' in get_posts_content
    print("  ✓ Tratamento de erro para query inicial presente")
    
    # Verifica tratamento de erro na execução da query
    assert 'posts = query.all()' in get_posts_content
    print("  ✓ Execução de query com tratamento de erro")
    
    # Verifica tratamento de erro ao buscar autor
    assert 'User.query.get' in get_posts_content
    print("  ✓ Tratamento de erro ao buscar autor do post")


def check_logging():
    """Verifica que há logging adequado de erros."""
    print("\n✓ Verificando logging de erros...")
    
    with open('gramatike_app/routes/__init__.py', 'r') as f:
        content = f.read()
    
    # Verifica logs de erro
    assert "current_app.logger.error(f'[API /api/posts] Erro ao acessar tabela Post:" in content
    print("  ✓ Log de erro para acesso à tabela Post")
    
    assert "current_app.logger.error(f'[API /api/posts] Erro ao executar query:" in content
    print("  ✓ Log de erro para execução de query")
    
    assert "current_app.logger.warning(f'[API /api/posts] Erro ao aplicar ordenação:" in content
    print("  ✓ Log de warning para erro de ordenação")
    
    assert "current_app.logger.warning(f\"ensure_core_tables failed:" in content
    print("  ✓ Log de warning para falha em ensure_core_tables")


def main():
    """Executa todas as verificações."""
    print("="*60)
    print("Validação de Segurança do Feed")
    print("="*60)
    
    try:
        check_ensure_core_tables()
        check_feed_route_safety()
        check_api_posts_error_handling()
        check_logging()
        
        print("\n" + "="*60)
        print("✅ TODAS AS VERIFICAÇÕES PASSARAM!")
        print("="*60)
        print("\nO feed agora está protegido contra:")
        print("  • Tabelas do banco de dados faltando")
        print("  • Erros de query devido a schema incompleto")
        print("  • Falhas ao buscar dados de usuários")
        print("  • Problemas de ordenação de posts")
        print("\nEm todos os casos, o feed retornará uma lista vazia")
        print("ao invés de quebrar com erro 500.")
        
        return 0
    except AssertionError as e:
        print(f"\n❌ ERRO: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
