#!/bin/bash
# NOTA: Este script NÃO é usado para Cloudflare Workers deployment!
#
# Cloudflare Workers usa pyproject.toml e uv para gerenciar dependências.
# Este script é mantido apenas para desenvolvimento local ou deploys não-Workers.
#
# Para deployment correto:
#   npm run deploy
#
# Veja: CLOUDFLARE_DEPLOYMENT_GUIDE.md

echo "⚠️  AVISO: Este script não é usado para Cloudflare Workers deployment!"
echo "Para deployment correto, use: npm run deploy"
echo ""
echo "Este script é apenas para desenvolvimento local."
echo ""

pip install -r requirements.txt

