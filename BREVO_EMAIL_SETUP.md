# Configuração de Email com Brevo (Sendinblue)

Este documento fornece instruções detalhadas para configurar o envio de emails através do Brevo no Gramátike.

## Visão Geral

O Gramátike usa SMTP para enviar emails de:
- Confirmação de cadastro
- Verificação de email
- Redefinição de senha
- Alteração de email
- Boas-vindas

## Configuração no Brevo

### 1. Criar Conta no Brevo

1. Acesse [https://www.brevo.com](https://www.brevo.com) e crie uma conta
2. Verifique seu email
3. Complete o setup inicial

### 2. Obter a SMTP Key

1. Acesse o painel do Brevo
2. Vá em **Settings** (Configurações) → **SMTP & API**
3. Na seção **SMTP**, clique em **Create a new SMTP key** ou copie uma existente
4. A chave começa com `xsmtpsib-` (diferente da API Key que começa com `xkeysib-`)
5. **IMPORTANTE**: Salve esta chave em local seguro - ela não será mostrada novamente

### 3. Verificar Domínio e Email Remetente

Para que os emails sejam entregues corretamente:

1. **Adicionar Domínio**:
   - Vá em **Settings** → **Senders & IP**
   - Clique em **Domains** → **Add a Domain**
   - Digite seu domínio (ex: `gramatike.com.br`)

2. **Configurar DNS (SPF e DKIM)**:
   - O Brevo fornecerá registros DNS para configurar
   - Adicione os registros TXT no seu provedor de DNS:
     - SPF: `v=spf1 include:spf.brevo.com ~all`
     - DKIM: (será fornecido pelo Brevo, geralmente um registro TXT)
   - Aguarde a verificação (pode levar até 48h, mas geralmente é rápido)

3. **Adicionar Email Remetente**:
   - Vá em **Settings** → **Senders & IP** → **Senders**
   - Clique em **Add a Sender**
   - Adicione o email que será usado (ex: `no-reply@gramatike.com.br`)
   - Você receberá um email de confirmação neste endereço
   - Clique no link de confirmação

## Configuração no Gramátike

### Desenvolvimento Local

Crie ou edite o arquivo `.env` na raiz do projeto:

```bash
# Email via Brevo
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=xsmtpsib-sua-chave-smtp-aqui
MAIL_PASSWORD=xsmtpsib-sua-chave-smtp-aqui
MAIL_DEFAULT_SENDER=no-reply@gramatike.com.br
MAIL_SENDER_NAME=Gramátike
```

**IMPORTANTE**: 
- Use a MESMA chave SMTP em `MAIL_USERNAME` e `MAIL_PASSWORD`
- O `MAIL_DEFAULT_SENDER` DEVE ser um email verificado no Brevo

### Produção (Vercel)

1. Acesse o painel do projeto no Vercel
2. Vá em **Settings** → **Environment Variables**
3. Adicione as seguintes variáveis:

| Variável | Valor |
|----------|-------|
| `MAIL_SERVER` | `smtp-relay.brevo.com` |
| `MAIL_PORT` | `587` |
| `MAIL_USE_TLS` | `true` |
| `MAIL_USERNAME` | `xsmtpsib-sua-chave-smtp-aqui` |
| `MAIL_PASSWORD` | `xsmtpsib-sua-chave-smtp-aqui` |
| `MAIL_DEFAULT_SENDER` | `no-reply@gramatike.com.br` |
| `MAIL_SENDER_NAME` | `Gramátike` |

4. Salve e reimplante o projeto

## Testando a Configuração

### Opção 1: Script de Diagnóstico (Recomendado)

```bash
# Definir a chave SMTP
export BREVO_SMTP_KEY="xsmtpsib-sua-chave-aqui"

# Executar diagnóstico completo
python3 scripts/diagnose_email.py seu-email@exemplo.com
```

Este script testa:
1. ✓ Conexão com servidor SMTP
2. ✓ Estabelecimento de TLS
3. ✓ Autenticação
4. ✓ Envio de email de teste

### Opção 2: Script Shell (Linux/Mac)

```bash
export BREVO_SMTP_KEY="xsmtpsib-sua-chave-aqui"
./scripts/send_test_email_brevo.sh seu-email@exemplo.com
```

### Opção 3: Script PowerShell (Windows)

```powershell
$env:BREVO_SMTP_KEY = "xsmtpsib-sua-chave-aqui"
.\scripts\send_test_email_brevo.ps1 -To "seu-email@exemplo.com"
```

## Solução de Problemas

### Emails não estão chegando

1. **Verifique as credenciais**:
   ```bash
   python3 scripts/diagnose_email.py seu-email@exemplo.com --smtp-key xsmtpsib-sua-chave
   ```

2. **Verifique os logs da aplicação**:
   - No desenvolvimento: verifique o console/terminal
   - Na produção (Vercel): veja os logs em **Deployments** → selecione o deployment → **Runtime Logs**

3. **Verifique se o email remetente está verificado**:
   - Acesse Brevo → **Settings** → **Senders & IP** → **Senders**
   - O email deve ter um ✓ (verificado)

4. **Verifique SPF/DKIM**:
   - Acesse Brevo → **Settings** → **Senders & IP** → **Domains**
   - O domínio deve estar "Authenticated"

5. **Verifique caixa de spam**:
   - Emails de teste podem cair no spam inicialmente
   - Com SPF/DKIM configurados corretamente, isso melhora

### Erro de Autenticação

```
SMTPAuthenticationError: (535, b'...')
```

**Causas comuns**:
- Chave SMTP incorreta ou expirada
- Usando API Key (xkeysib-) ao invés de SMTP Key (xsmtpsib-)
- MAIL_USERNAME e MAIL_PASSWORD diferentes (devem ser iguais)

**Solução**:
1. Gere uma nova SMTP Key no Brevo
2. Atualize ambas variáveis `MAIL_USERNAME` e `MAIL_PASSWORD` com a mesma chave
3. Teste com o script de diagnóstico

### Erro de Remetente não Autorizado

```
SMTPSenderRefused: (550, b'Sender not authorized')
```

**Causa**: Email remetente não está verificado no Brevo

**Solução**:
1. Vá em Brevo → **Settings** → **Senders & IP** → **Senders**
2. Adicione o email usado em `MAIL_DEFAULT_SENDER`
3. Confirme o email clicando no link de verificação
4. Aguarde alguns minutos e teste novamente

### Emails caindo no Spam

**Soluções**:
1. Configure SPF e DKIM corretamente (veja seção "Verificar Domínio")
2. Use um email remetente profissional (ex: `no-reply@seudominio.com`)
3. Evite palavras de spam no assunto/conteúdo
4. Mantenha uma taxa de envio razoável
5. Considere adicionar um link de "unsubscribe" (descadastrar)

### Timeout ou Erro de Conexão

```
TimeoutError: [Errno 110] Connection timed out
```

**Causas**:
- Firewall bloqueando porta 587
- Servidor sem acesso à internet
- Proxy/VPN interferindo

**Solução**:
1. Teste conexão direta:
   ```bash
   telnet smtp-relay.brevo.com 587
   # ou
   nc -zv smtp-relay.brevo.com 587
   ```
2. Verifique firewall/proxy
3. Em produção (Vercel), isso não deve ser um problema

## Limites do Brevo

### Plano Gratuito
- **300 emails/dia**
- Marca "Sent with Brevo" nos emails
- Todos os recursos SMTP

### Planos Pagos
- A partir de 25€/mês
- Sem limites diários (baseado em volume contratado)
- Sem marca "Sent with Brevo"
- Suporte prioritário

**Recomendação**: Para produção, considere um plano pago para maior confiabilidade e volume.

## Alternativas ao Brevo

Se preferir outro provedor SMTP:

### SendGrid
```bash
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=apikey
MAIL_PASSWORD=SG.sua-api-key-aqui
```

### AWS SES
```bash
MAIL_SERVER=email-smtp.us-east-1.amazonaws.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=suas-credenciais-smtp
MAIL_PASSWORD=sua-senha-smtp
```

### Gmail/Google Workspace
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app
```

**Nota**: Para Gmail, use "Senhas de app" ao invés da senha normal (requer 2FA ativado).

## Checklist de Configuração

- [ ] Conta criada no Brevo
- [ ] SMTP Key obtida (xsmtpsib-...)
- [ ] Domínio adicionado no Brevo
- [ ] SPF configurado no DNS
- [ ] DKIM configurado no DNS
- [ ] Email remetente verificado
- [ ] Variáveis de ambiente configuradas (local e/ou produção)
- [ ] Teste realizado com script de diagnóstico
- [ ] Email de teste recebido com sucesso

## Suporte

Se os problemas persistirem após seguir este guia:

1. Execute o diagnóstico completo e salve a saída:
   ```bash
   python3 scripts/diagnose_email.py seu-email@exemplo.com > email_debug.log 2>&1
   ```

2. Verifique os logs da aplicação no Vercel

3. Contate o suporte do Brevo se o problema for com a conta/configuração deles

4. Abra uma issue no repositório com os logs (sem expor a SMTP Key!)

## Recursos Adicionais

- [Documentação Oficial do Brevo SMTP](https://developers.brevo.com/docs/send-emails-with-smtp)
- [Guia SPF/DKIM](https://help.brevo.com/hc/en-us/articles/209551085)
- [Solução de Problemas Brevo](https://help.brevo.com/hc/en-us/articles/360000991960)
