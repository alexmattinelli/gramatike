# Correção de Problemas de Email com Brevo - Resumo das Alterações

## Problema Identificado

O usuário relatou que emails não estão sendo entregues aos usuários usando o serviço Brevo (anteriormente Sendinblue). Após análise do código, foram identificados os seguintes problemas:

### 1. Logging Inadequado
O tratamento de erros em `gramatike_app/utils/emailer.py` estava silenciosamente escondendo falhas:
```python
except Exception as e:
    try:
        current_app.logger.error(f"Falha ao enviar e-mail: {e}")
    except Exception:
        pass  # Erro completamente escondido!
    return False
```

### 2. Falta de Validação
Não havia validação se:
- As credenciais SMTP estavam configuradas corretamente
- O email remetente estava verificado no Brevo
- A chave SMTP estava presente (poderia tentar enviar sem credenciais)

### 3. Falta de Ferramentas de Diagnóstico
Não havia uma forma fácil de:
- Testar a configuração SMTP
- Diagnosticar problemas de conexão/autenticação
- Verificar se o Brevo estava configurado corretamente

### 4. Documentação Insuficiente
A documentação não explicava:
- Como configurar especificamente para Brevo
- Diferença entre SMTP Key e API Key
- Necessidade de verificar email remetente
- Como configurar SPF/DKIM

## Alterações Realizadas

### 1. Melhorias no `emailer.py` ✅

**Arquivo**: `gramatike_app/utils/emailer.py`

#### Melhorias implementadas:

1. **Validação de Configuração**:
   - Verifica se MAIL_SERVER e MAIL_DEFAULT_SENDER estão configurados
   - Verifica se MAIL_USERNAME e MAIL_PASSWORD estão presentes
   - Retorna mensagens claras se algo estiver faltando

2. **Logging Robusto**:
   - Tenta usar `current_app.logger`
   - Se falhar, usa `print()` como fallback
   - Garante que erros NUNCA sejam silenciados

3. **Tratamento de Erros Específicos**:
   - `SMTPAuthenticationError`: Identifica problemas de autenticação
   - `SMTPException`: Outros erros SMTP
   - `Exception`: Erros inesperados
   - Cada tipo de erro tem mensagem específica

4. **Log de Sucesso**:
   - Confirma quando email é enviado com sucesso
   - Ajuda a diagnosticar se o problema é envio ou entrega

#### Código novo (trechos principais):

```python
# Validação de credenciais
if not username or not password:
    msg_error = f'Configuração SMTP incompleta: MAIL_USERNAME ou MAIL_PASSWORD ausentes. Host: {host}'
    try:
        current_app.logger.warning(msg_error)
    except Exception:
        print(f"[AVISO] {msg_error}", flush=True)
    return False

# Tratamento de erros específicos
except smtplib.SMTPAuthenticationError as e:
    error_msg = f"Falha de autenticação SMTP: {e}. Verifique MAIL_USERNAME e MAIL_PASSWORD."
    try:
        current_app.logger.error(error_msg)
    except Exception:
        print(f"[ERRO] {error_msg}", flush=True)
    return False
```

### 2. Script de Diagnóstico Python ✅

**Arquivo**: `scripts/diagnose_email.py`

Script completo para diagnosticar problemas de email SMTP, especialmente com Brevo.

#### Funcionalidades:

1. **Teste de Conexão**: Verifica se consegue conectar ao servidor SMTP
2. **Teste de TLS**: Verifica se consegue estabelecer TLS/STARTTLS
3. **Teste de Autenticação**: Valida credenciais SMTP
4. **Teste de Envio**: Envia email de teste real
5. **Validação de Chave**: Detecta se está usando API Key ao invés de SMTP Key
6. **Mensagens Detalhadas**: Explica exatamente o que deu errado e como corrigir

#### Uso:

```bash
# Com variável de ambiente
export BREVO_SMTP_KEY="xsmtpsib-..."
python3 scripts/diagnose_email.py seu-email@exemplo.com

# Passando chave diretamente
python3 scripts/diagnose_email.py seu-email@exemplo.com --smtp-key xsmtpsib-...

# Com opções completas
python3 scripts/diagnose_email.py seu-email@exemplo.com \
  --server smtp-relay.brevo.com \
  --port 587 \
  --smtp-key xsmtpsib-... \
  --from no-reply@gramatike.com.br \
  --from-name "Gramátike"
```

#### Exemplo de saída:

