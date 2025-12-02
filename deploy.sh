#!/bin/bash
# Script de Deploy para Cloudflare Workers

echo "🚀 Deploy Gramátike - Cloudflare Workers"
echo "========================================"
echo ""

# Configura token
export CLOUDFLARE_API_TOKEN="VR_NPs75hlB1xC_TLiyj6uhn-piwFHHGJ5bWEAv2"

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
  echo "Tente manualmente:"
  echo "  export CLOUDFLARE_API_TOKEN=\"VR_NPs75hlB1xC_TLiyj6uhn-piwFHHGJ5bWEAv2\""
  echo "  npx wrangler deploy"
fi
