# Gramatike

## Vercel (via GitHub)
1. Tenha este repositório no GitHub (já está em `main`).
2. No painel da Vercel, importe o projeto a partir deste repositório.
3. Build & Output Settings:
- Framework: Other
- Python Runtime: conforme `vercel.json` (python3.12)
- Output: não precisa especificar, `api/index.py` expõe o Flask.
4. Variáveis de ambiente (Project Settings > Environment Variables):
- `SECRET_KEY`: uma string segura
- (Opcional) `DATABASE_URL`: use Postgres gerenciado se precisar de persistência real no edge (recomendado para produção). Caso contrário, o SQLite em `instance/app.db` pode não ser persistente no ambiente serverless da Vercel.

## Variáveis de ambiente necessárias

Mínimo para rodar:

- SECRET_KEY: string segura (32+ chars)
- Opcional: DATABASE_URL (Postgres recomendado em produção); sem isso, usa SQLite local (não persiste em serverless)

### Database Migrations

Para aplicar migrações pendentes ao banco de dados:

```bash
# Aplicar todas as migrações pendentes
flask db upgrade

# Verificar versão atual da migração
flask db current
```

**Nota importante:** Se você encontrar o erro `StringDataRightTruncation` relacionado ao campo `resumo`, consulte [DEPLOY_QUICK_REFERENCE.md](DEPLOY_QUICK_REFERENCE.md) para aplicar a correção que converte o campo de VARCHAR(400) para TEXT (ilimitado).

E-mail (opcional, mas necessário para verificação de e-mail, reset de senha, etc.):

- MAIL_SERVER: host SMTP (ex: smtp.office365.com ou smtp-relay.brevo.com)
- MAIL_PORT: porta (geralmente 587)
- MAIL_USE_TLS: true/false (geralmente true)
- MAIL_USERNAME: usuário SMTP (e/ou API Key)
- MAIL_PASSWORD: senha SMTP (ou API Key)
- MAIL_DEFAULT_SENDER: e-mail remetente padrão (ex: no-reply@gramatike.com.br)
- MAIL_SENDER_NAME: nome amigável do remetente (ex: Gramátike)

**Para Brevo (recomendado)**: Veja o guia completo em [BREVO_EMAIL_SETUP.md](BREVO_EMAIL_SETUP.md) com:
- Instruções passo-a-passo de configuração
- Como obter a SMTP Key
- Configuração de SPF/DKIM
- Scripts de diagnóstico e teste
- Solução de problemas comuns

### Testar Envio de E-mails

Para testar se o envio de e-mails está funcionando corretamente, use o script `send_test_email.py`:

```bash
# E-mail de teste básico (usa configuração do .env ou variáveis de ambiente)
python3 scripts/send_test_email.py seu_email@exemplo.com

# E-mail personalizado com título e conteúdo
python3 scripts/send_test_email.py seu_email@exemplo.com \
  --title "Meu Teste" \
  --html "<p>Conteúdo personalizado do e-mail</p>"

# Especificar servidor SMTP manualmente (útil para testes)
python3 scripts/send_test_email.py seu_email@exemplo.com \
  --server smtp.gmail.com \
  --port 587 \
  --tls \
  --user seu_email@gmail.com \
  --password sua_senha
```

**Nota:** Os e-mails de teste agora incluem o template completo do Gramátike com logo e botões roxos. Veja [EMAIL_TEST_TEMPLATE_FIX.md](EMAIL_TEST_TEMPLATE_FIX.md) para mais detalhes.

Supabase Storage (necessário para upload de arquivos em ambientes serverless como Vercel):

- SUPABASE_URL: URL do projeto Supabase (ex: https://xxxxx.supabase.co)
- SUPABASE_SERVICE_ROLE_KEY: chave de serviço do Supabase (encontrada em Settings > API)
- SUPABASE_BUCKET: nome do bucket de storage (padrão: 'avatars', mas você pode usar qualquer bucket configurado)

**🚨 IMPORTANTE - Configuração Necessária para Imagens Funcionarem:**

Se as imagens não estiverem aparecendo no site, o problema mais comum é que o bucket do Supabase não está configurado corretamente. Você precisa:

1. Criar um bucket (ex: 'avatars') em Storage
2. **Marcar o bucket como "Public bucket"** (ESSENCIAL!)
3. Configurar políticas RLS de acesso público para leitura dos arquivos
4. Permitir upload/update através da service role key

**📖 Guia Completo:** Veja [SUPABASE_BUCKET_SETUP.md](SUPABASE_BUCKET_SETUP.md) para instruções detalhadas passo-a-passo.

**🔧 Diagnóstico:** Se as imagens não funcionarem, execute o script de diagnóstico:
```bash
python diagnose_images.py
```
Este script verifica automaticamente sua configuração e identifica problemas.

RAG/IA (opcional):

- RAG_MODEL: modelo de embeddings (padrão: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)

Veja `.env.example` para um modelo de configuração local. No Vercel, cadastre as mesmas chaves em Settings → Environment Variables.

### Executar local
Ver seção "Development".
