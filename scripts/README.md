# 📜 Scripts de Setup e Manutenção

Este diretório contém scripts úteis para configurar e manter o Gramátike.

## 🚀 Scripts Disponíveis

### 1. `setup-inicial.sh` - Setup Completo Interativo

Script interativo que configura tudo do zero.

**Uso:**
```bash
bash scripts/setup-inicial.sh
```

**O que faz:**
- ✅ Verifica Node.js e npm
- ✅ Instala dependências
- ✅ Verifica autenticação Wrangler
- ✅ Verifica banco D1
- ✅ Opcionalmente aplica o schema

**Quando usar:** Primeira vez configurando o projeto

---

### 2. `setup-com-api-token.sh` - Setup com API Token

Usa um API token do Cloudflare para configurar o banco D1.

**Uso:**
```bash
bash scripts/setup-com-api-token.sh
```

**O que faz:**
- ✅ Autentica com API token
- ✅ Lista bancos D1
- ✅ Aplica schema no banco gramatike
- ✅ Verifica tabelas criadas

**Quando usar:** Quando você tem um API token e quer configurar rapidamente

**Nota:** Edite o arquivo para adicionar seu token, ou:
```bash
export CLOUDFLARE_API_TOKEN="seu-token-aqui"
bash scripts/setup-com-api-token.sh
```

---

### 3. `migrate-schema.sh` - Migração de Schema

Aplica o schema SQL no banco D1 (local e/ou remoto).

**Uso:**
```bash
bash scripts/migrate-schema.sh
```

**O que faz:**
- ✅ Verifica autenticação
- ✅ Aplica schema localmente
- ✅ Pergunta se quer aplicar em produção
- ✅ Requer confirmação para produção (proteção contra acidentes)

**Quando usar:** 
- Atualizar schema do banco
- Resetar banco de desenvolvimento
- Aplicar mudanças de schema em produção

**⚠️ AVISO:** Este script RECRIA as tabelas, apagando todos os dados!

---

## 📚 Documentação Relacionada

Consulte também:
- [GUIA_SETUP_DB.md](../GUIA_SETUP_DB.md) - Guia completo passo a passo
- [SETUP_RAPIDO_API_TOKEN.md](../SETUP_RAPIDO_API_TOKEN.md) - Setup rápido com token
- [README.md](../README.md) - Documentação geral do projeto
- [SETUP.md](../SETUP.md) - Instruções de deploy

---

## 🛠️ Executando os Scripts

Todos os scripts devem ser executados da raiz do projeto:

```bash
# Correto ✅
cd /caminho/para/gramatike
bash scripts/setup-inicial.sh

# Errado ❌
cd scripts
bash setup-inicial.sh
```

---

## 🔐 Segurança

**NUNCA** commite API tokens ou credenciais nos scripts!

Use variáveis de ambiente:
```bash
export CLOUDFLARE_API_TOKEN="seu-token"
bash scripts/setup-com-api-token.sh
unset CLOUDFLARE_API_TOKEN
```

Ou arquivos `.env` (já incluídos no .gitignore):
```bash
echo "CLOUDFLARE_API_TOKEN=seu-token" > .env
source .env
bash scripts/setup-com-api-token.sh
```

---

## 💡 Dicas

### Tornar scripts executáveis:
```bash
chmod +x scripts/*.sh
```

### Executar sem bash explícito:
```bash
./scripts/setup-inicial.sh
```

### Debug de scripts:
```bash
bash -x scripts/setup-inicial.sh
```

---

## 🆘 Problemas Comuns

### "Permission denied"
```bash
chmod +x scripts/*.sh
```

### "Command not found: npx"
```bash
npm install
```

### "Not authenticated"
```bash
npx wrangler login
# OU
export CLOUDFLARE_API_TOKEN="seu-token"
```

---

**Precisa de ajuda?** Consulte os guias em português na raiz do projeto! 📖
