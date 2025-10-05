param(
    [string]$To = "alexmattinelli@outlook.com",
    [string]$FromEmail = "no-reply@gramatike.com.br",
    [string]$FromName = "Gramátike"
)

Write-Host "=== Envio de teste via Brevo (smtp-relay.brevo.com) ===" -ForegroundColor Cyan
# Preferencialmente use a SMTP Key (xsmtpsib-...). Caso não exista, faz fallback para a API Key (xkeysib-...)
$SMTP = $env:BREVO_SMTP_KEY
if (-not $SMTP -or $SMTP -eq "") {
  $SMTP = $env:BREVO_API_KEY
}
if (-not $SMTP -or $SMTP -eq "") {
  $smtpSecure = Read-Host -Prompt "Brevo SMTP Key ou API Key (será mantida somente em memória)" -AsSecureString
  $BSTR = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($smtpSecure)
  $SMTP  = [Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
}

# Configura variáveis de ambiente esperadas pelo app
Set-Item -Path Env:MAIL_SERVER -Value "smtp-relay.brevo.com"
Set-Item -Path Env:MAIL_PORT -Value "587"
Set-Item -Path Env:MAIL_USE_TLS -Value "true"
Set-Item -Path Env:MAIL_USERNAME -Value $SMTP
Set-Item -Path Env:MAIL_PASSWORD -Value $SMTP
Set-Item -Path Env:MAIL_DEFAULT_SENDER -Value $FromEmail
Set-Item -Path Env:MAIL_SENDER_NAME -Value $FromName

# Garante que o Python veja o pacote do app
$root = Split-Path -Parent $PSScriptRoot
Set-Item -Path Env:PYTHONPATH -Value $root
Set-Location -Path $root

# Executa o script diretamente (com sys.path fix interno)
python scripts/send_test_email.py $To `
  --server smtp-relay.brevo.com `
  --port 587 `
  --tls `
  --user $SMTP `
  --password $SMTP `
  --from-email $FromEmail `
  --from-name $FromName

if ($LASTEXITCODE -eq 0) {
  Write-Host "[OK] E-mail de teste enviado para $To via Brevo." -ForegroundColor Green
} else {
  Write-Host "[ERRO] Falha ao enviar. Verifique API Key, domínio verificado (SPF/DKIM) e conexão." -ForegroundColor Red
}
