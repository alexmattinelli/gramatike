#!/bin/bash
# Script para configurar o banco de dados Cloudflare D1
# Gramátike - Plataforma Educacional de Gramática Portuguesa

set -e

echo "🗄️  Gramátike - Configuração do Banco de Dados D1"
echo "================================================="
echo ""

# Detectar diretório do script e raiz do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Verificar se wrangler está instalado
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler CLI não encontrado."
    echo "   Instale com: npm install -g wrangler"
    echo "   Ou use: npm install (para instalar localmente)"
    exit 1
fi

# Verificar se está autenticado
echo "🔐 Verificando autenticação no Cloudflare..."
if ! wrangler whoami &> /dev/null; then
    echo "❌ Você não está autenticado no Cloudflare."
    echo "   Execute: wrangler login"
    exit 1
fi
echo "✅ Autenticado no Cloudflare"
echo ""

# Nome do banco de dados
DB_NAME="gramatike"

# Verificar se o banco já existe
echo "🔍 Verificando se o banco de dados '$DB_NAME' existe..."
if wrangler d1 list 2>/dev/null | grep -q "$DB_NAME"; then
    echo "✅ Banco de dados '$DB_NAME' encontrado"
else
    echo "📦 Criando banco de dados '$DB_NAME'..."
    wrangler d1 create "$DB_NAME"
    echo ""
    echo "⚠️  IMPORTANTE: Atualize o 'database_id' no arquivo wrangler.toml"
    echo "   com o ID exibido acima."
    echo ""
fi

# Encontrar o arquivo schema
SCHEMA_FILE="$PROJECT_ROOT/schema.d1.sql"
if [ ! -f "$SCHEMA_FILE" ]; then
    SCHEMA_FILE="./schema.d1.sql"
fi

if [ ! -f "$SCHEMA_FILE" ]; then
    echo "❌ Arquivo schema.d1.sql não encontrado!"
    echo "   Procurado em: $PROJECT_ROOT/schema.d1.sql"
    echo "   Certifique-se de estar no diretório raiz do projeto."
    exit 1
fi

# Aplicar o schema
echo ""
echo "📋 Aplicando schema ao banco de dados..."
echo "   Arquivo: $SCHEMA_FILE"
echo ""

wrangler d1 execute "$DB_NAME" --file="$SCHEMA_FILE"

echo ""
echo "✅ Schema aplicado com sucesso!"
echo ""

# Verificar tabelas criadas
echo "📊 Verificando tabelas criadas..."
echo "   (Listando tabelas no banco de dados)"
echo ""
wrangler d1 execute "$DB_NAME" --command="SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"

echo ""
echo "🎉 Configuração do banco de dados concluída!"
echo ""
echo "📝 Próximos passos:"
echo "   1. Verifique se o 'database_id' no wrangler.toml está correto"
echo "   2. Faça o deploy: npm run deploy"
echo "   3. Acesse seu site e teste o login/cadastro"
echo ""
echo "📖 Para mais informações, consulte: CLOUDFLARE_D1_SETUP.md"
