#!/bin/bash
# Script de setup inicial completo para o Gramátike
# Este script verifica e configura tudo que você precisa

set -e

echo "🚀 Gramátike - Setup Inicial"
echo "============================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para printar em verde
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Função para printar em vermelho
error() {
    echo -e "${RED}❌ $1${NC}"
}

# Função para printar em amarelo
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Verificar Node.js
echo "1️⃣  Verificando Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    success "Node.js instalado: $NODE_VERSION"
else
    error "Node.js não está instalado!"
    echo "   Instale em: https://nodejs.org/"
    exit 1
fi
echo ""

# 2. Verificar npm
echo "2️⃣  Verificando npm..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm -v)
    success "npm instalado: v$NPM_VERSION"
else
    error "npm não está instalado!"
    exit 1
fi
echo ""

# 3. Instalar dependências
echo "3️⃣  Instalando dependências..."
if [ -f "package.json" ]; then
    npm install
    success "Dependências instaladas!"
else
    error "package.json não encontrado!"
    exit 1
fi
echo ""

# 4. Verificar autenticação Wrangler
echo "4️⃣  Verificando autenticação Wrangler..."
if npx wrangler whoami &> /dev/null; then
    USER_INFO=$(npx wrangler whoami 2>&1 | grep -o 'logged in as.*' || echo "autenticado")
    success "Wrangler autenticado: $USER_INFO"
    AUTHENTICATED=true
else
    warning "Wrangler não está autenticado!"
    echo ""
    echo "   Para autenticar, execute:"
    echo "   npx wrangler login"
    echo ""
    read -p "Deseja fazer login agora? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npx wrangler login
        if npx wrangler whoami &> /dev/null; then
            success "Login realizado com sucesso!"
            AUTHENTICATED=true
        else
            error "Falha no login. Tente novamente manualmente."
            AUTHENTICATED=false
        fi
    else
        warning "Pulando autenticação. Você precisará fazer isso depois."
        AUTHENTICATED=false
    fi
fi
echo ""

# 5. Verificar banco D1
if [ "$AUTHENTICATED" = true ]; then
    echo "5️⃣  Verificando banco D1..."
    if npx wrangler d1 list 2>&1 | grep -q "gramatike"; then
        success "Banco D1 'gramatike' encontrado!"
        DB_EXISTS=true
    else
        warning "Banco D1 'gramatike' não encontrado!"
        echo ""
        read -p "Deseja criar o banco agora? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            npx wrangler d1 create gramatike
            success "Banco criado!"
            warning "IMPORTANTE: Copie o database_id e atualize o wrangler.toml"
            DB_EXISTS=true
        else
            warning "Pulando criação do banco."
            DB_EXISTS=false
        fi
    fi
    echo ""
else
    warning "Pulando verificação do banco (não autenticado)"
    DB_EXISTS=false
    echo ""
fi

# 6. Aplicar schema
if [ "$AUTHENTICATED" = true ] && [ "$DB_EXISTS" = true ]; then
    echo "6️⃣  Configurando schema do banco..."
    read -p "Deseja aplicar o schema no banco agora? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "Escolha o ambiente:"
        echo "  1) Apenas local (desenvolvimento)"
        echo "  2) Apenas remoto (produção)"
        echo "  3) Ambos"
        read -p "Opção (1/2/3): " -n 1 -r ENV_CHOICE
        echo
        echo ""
        
        case $ENV_CHOICE in
            1)
                echo "Aplicando schema localmente..."
                npx wrangler d1 execute gramatike --local --file=./db/schema.sql
                success "Schema aplicado no ambiente local!"
                ;;
            2)
                warning "ATENÇÃO: Isso vai recriar as tabelas em produção!"
                read -p "Tem certeza? (SIM/não): " confirm
                if [ "$confirm" = "SIM" ]; then
                    npx wrangler d1 execute gramatike --remote --file=./db/schema.sql
                    success "Schema aplicado em produção!"
                else
                    warning "Operação cancelada."
                fi
                ;;
            3)
                echo "Aplicando schema localmente..."
                npx wrangler d1 execute gramatike --local --file=./db/schema.sql
                success "Schema aplicado no ambiente local!"
                echo ""
                warning "Aplicando em produção..."
                read -p "Tem certeza? (SIM/não): " confirm
                if [ "$confirm" = "SIM" ]; then
                    npx wrangler d1 execute gramatike --remote --file=./db/schema.sql
                    success "Schema aplicado em produção!"
                else
                    warning "Schema aplicado apenas localmente."
                fi
                ;;
            *)
                warning "Opção inválida. Pulando aplicação do schema."
                ;;
        esac
    fi
    echo ""
else
    warning "Pulando configuração do schema (pré-requisitos não atendidos)"
    echo ""
fi

# 7. Resumo final
echo "========================================"
echo "📋 RESUMO DO SETUP"
echo "========================================"
echo ""

if [ "$AUTHENTICATED" = true ]; then
    success "Wrangler autenticado"
else
    error "Wrangler NÃO autenticado - execute: npx wrangler login"
fi

if [ "$DB_EXISTS" = true ]; then
    success "Banco D1 configurado"
else
    error "Banco D1 NÃO configurado - veja GUIA_SETUP_DB.md"
fi

echo ""
echo "📚 Próximos passos:"
echo ""
echo "   • Para iniciar o servidor local:"
echo "     npm run dev"
echo ""
echo "   • Para fazer deploy:"
echo "     npm run deploy"
echo ""
echo "   • Para configurar o banco manualmente:"
echo "     Veja o arquivo GUIA_SETUP_DB.md"
echo ""
echo "   • Para executar o schema:"
echo "     npm run db:init"
echo ""

success "Setup inicial concluído! 🎉"
