# Gramatike

## Performance Optimization

**Caching Implementation**: The app uses response caching to reduce CPU usage and stay within Vercel's free tier limits. See [CACHE_IMPLEMENTATION.md](CACHE_IMPLEMENTATION.md) for details.

Key cached endpoints:
- `/api/palavra-do-dia` - 1 hour cache
- `/api/redacao/temas` - 10 minute cache
- `/api/gramatike/search` - 5 minute cache
- `/api/novidades` - 5 minute cache
- `/` (index page) - 3 minute cache for trending/commented posts

To monitor cache performance:
```bash
python scripts/monitor_cache.py
```

### Vercel (via GitHub)
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

**Importante:** No Supabase Storage, você precisa:
1. Criar um bucket (ex: 'avatars') em Storage
2. Configurar políticas de acesso público para leitura dos arquivos
3. Permitir upload/update através da service role key

RAG/IA (opcional):

- RAG_MODEL: modelo de embeddings (padrão: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)

Veja `.env.example` para um modelo de configuração local. No Vercel, cadastre as mesmas chaves em Settings → Environment Variables.

### Executar local
Ver seção "Development".
