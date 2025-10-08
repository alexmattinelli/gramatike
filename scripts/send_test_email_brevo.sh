#!/bin/bash
# Script para testar envio de email via Brevo (smtp-relay.brevo.com)
# Uso: ./scripts/send_test_email_brevo.sh [email_destino]

TO="${1:-alexmattinelli@outlook.com}"
FROM_EMAIL="${2:-no-reply@gramatike.com.br}"
FROM_NAME="${3:-Gramátike}"

echo "=== Envio de teste via Brevo (smtp-relay.brevo.com) ==="

# Tenta pegar a chave SMTP do ambiente (preferência: BREVO_SMTP_KEY, fallback: BREVO_API_KEY)
SMTP_KEY="${BREVO_SMTP_KEY:-$BREVO_API_KEY}"

if [ -z "$SMTP_KEY" ]; then
  echo "AVISO: BREVO_SMTP_KEY ou BREVO_API_KEY não encontrado no ambiente."
  read -sp "Digite a Brevo SMTP Key ou API Key: " SMTP_KEY
  echo
fi

if [ -z "$SMTP_KEY" ]; then
  echo "[ERRO] Chave SMTP não fornecida. Abortando."
  exit 1
fi

# Configura variáveis de ambiente para o script Python
export MAIL_SERVER="smtp-relay.brevo.com"
export MAIL_PORT="587"
export MAIL_USE_TLS="true"
export MAIL_USERNAME="$SMTP_KEY"
export MAIL_PASSWORD="$SMTP_KEY"
export MAIL_DEFAULT_SENDER="$FROM_EMAIL"
export MAIL_SENDER_NAME="$FROM_NAME"

# Garante que o Python veja o pacote do app
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"

cd "$ROOT_DIR"

# Executa o script de teste
python3 scripts/send_test_email.py "$TO" \
  --server smtp-relay.brevo.com \
  --port 587 \
  --tls \
  --user "$SMTP_KEY" \
  --password "$SMTP_KEY" \
  --from-email "$FROM_EMAIL" \
  --from-name "$FROM_NAME"

if [ $? -eq 0 ]; then
  echo "[OK] E-mail de teste enviado para $TO via Brevo."
else
  echo "[ERRO] Falha ao enviar. Verifique:"
  echo "  1. Chave SMTP está correta (deve começar com xsmtpsib-)"
  echo "  2. Email remetente ($FROM_EMAIL) está verificado no Brevo"
  echo "  3. Domínio tem SPF/DKIM configurado"
  echo "  4. Conexão com smtp-relay.brevo.com:587 está permitida"
  exit 1
fi
