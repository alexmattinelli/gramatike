# Guia de Troubleshooting - Gramátike

Este documento fornece soluções para problemas comuns encontrados no Gramátike.

## 🚨 Problema: "Sistema temporariamente indisponível"

### Causa
Este erro geralmente ocorre quando:
- As tabelas do banco de dados não foram criadas
- As tabelas foram excluídas acidentalmente
- Houve falha na migração do banco de dados

### Solução

#### Para Desenvolvimento Local (SQLite)

1. **Opção 1: Usar o script de inicialização**
   ```bash
   python scripts/init_database.py
   ```

2. **Opção 2: Recriar manualmente com Flask**
   ```bash
   # No terminal Python
   python
   >>> from gramatike_app import create_app
   >>> from gramatike_app.models import db
   >>> app = create_app()
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

3. **Opção 3: Usar migrações Flask-Migrate**
   ```bash
   # Se as migrações já existem
   flask db upgrade
   
   # Se precisa criar novas migrações
   flask db migrate -m "Recreate tables"
   flask db upgrade
   ```

#### Para Produção (Cloudflare D1)

1. **Verificar se o banco D1 existe**
   ```bash
   wrangler d1 info gramatike
   ```

2. **Se não existir, criar o banco**
   ```bash
   wrangler d1 create gramatike
   ```

3. **Atualizar o `wrangler.toml` com o database_id retornado**

4. **Criar as tabelas executando o schema**
   ```bash
   wrangler d1 execute gramatike --file=./schema.d1.sql
   ```

5. **Verificar se as tabelas foram criadas**
   ```bash
   wrangler d1 execute gramatike --command="SELECT name FROM sqlite_master WHERE type='table';"
   ```

6. **Fazer deploy da aplicação**
   ```bash
   npm run deploy
   ```

## 🔐 Problema: Login não funciona após restauração do banco

### Causa
Usuáries foram excluídes quando as tabelas foram removidas.

### Solução

1. **Criar um novo superadmin**
   ```bash
   python create_superadmin.py
   ```
   
2. **Ou criar usuárie manualmente**
   ```bash
   python
   >>> from gramatike_app import create_app
   >>> from gramatike_app.models import db, User
   >>> app = create_app()
   >>> with app.app_context():
   ...     user = User(username='admin', email='admin@gramatike.com')
   ...     user.set_password('senha_segura')
   ...     user.is_admin = True
   ...     user.is_superadmin = True
   ...     db.session.add(user)
   ...     db.session.commit()
   >>> exit()
   ```

## 📊 Problema: Dados foram perdidos

### Prevenção
Para evitar perda de dados no futuro:

1. **Fazer backup regular do banco de dados**
   
   Para SQLite local:
   ```bash
   cp instance/app.db instance/backup_$(date +%Y%m%d_%H%M%S).db
   ```
   
   Para D1:
   ```bash
   wrangler d1 execute gramatike --command="SELECT * FROM user;" --output=backup_users.json
   ```

2. **Usar controle de versão para migrações**
   - Nunca delete arquivos de migração
   - Sempre teste migrações em ambiente de desenvolvimento primeiro

3. **Testar antes de fazer deploy**
   ```bash
   # Testar localmente
   python run.py
   
   # Testar migrações
   flask db upgrade
   flask db downgrade
   flask db upgrade
   ```

## 🔄 Problema: Migrações conflitantes

### Causa
Múltiplas migrações tentando modificar a mesma tabela.

### Solução

1. **Verificar estado das migrações**
   ```bash
   flask db current
   flask db history
   ```

2. **Resolver conflitos**
   ```bash
   # Voltar para uma migração anterior
   flask db downgrade <revision>
   
   # Aplicar novamente
   flask db upgrade
   ```

3. **Recriar migrações do zero (última opção)**
   ```bash
   # CUIDADO: Isso apaga histórico de migrações
   rm -rf migrations/versions/*
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

## 🌐 Problema: Cloudflare D1 não sincroniza

### Solução

1. **Verificar configuração do wrangler.toml**
   ```toml
   [[d1_databases]]
   binding = "DB"
   database_name = "gramatike"
   database_id = "seu-database-id-aqui"
   ```

2. **Verificar se está autenticado**
   ```bash
   wrangler whoami
   # Se não estiver autenticado:
   wrangler login
   ```

3. **Recriar binding se necessário**
   ```bash
   wrangler d1 list
   # Copie o ID correto e atualize wrangler.toml
   ```

## 📝 Problema: Flash messages não aparecem

### Causa
Template não está renderizando as mensagens flash corretamente.

### Solução

Verifique se o template tem o bloco correto:

```jinja2
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    <ul class="flash-messages">
      {% for category, message in messages %}
        <li class="flash-{{ category }}">{{ message }}</li>
      {% endfor %}
    </ul>
  {% endif %}
{% endwith %}
```

## 🆘 Ainda com problemas?

1. **Verifique os logs**
   ```bash
   # Logs do Flask local
   python run.py --debug
   
   # Logs do Cloudflare
   wrangler tail
   ```

2. **Verifique variáveis de ambiente**
   ```bash
   # Localmente
   cat .env
   
   # No Cloudflare
   wrangler secret list
   ```

3. **Contate o suporte ou abra um issue**
   - Inclua logs de erro
   - Descreva os passos que levaram ao problema
   - Mencione seu ambiente (local, Cloudflare, etc.)

## 📚 Recursos Adicionais

- [README.md](README.md) - Documentação principal
- [README_DEPLOY_CLOUDFLARE.md](README_DEPLOY_CLOUDFLARE.md) - Deploy Cloudflare
- [schema.d1.sql](schema.d1.sql) - Schema completo do banco
- [Documentação Cloudflare D1](https://developers.cloudflare.com/d1/)
- [Documentação Flask-Migrate](https://flask-migrate.readthedocs.io/)
