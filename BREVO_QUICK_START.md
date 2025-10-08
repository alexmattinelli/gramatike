# Guia Rápido: Resolver Problema de Email com Brevo

## 🚀 Início Rápido

### Passo 1: Diagnóstico
Execute o script de diagnóstico para identificar o problema:

```bash
export BREVO_SMTP_KEY="sua-chave-smtp-aqui"
python3 scripts/diagnose_email.py seu-email@exemplo.com
```

O script testará:
1. ✓ Conexão com servidor SMTP
2. ✓ TLS/STARTTLS
3. ✓ Autenticação
4. ✓ Envio de email

### Passo 2: Veja o que falhou

#### Se falhou na **Autenticação**:
```
✗ ERRO de autenticação: (535, b'...')
```
**Solução**: 
- Verifique se está usando SMTP Key (xsmtpsib-), NÃO API Key (xkeysib-)
- Mesma chave em MAIL_USERNAME e MAIL_PASSWORD

#### Se falhou no **Envio**:
```
✗ ERRO ao enviar: (550, b'Sender not authorized')
```
**Solução**:
- Email remetente DEVE estar verificado no Brevo
- Acesse Brevo → Settings → Senders & IP → Senders
- Adicione e verifique o email

#### Se passou tudo mas **email não chegou**:
**Solução**:
1. Verifique pasta de spam
2. Configure SPF/DKIM (veja documentação completa)
3. Aguarde alguns minutos (pode ter delay)

### Passo 3: Configurar Corretamente

#### Desenvolvimento Local
Edite `.env`:
```bash
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=xsmtpsib-sua-chave-smtp-aqui
MAIL_PASSWORD=xsmtpsib-sua-chave-smtp-aqui
MAIL_DEFAULT_SENDER=no-reply@gramatike.com.br
MAIL_SENDER_NAME=Gramátike
```

#### Produção (Vercel)
1. Vercel Dashboard → Settings → Environment Variables
2. Adicione as mesmas variáveis acima
3. Reimplante o projeto

### Passo 4: Testar Novamente
```bash
./scripts/send_test_email_brevo.sh seu-email@exemplo.com
```

## 📚 Documentação Completa

Para instruções detalhadas, veja:
- **[BREVO_EMAIL_SETUP.md](BREVO_EMAIL_SETUP.md)** - Guia completo de configuração
- **[FIX_BREVO_EMAIL_SUMMARY.md](FIX_BREVO_EMAIL_SUMMARY.md)** - Resumo das alterações

## 🛠️ Ferramentas Disponíveis

### 1. Script de Diagnóstico (Python)
```bash
python3 scripts/diagnose_email.py EMAIL [opções]
```

### 2. Script de Teste (Shell - Linux/Mac)
```bash
./scripts/send_test_email_brevo.sh EMAIL
```

### 3. Script de Teste (PowerShell - Windows)
```powershell
.\scripts\send_test_email_brevo.ps1 -To EMAIL
```

## ❓ Perguntas Frequentes

**P: Qual a diferença entre API Key e SMTP Key?**
- API Key (xkeysib-): Para usar a API REST do Brevo
- SMTP Key (xsmtpsib-): Para enviar emails via SMTP ← **USE ESTA**

**P: Por que emails não estão chegando?**
1. Verifique se passou no diagnóstico
2. Verifique email remetente verificado
3. Verifique SPF/DKIM configurados
4. Verifique pasta de spam

**P: Como ver os erros em produção?**
- Vercel: Deployments → [seu deployment] → Runtime Logs
- Os logs agora mostram erros detalhados

**P: O que mudou no código?**
- ✅ Validação de configuração antes de enviar
- ✅ Logs detalhados de erros (nunca mais silenciado)
- ✅ Mensagens claras sobre o que está errado
- ✅ Fallback para print() se logger falhar

## 🎯 Checklist de Configuração

- [ ] Conta criada no Brevo
- [ ] SMTP Key obtida (xsmtpsib-...)
- [ ] Email remetente adicionado no Brevo
- [ ] Email remetente verificado (check no email)
- [ ] Variáveis MAIL_* configuradas (.env ou Vercel)
- [ ] MAIL_USERNAME = MAIL_PASSWORD = mesma SMTP Key
- [ ] MAIL_DEFAULT_SENDER = email verificado
- [ ] Diagnóstico executado e passou
- [ ] Email de teste recebido

## 🆘 Precisa de Ajuda?

1. Execute o diagnóstico e salve a saída:
   ```bash
   python3 scripts/diagnose_email.py seu-email@exemplo.com > debug.log 2>&1
   ```

2. Veja `BREVO_EMAIL_SETUP.md` seção "Solução de Problemas"

3. Abra uma issue no repositório (não exponha a SMTP Key!)
