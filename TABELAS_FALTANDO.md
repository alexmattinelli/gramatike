# Tabelas Faltando no Seu Banco D1

## Resumo

Você tem **38 tabelas** mas estão faltando **17 tabelas** do schema completo.

### Tabelas Críticas Faltando (Afetam o Feed)

⚠️ **post_image** - Imagens anexadas aos posts  
⚠️ **notification** - Sistema de notificações  
⚠️ **amizade** - Amizades (seguimento mútuo) para Amigues  
⚠️ **report** - Denúncias de conteúdo  
⚠️ **curtida** - Sistema de curtidas (alternativo a post_likes)  
⚠️ **mencao** - Menções @usuario nos posts  

### Todas as Tabelas Faltando

1. activity_log
2. **amizade** ⚠️
3. **curtida** ⚠️
4. email_token
5. exercise_progress
6. favorito
7. grupo_membre
8. grupo_mensagem
9. **mencao** ⚠️
10. **notification** ⚠️
11. **post_image** ⚠️
12. **report** ⚠️
13. upload
14. user_badge
15. user_history
16. user_points
17. user_preferences

## Como Criar as Tabelas Faltando

### Opção 1: Criar Todas de Uma Vez (Recomendado)

```bash
# Aplicar o schema completo (só cria as que não existem)
wrangler d1 execute gramatike-db --file=schema.d1.sql
```

Isso é seguro porque todas as tabelas usam `CREATE TABLE IF NOT EXISTS`, então não vai afetar as tabelas que já existem.

### Opção 2: Criar Só as Críticas para o Feed

Execute este SQL para criar apenas as 6 tabelas críticas:

```bash
wrangler d1 execute gramatike-db --file=tabelas_faltando_criticas.sql
```

Conteúdo do arquivo `tabelas_faltando_criticas.sql`:

```sql
-- Tabela para imagens dos posts
CREATE TABLE IF NOT EXISTS post_image (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    image_url TEXT NOT NULL,
    image_ordem INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_post_image_post ON post_image(post_id);

-- Tabela de notificações
CREATE TABLE IF NOT EXISTS notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    conteudo TEXT,
    link TEXT,
    visto INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notification_user ON notification(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_visto ON notification(visto);

-- Tabela de amizades (seguimento mútuo)
CREATE TABLE IF NOT EXISTS amizade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user1_id INTEGER NOT NULL,
    user2_id INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(user1_id, user2_id),
    FOREIGN KEY (user1_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (user2_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_amizade_user1 ON amizade(user1_id);
CREATE INDEX IF NOT EXISTS idx_amizade_user2 ON amizade(user2_id);

-- Tabela de denúncias
CREATE TABLE IF NOT EXISTS report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reporter_id INTEGER NOT NULL,
    reported_user_id INTEGER,
    post_id INTEGER,
    comentario_id INTEGER,
    tipo TEXT NOT NULL,
    motivo TEXT NOT NULL,
    descricao TEXT,
    status TEXT DEFAULT 'pendente',
    created_at TEXT DEFAULT (datetime('now')),
    resolved_at TEXT,
    resolved_by INTEGER,
    FOREIGN KEY (reporter_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (reported_user_id) REFERENCES user(id) ON DELETE SET NULL,
    FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE,
    FOREIGN KEY (resolved_by) REFERENCES user(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_report_status ON report(status);
CREATE INDEX IF NOT EXISTS idx_report_created ON report(created_at);

-- Tabela de curtidas (sistema antigo, pode usar post_likes)
CREATE TABLE IF NOT EXISTS curtida (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_curtida_user ON curtida(user_id);
CREATE INDEX IF NOT EXISTS idx_curtida_post ON curtida(post_id);

-- Tabela de menções
CREATE TABLE IF NOT EXISTS mencao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    mentioned_by INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (mentioned_by) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_mencao_user ON mencao(user_id);
CREATE INDEX IF NOT EXISTS idx_mencao_post ON mencao(post_id);
```

## Impacto das Tabelas Faltando

### Com as Tabelas Atuais (38)

✅ Login funciona (user, user_session)  
✅ Posts básicos funcionam (post, post_likes)  
✅ Comentários funcionam (comentario)  
✅ Seguir funciona (seguidories)  
❌ Imagens em posts NÃO funcionam (falta post_image)  
❌ Notificações NÃO funcionam (falta notification)  
❌ Amigues NÃO aparece (falta amizade)  
❌ Denunciar NÃO funciona (falta report)  
❌ Menções @usuario NÃO funcionam (falta mencao)  

### Depois de Criar as Tabelas Críticas

✅ Login funciona  
✅ Posts com imagens funcionam  
✅ Comentários funcionam  
✅ Seguir funciona  
✅ **Imagens em posts funcionam** (post_image)  
✅ **Notificações funcionam** (notification)  
✅ **Amigues aparece** (amizade)  
✅ **Denunciar funciona** (report)  
✅ **Menções @usuario funcionam** (mencao)  

## Comandos Rápidos

### Verificar Tabelas Atuais
```bash
wrangler d1 execute gramatike-db --command="SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
```

### Criar Todas as Tabelas Faltando
```bash
wrangler d1 execute gramatike-db --file=schema.d1.sql
```

### Verificar se post_image Existe
```bash
wrangler d1 execute gramatike-db --command="SELECT COUNT(*) as existe FROM sqlite_master WHERE type='table' AND name='post_image';"
```

## Recomendação

Execute o schema completo:
```bash
wrangler d1 execute gramatike-db --file=schema.d1.sql
```

Isso vai criar apenas as 17 tabelas faltando sem afetar as 38 que já existem. É a forma mais segura e completa.

---

**Status Atual:** 38/55 tabelas (69%)  
**Faltando:** 17 tabelas (31%)  
**Críticas Faltando:** 6 tabelas que afetam o feed  

**Próximo Passo:** Executar `schema.d1.sql` para ter todas as funcionalidades
