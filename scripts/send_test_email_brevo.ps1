param(
    [string]$To = "alexmattinelli@outlook.com",
    [string]$FromEmail = "no-reply@gramatike.com.br",
    [string]$FromName = "Gramátike"
)

Write-Host "=== Envio de teste via Brevo (smtp-relay.brevo.com) ===" -ForegroundColor Cyan
# Usa variável de ambiente se disponível; senão, solicita
$API = $env:BREVO_API_KEY
if (-not $API -or $API -eq "") {
  $apiSecure = Read-Host -Prompt "Brevo API Key (será mantida somente em memória)" -AsSecureString
  $BSTR = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiSecure)
  $API  = [Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
}

# Configura variáveis de ambiente esperadas pelo app
Set-Item -Path Env:MAIL_SERVER -Value "smtp-relay.brevo.com"
Set-Item -Path Env:MAIL_PORT -Value "587"
Set-Item -Path Env:MAIL_USE_TLS -Value "true"
Set-Item -Path Env:MAIL_USERNAME -Value $API
Set-Item -Path Env:MAIL_PASSWORD -Value $API
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
  --user $API `
  --password $API `
  --from-email $FromEmail `
  --from-name $FromName

if ($LASTEXITCODE -eq 0) {
  Write-Host "[OK] E-mail de teste enviado para $To via Brevo." -ForegroundColor Green
} else {
  Write-Host "[ERRO] Falha ao enviar. Verifique API Key, domínio verificado (SPF/DKIM) e conexão." -ForegroundColor Red
}
