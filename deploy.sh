#!/bin/bash
# Script de Deploy para Cloudflare Workers

echo "🚀 Deploy Gramátike - Cloudflare Workers"
echo "========================================"
echo ""

# Token deve ser configurado via variável de ambiente
# NÃO adicione tokens diretamente no código!
# Configure via: export CLOUDFLARE_API_TOKEN="seu-token-aqui"

if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
  echo "❌ CLOUDFLARE_API_TOKEN não definido!"
  echo ""
  echo "Configure o token antes de executar:"
  echo "  export CLOUDFLARE_API_TOKEN=\"seu-token-aqui\""
  echo ""
  echo "Ou use wrangler login:"
  echo "  npx wrangler login"
  exit 1
fi

# Testa token
echo "🔐 Testando autenticação..."
curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | grep -q "success.*true"

if [ $? -eq 0 ]; then
  echo "✅ Token válido!"
  echo ""
  
  # Deploy
  echo "📦 Fazendo deploy..."
  npx wrangler deploy
  
  if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ DEPLOY COMPLETO!"
    echo "========================================"
    echo ""
    echo "🌐 Teste as páginas:"
    echo "   • https://www.gramatike.com.br/configuracoes"
    echo "   • https://www.gramatike.com.br/suporte"
    echo "   • https://www.gramatike.com.br/perfil"
    echo ""
  else
    echo ""
    echo "❌ Erro no deploy. Verifique os logs acima."
  fi
else
  echo "❌ Token inválido ou erro na API"
  echo ""
  echo "Tente fazer login manualmente:"
  echo "  npx wrangler login"
fi
