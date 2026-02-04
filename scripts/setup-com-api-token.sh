#!/bin/bash
# Script para executar o setup do banco D1 usando API Token
# Execute este script no seu computador local

set -e

echo "🔐 Setup do Banco D1 com API Token"
echo "===================================="
echo ""

# API Token (substitua se necessário)
API_TOKEN="CZ_tsTFT-M3-p9aeGyYk136ro4-bu3zMvFw5AiUx"

# Exportar o token como variável de ambiente
export CLOUDFLARE_API_TOKEN="$API_TOKEN"

echo "1️⃣  Verificando autenticação..."
if npx wrangler whoami; then
    echo "✅ Autenticado com sucesso!"
else
    echo "❌ Erro na autenticação"
    echo ""
    echo "Verifique se:"
    echo "  - Você tem conexão com internet"
    echo "  - O token está correto"
    echo "  - O token tem as permissões necessárias"
    exit 1
fi

echo ""
echo "2️⃣  Listando bancos D1 disponíveis..."
npx wrangler d1 list

echo ""
echo "3️⃣  Executando schema no banco 'gramatike'..."
read -p "Deseja continuar e aplicar o schema em PRODUÇÃO? (SIM/não): " confirm

if [ "$confirm" = "SIM" ]; then
    echo ""
    echo "📊 Aplicando schema..."
    npx wrangler d1 execute gramatike --remote --file=./db/schema.sql
    
    echo ""
    echo "✅ Schema aplicado com sucesso!"
    echo ""
    
    echo "🔍 Verificando tabelas criadas..."
    npx wrangler d1 execute gramatike --remote --command "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    
    echo ""
    echo "🎉 Banco de dados configurado!"
    echo ""
    echo "📋 Tabelas criadas:"
    echo "  - users"
    echo "  - posts"
    echo "  - sessions"
    echo "  - password_resets"
    echo "  - post_likes"
    echo "  - post_comments"
else
    echo "❌ Operação cancelada."
fi