```
======================================================================
DIAGNÓSTICO DE EMAIL SMTP - BREVO
======================================================================

Configuração:
  Servidor: smtp-relay.brevo.com:587
  TLS: Sim
  De: no-reply@gramatike.com.br
  Para: teste@exemplo.com

1. Testando conexão com smtp-relay.brevo.com:587...
   ✓ Conexão estabelecida com sucesso

2. Testando TLS/STARTTLS...
   ✓ TLS estabelecido com sucesso

3. Testando autenticação...
   Username: xsmtpsib-1234567890ab...
   ✓ Autenticação bem-sucedida

4. Testando envio de email...
   De: no-reply@gramatike.com.br
   Para: teste@exemplo.com
   ✓ Email enviado com sucesso!
   VERIFIQUE: Caixa de entrada de teste@exemplo.com (pode estar no spam)

======================================================================
✅ TODOS OS TESTES PASSARAM!
======================================================================
```

### 3. Script Shell para Linux/Mac ✅

**Arquivo**: `scripts/send_test_email_brevo.sh`

Equivalente ao script PowerShell existente, mas para sistemas Unix.

#### Funcionalidades:

- Pega SMTP Key do ambiente ou solicita ao usuário
- Configura variáveis de ambiente automaticamente
- Chama `scripts/send_test_email.py` com parâmetros corretos
- Fornece mensagens de sucesso/erro claras

#### Uso:

```bash
# Método 1: Com variável de ambiente
export BREVO_SMTP_KEY="xsmtpsib-..."
./scripts/send_test_email_brevo.sh seu-email@exemplo.com

# Método 2: Script solicita a chave
./scripts/send_test_email_brevo.sh seu-email@exemplo.com

# Personalizar remetente
./scripts/send_test_email_brevo.sh seu-email@exemplo.com no-reply@gramatike.com.br "Gramátike"
```

### 4. Documentação Completa ✅

**Arquivo**: `BREVO_EMAIL_SETUP.md`

Guia completo de 200+ linhas com:

#### Conteúdo:

1. **Visão Geral**: O que é Brevo e como funciona
2. **Configuração no Brevo**:
   - Como criar conta
   - Como obter SMTP Key
   - Como verificar domínio
   - Como configurar SPF/DKIM
   - Como adicionar email remetente
3. **Configuração no Gramátike**:
   - Desenvolvimento local (.env)
   - Produção (Vercel)
4. **Testando a Configuração**:
   - 3 métodos diferentes (diagnóstico, shell, PowerShell)
5. **Solução de Problemas**:
   - Emails não chegando
   - Erro de autenticação
   - Remetente não autorizado
   - Emails no spam
   - Timeout/conexão
6. **Limites do Brevo**: Planos e restrições
7. **Alternativas**: SendGrid, AWS SES, Gmail
8. **Checklist de Configuração**: Lista de verificação completa

### 5. Atualização do `.env.example` ✅

**Arquivo**: `.env.example`

Adicionadas instruções específicas para Brevo com comentários claros:

```bash
# E-mail (opcional, mas necessário para verificação de e-mail, reset de senha)
# Para Brevo (recomendado):
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USE_TLS=true
# IMPORTANTE: Para Brevo, use a SMTP Key (xsmtpsib-...) em AMBOS username e password
MAIL_USERNAME=xsmtpsib-sua-chave-smtp-aqui
MAIL_PASSWORD=xsmtpsib-sua-chave-smtp-aqui
# O email remetente DEVE estar verificado no Brevo
MAIL_DEFAULT_SENDER=no-reply@gramatike.com.br
MAIL_SENDER_NAME=Gramátike

# Alternativa - Office 365:
# MAIL_SERVER=smtp.office365.com
# ...
```

### 6. Atualização do README.md ✅

**Arquivo**: `README.md`

Adicionada referência ao guia completo do Brevo:

```markdown
**Para Brevo (recomendado)**: Veja o guia completo em [BREVO_EMAIL_SETUP.md](BREVO_EMAIL_SETUP.md) com:
- Instruções passo-a-passo de configuração
- Como obter a SMTP Key
- Configuração de SPF/DKIM
- Scripts de diagnóstico e teste
- Solução de problemas comuns
```

## Como Usar as Melhorias

### Para o Usuário (Diagnosticar o Problema)

1. **Execute o diagnóstico completo**:
   ```bash
   export BREVO_SMTP_KEY="sua-chave-aqui"
   python3 scripts/diagnose_email.py seu-email@exemplo.com
   ```

2. **Veja o que falhou**:
   - Se falhar na conexão: problema de rede/firewall
   - Se falhar no TLS: problema de certificado/porta
   - Se falhar na autenticação: chave SMTP incorreta
   - Se falhar no envio: email remetente não verificado

3. **Siga as instruções**:
   - O script mostra exatamente o que está errado
   - Veja `BREVO_EMAIL_SETUP.md` para correções detalhadas

