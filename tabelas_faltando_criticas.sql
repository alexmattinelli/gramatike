-- Tabelas Críticas Faltando para o Feed
-- Execute: wrangler d1 execute gramatike-db --file=tabelas_faltando_criticas.sql

CREATE TABLE IF NOT EXISTS post_image (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    ordem INTEGER DEFAULT 0,
    width INTEGER,
    height INTEGER,
    FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_post_image_post ON post_image(post_id);

-- ============================================================================
-- ESTUDOS (legado)
-- ============================================================================

CREATE TABLE IF NOT EXISTS notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuarie_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,  -- 'curtida', 'comentario', 'seguir', 'mencao', 'sistema'
    titulo TEXT,
    mensagem TEXT,
    link TEXT,
    lida INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    -- Referências opcionais
    from_usuarie_id INTEGER,
    post_id INTEGER,
    comentario_id INTEGER,
    FOREIGN KEY (usuarie_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (from_usuarie_id) REFERENCES user(id),
    FOREIGN KEY (post_id) REFERENCES post(id),
    FOREIGN KEY (comentario_id) REFERENCES comentario(id)
);

CREATE INDEX IF NOT EXISTS idx_notification_usuarie ON notification(usuarie_id);
CREATE INDEX IF NOT EXISTS idx_notification_lida ON notification(lida);
CREATE INDEX IF NOT EXISTS idx_notification_created ON notification(created_at);

-- ============================================================================
-- AMIGUES (relacionamento bidirecional)
-- ============================================================================

CREATE TABLE IF NOT EXISTS amizade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuarie1_id INTEGER NOT NULL,
    usuarie2_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pendente',  -- 'pendente', 'aceita', 'recusada'
    solicitante_id INTEGER NOT NULL,  -- quem enviou o pedido
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT,
    FOREIGN KEY (usuarie1_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (usuarie2_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (solicitante_id) REFERENCES user(id),
    UNIQUE(usuarie1_id, usuarie2_id)
);

CREATE INDEX IF NOT EXISTS idx_amizade_usuarie1 ON amizade(usuarie1_id);
CREATE INDEX IF NOT EXISTS idx_amizade_usuarie2 ON amizade(usuarie2_id);
CREATE INDEX IF NOT EXISTS idx_amizade_status ON amizade(status);

-- ============================================================================
-- UPLOAD DE IMAGENS (para R2)
-- ============================================================================

CREATE TABLE IF NOT EXISTS report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    usuarie_id INTEGER,
    motivo TEXT,
    category TEXT,
    data TEXT DEFAULT (datetime('now')),
    resolved INTEGER DEFAULT 0,
    resolved_at TEXT,
    FOREIGN KEY (post_id) REFERENCES post(id),
    FOREIGN KEY (usuarie_id) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_report_resolved ON report(resolved);

CREATE TABLE IF NOT EXISTS curtida (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuarie_id INTEGER,
    post_id INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuarie_id) REFERENCES user(id),
    FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_curtida_post ON curtida(post_id);

-- ============================================================================
-- CONTEÚDO EDUCACIONAL
-- ============================================================================

CREATE TABLE IF NOT EXISTS mencao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuarie_id INTEGER NOT NULL,  -- quem foi mencionade
    autor_id INTEGER NOT NULL,    -- quem mencionou
    tipo TEXT NOT NULL,           -- 'post' ou 'comentario'
    item_id INTEGER NOT NULL,     -- id do post ou comentário
    lida INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuarie_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (autor_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_mencao_usuarie ON mencao(usuarie_id);
CREATE INDEX IF NOT EXISTS idx_mencao_autor ON mencao(autor_id);
CREATE INDEX IF NOT EXISTS idx_mencao_tipo ON mencao(tipo);

-- ============================================================================
-- HASHTAGS (#) EM POSTS E COMENTÁRIOS
-- ============================================================================

