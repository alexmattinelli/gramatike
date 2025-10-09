# 📊 Guia Rápido: Sistema de Logging

## 🎯 Como Usar Logging no Gramátike

### Importar e usar:
```python
from flask import current_app

# Info (operações normais)
current_app.logger.info('Usuário fez login')
current_app.logger.info(f'API retornou {len(items)} itens')

# Warning (situações incomuns mas não críticas)
current_app.logger.warning('Cache miss, buscando do BD')
current_app.logger.warning(f'Thumbnail falhou: {erro}')

# Error (erros que precisam atenção)
current_app.logger.error('Falha ao salvar no banco')
current_app.logger.error(f'Erro ao processar item id={id}: {erro}')

# Debug (só em desenvolvimento)
current_app.logger.debug(f'Estado: {estado}')
```

## 📋 Níveis de Log

| Nível | Produção | Desenvolvimento | Quando Usar |
|-------|----------|-----------------|-------------|
| DEBUG | ❌ Oculto | ✅ Visível | Detalhes internos, variáveis |
| INFO | ✅ Visível | ✅ Visível | Operações normais, rastreamento |
| WARNING | ✅ Visível | ✅ Visível | Situações incomuns, fallbacks |
| ERROR | ✅ Visível | ✅ Visível | Erros, exceções, falhas |

## 🔍 Formato dos Logs

```
[2025-10-09 19:35:18] INFO in module: Mensagem aqui
[YYYY-MM-DD HH:MM:SS] LEVEL in module: message
```

## 🧪 Testar Localmente

```bash
# Produção (INFO+)
python3 test_logging.py

# Desenvolvimento (DEBUG+)
FLASK_ENV=development python3 test_logging.py
```

## 🚀 Ver Logs no Vercel

1. Dashboard Vercel → Deployments
2. Selecione deployment → Runtime Logs
3. Logs aparecem em tempo real com timestamps

## ❌ Não Faça

```python
# ❌ NÃO use print()
print('Alguma coisa')

# ❌ NÃO use string formatting sem f-string
current_app.logger.info('Valor: ' + str(valor))

# ❌ NÃO logue senhas ou dados sensíveis
current_app.logger.info(f'Senha: {senha}')  # NUNCA!
```

## ✅ Faça

```python
# ✅ Use logger com f-strings
current_app.logger.info(f'Valor processado: {valor}')

# ✅ Adicione contexto (IDs, nomes)
current_app.logger.error(f'Erro ao processar post id={post_id}: {erro}')

# ✅ Use níveis apropriados
current_app.logger.info('Operação concluída')    # Normal
current_app.logger.warning('Fallback usado')     # Incomum
current_app.logger.error('Falha ao salvar')      # Erro
```

## 📚 Documentação Completa

Ver: [LOGGING_IMPROVEMENTS.md](LOGGING_IMPROVEMENTS.md)