### Para Desenvolvimento

1. **Configure o `.env`**:
   ```bash
   cp .env.example .env
   # Edite .env com suas credenciais Brevo
   ```

2. **Teste a configuração**:
   ```bash
   ./scripts/send_test_email_brevo.sh seu-email@exemplo.com
   ```

3. **Verifique os logs**:
   - Agora os erros aparecem no console
   - Mensagens claras sobre o que está faltando

### Para Produção (Vercel)

1. **Configure as variáveis de ambiente** (veja `BREVO_EMAIL_SETUP.md` seção "Produção")

2. **Reimplante o projeto**

3. **Verifique os logs do Vercel**:
   - Agora os erros aparecem nos Runtime Logs
   - Mensagens indicam exatamente o problema

## Problemas Comuns e Soluções

### 1. "Configuração SMTP incompleta"

**Antes**: Tentava enviar sem credenciais, falhava silenciosamente

**Agora**: 
- Log claro: "MAIL_USERNAME ou MAIL_PASSWORD ausentes"
- Indica qual variável está faltando
- Não tenta enviar (evita timeout desnecessário)

**Solução**: Configure todas as variáveis MAIL_* no ambiente

### 2. "Falha de autenticação SMTP"

**Antes**: Erro genérico sem detalhes

**Agora**:
- Log específico: "SMTPAuthenticationError"
- Dica: "Verifique MAIL_USERNAME e MAIL_PASSWORD"
- Script de diagnóstico mostra se a chave está correta

**Solução**: 
- Use SMTP Key (xsmtpsib-), não API Key (xkeysib-)
- Mesma chave em MAIL_USERNAME e MAIL_PASSWORD

### 3. "Sender not authorized"

**Antes**: Erro sem explicação clara

**Agora**:
- Log específico do erro SMTP
- Documentação explica verificação de email
- Checklist de configuração

**Solução**: Verifique email remetente no Brevo (veja `BREVO_EMAIL_SETUP.md`)

### 4. Emails não chegam (sem erro)

**Antes**: Nenhuma informação

**Agora**:
- Log de sucesso: "E-mail enviado com sucesso para..."
- Se viu o log de sucesso mas email não chegou: problema no Brevo ou spam
- Script de diagnóstico verifica toda a cadeia

**Solução**: 
- Verifique SPF/DKIM (seção do guia)
- Verifique pasta de spam
- Veja logs do Brevo

## Próximos Passos Recomendados

1. **Execute o diagnóstico** para identificar o problema específico
2. **Siga o `BREVO_EMAIL_SETUP.md`** para configuração correta
3. **Verifique variáveis de ambiente** no Vercel (produção)
4. **Teste localmente** antes de implantar
5. **Monitore os logs** após implantar

## Arquivos Alterados

- ✅ `gramatike_app/utils/emailer.py` - Melhor logging e validação
- ✅ `scripts/diagnose_email.py` - Novo script de diagnóstico
- ✅ `scripts/send_test_email_brevo.sh` - Script shell para Linux/Mac
- ✅ `BREVO_EMAIL_SETUP.md` - Documentação completa
- ✅ `.env.example` - Instruções para Brevo
- ✅ `README.md` - Referência ao guia Brevo

## Benefícios das Alterações

1. ✅ **Erros nunca mais escondidos**: Sempre haverá log (app.logger ou print)
2. ✅ **Diagnóstico fácil**: Script automatizado identifica o problema exato
3. ✅ **Documentação completa**: Guia passo-a-passo para Brevo
4. ✅ **Validação preventiva**: Detecta configuração incorreta antes de tentar enviar
5. ✅ **Multiplataforma**: Scripts para Windows (PowerShell) e Unix (Bash)
6. ✅ **Mensagens claras**: Cada erro tem explicação e solução

## Testes Realizados

- ✅ Script de diagnóstico executa sem erros
- ✅ Ajuda dos scripts funciona corretamente
- ✅ Validação de chaves SMTP (detecta API Key vs SMTP Key)
- ✅ Mensagens de erro são claras e acionáveis
- ✅ Documentação está completa e coerente

## Conclusão

As alterações resolvem o problema de emails não serem entregues de três formas:

1. **Prevenção**: Validação detecta configuração incorreta antes de tentar enviar
2. **Diagnóstico**: Ferramentas automatizadas identificam o problema exato
3. **Correção**: Documentação guia passo-a-passo para configurar corretamente

**O usuário agora tem tudo que precisa para**:
- Identificar por que emails não estão sendo entregues
- Corrigir a configuração do Brevo
- Testar e validar que está funcionando
- Configurar corretamente em produção (Vercel)
