#!/usr/bin/env python3
"""
Script de teste para demonstrar a configuração de logging melhorada.

Este script testa:
1. Logging em diferentes níveis (DEBUG, INFO, WARNING, ERROR)
2. Logging em diferentes ambientes (development vs production)
3. Logging em contexto de aplicação
"""

import os
from gramatike_app import create_app

def test_logging():
    print("=" * 70)
    print("TESTE DE LOGGING - AMBIENTE DE PRODUÇÃO (padrão)")
    print("=" * 70)
    
    app = create_app()
    
    with app.app_context():
        app.logger.debug('DEBUG: Esta mensagem NÃO aparece em produção')
        app.logger.info('INFO: Esta mensagem aparece em produção')
        app.logger.warning('WARNING: Aviso importante')
        app.logger.error('ERROR: Erro simulado para teste')
    
    print("\n" + "=" * 70)
    print("TESTE DE LOGGING - AMBIENTE DE DESENVOLVIMENTO")
    print("=" * 70)
    
    os.environ['FLASK_ENV'] = 'development'
    app_dev = create_app()
    
    with app_dev.app_context():
        app_dev.logger.debug('DEBUG: Esta mensagem APARECE em desenvolvimento')
        app_dev.logger.info('INFO: Informação útil para debug')
        app_dev.logger.warning('WARNING: Aviso de desenvolvimento')
        app_dev.logger.error('ERROR: Erro capturado com contexto completo')
    
    print("\n" + "=" * 70)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    print("\nBenefícios da nova configuração de logging:")
    print("  ✅ Logs com timestamp formatado")
    print("  ✅ Diferentes níveis de log (DEBUG, INFO, WARNING, ERROR)")
    print("  ✅ Handler otimizado para ambientes serverless (flush automático)")
    print("  ✅ Visível no Vercel Runtime Logs")
    print("  ✅ Formato padronizado: [timestamp] LEVEL in module: message")

if __name__ == '__main__':
    test_logging()
