#!/bin/bash
# Script para aplicar schema no D1 local e remoto
# Gramátike - Database Migration Script

set -e

# Database name (default: gramatike, can be overridden with DB_NAME env var)
DB_NAME="${DB_NAME:-gramatike}"

echo "🔄 Aplicando schema no D1..."
echo "📊 Database: $DB_NAME"
echo ""

# Verificar se wrangler está instalado
if ! command -v wrangler &> /dev/null && ! command -v npx &> /dev/null; then
    echo "❌ Erro: wrangler não está instalado"
    echo "Instale com: npm install"
    exit 1
fi

# Usar npx wrangler se wrangler não estiver instalado globalmente
WRANGLER_CMD="wrangler"
if ! command -v wrangler &> /dev/null; then
    WRANGLER_CMD="npx wrangler"
fi

# Verificar se o arquivo schema existe
if [ ! -f "./db/schema.sql" ]; then
    echo "❌ Erro: db/schema.sql não encontrado"
    echo "   O arquivo deve estar em ./db/schema.sql"
    echo "   Verifique se você está executando o script do diretório correto."
    exit 1
fi

# Verificar se está autenticado
echo "🔐 Verificando autenticação..."
if ! $WRANGLER_CMD whoami &> /dev/null; then
    echo "❌ Erro: Você não está autenticado no Wrangler"
    echo ""
    echo "Execute primeiro:"
    echo "  npx wrangler login"
    echo ""
    echo "Depois execute este script novamente."
    exit 1
fi

echo "✅ Autenticado como: $($WRANGLER_CMD whoami 2>&1 | grep -o 'logged in as.*' || echo 'usuário')"
echo ""

# Aplicar schema localmente
echo "📍 Aplicando schema no D1 local..."
$WRANGLER_CMD d1 execute "$DB_NAME" --local --file=./db/schema.sql

echo ""
echo "✅ Schema aplicado com sucesso no ambiente local!"
echo ""

# Perguntar se deseja aplicar em produção
read -p "Deseja aplicar o schema em produção também? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "⚠️  ATENÇÃO: Isso irá RECRIAR todas as tabelas em produção!"
    echo "   Todos os dados atuais serão PERDIDOS."
    echo ""
    read -p "Você tem certeza? Digite 'SIM' para confirmar: " confirm
    
    if [ "$confirm" = "SIM" ]; then
        echo ""
        echo "📍 Aplicando schema no D1 remoto (produção)..."
        $WRANGLER_CMD d1 execute "$DB_NAME" --remote --file=./db/schema.sql
        echo ""
        echo "✅ Schema aplicado com sucesso em produção!"
        echo ""
        echo "🔍 Verificando tabelas criadas..."
        $WRANGLER_CMD d1 execute "$DB_NAME" --remote --command "SELECT name FROM sqlite_master WHERE type='table';" || echo "⚠️  Não foi possível verificar as tabelas"
    else
        echo "❌ Operação cancelada."
        exit 1
    fi
else
    echo ""
    echo "ℹ️  Schema aplicado apenas localmente."
    echo "   Para aplicar em produção manualmente, execute:"
    echo "   npx wrangler d1 execute $DB_NAME --remote --file=./db/schema.sql"
fi

echo ""
echo "🎉 Migração concluída!"
echo ""
echo "📚 Para mais informações, consulte: GUIA_SETUP_DB.md"
