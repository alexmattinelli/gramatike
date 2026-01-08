#!/bin/bash
# Script para aplicar schema no D1 local e remoto
# Gramátike - Database Migration Script

set -e

echo "🔄 Aplicando schema no D1..."
echo ""

# Verificar se wrangler está instalado
if ! command -v wrangler &> /dev/null; then
    echo "❌ Erro: wrangler não está instalado"
    echo "Instale com: npm install -g wrangler"
    exit 1
fi

# Verificar se o arquivo schema existe
if [ ! -f "./schema.d1.sql" ]; then
    echo "❌ Erro: schema.d1.sql não encontrado"
    exit 1
fi

# Aplicar schema localmente
echo "📍 Aplicando schema no D1 local..."
wrangler d1 execute gramatike --local --file=./schema.d1.sql

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
        wrangler d1 execute gramatike --remote --file=./schema.d1.sql
        echo ""
        echo "✅ Schema aplicado com sucesso em produção!"
    else
        echo "❌ Operação cancelada."
        exit 1
    fi
else
    echo ""
    echo "ℹ️  Schema aplicado apenas localmente."
    echo "   Para aplicar em produção manualmente, execute:"
    echo "   wrangler d1 execute gramatike --remote --file=./schema.d1.sql"
fi

echo ""
echo "🎉 Migração concluída!"
