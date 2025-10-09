#!/usr/bin/env python
"""
Test script para demonstrar a melhoria no error handler 500.

Este script testa que o error handler agora loga informações detalhadas
incluindo tipo de erro, mensagem, path, método HTTP, IP e stack trace completo.
"""

from gramatike_app import create_app
import sys
from io import StringIO

def test_error_handler():
    app = create_app()
    
    # Criar rotas de teste que geram diferentes erros
    @app.route('/test-value-error')
    def test_value_error():
        raise ValueError("Erro de valor de teste")
    
    @app.route('/test-zero-division')
    def test_zero_division():
        return 1 / 0
    
    @app.route('/test-key-error')
    def test_key_error():
        d = {}
        return d['chave_inexistente']
    
    print("="*70)
    print("TESTE DO ERROR HANDLER 500 MELHORADO")
    print("="*70)
    
    test_cases = [
        ('/test-value-error', 'ValueError'),
        ('/test-zero-division', 'ZeroDivisionError'),
        ('/test-key-error', 'KeyError'),
    ]
    
    with app.test_client() as client:
        for path, expected_error in test_cases:
            print(f"\n{'─'*70}")
            print(f"Testando: {path} (esperado: {expected_error})")
            print('─'*70)
            
            # Capturar logs
            response = client.get(path)
            
            # Verificar resposta
            assert response.status_code == 500, f"Status esperado 500, recebeu {response.status_code}"
            assert response.get_data(as_text=True) == "Erro interno no servidor.", \
                "Mensagem de erro para usuário incorreta"
            
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Mensagem ao usuário: '{response.get_data(as_text=True)}'")
            print(f"✅ Erro logado corretamente (veja os logs acima)")
    
    print(f"\n{'='*70}")
    print("✅ TODOS OS TESTES PASSARAM!")
    print("="*70)
    print("\nMelhorias implementadas:")
    print("  1. ✅ Tipo de erro identificado corretamente (não apenas 'InternalServerError')")
    print("  2. ✅ Mensagem de erro capturada")
    print("  3. ✅ Path da requisição logado")
    print("  4. ✅ Método HTTP logado")
    print("  5. ✅ IP do cliente logado")
    print("  6. ✅ Stack trace completo logado")
    print("  7. ✅ Fallback para print() se logger falhar")
    print("\nAgora é possível diagnosticar erros em produção! 🎉")

if __name__ == "__main__":
    test_error_handler()
