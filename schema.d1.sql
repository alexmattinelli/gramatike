-- Schema SQL para Cloudflare D1 (SQLite)
-- Gramátike - Plataforma Educacional de Gramática Portuguesa
-- Versão: 1.0.0

-- ============================================================================
-- USUÁRIOS E AUTENTICAÇÃO
-- ============================================================================

CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email_confirmed INTEGER DEFAULT 0,
    email_confirmed_at TEXT,
    foto_perfil TEXT DEFAULT 'img/perfil.png',
    genero TEXT,
    pronome TEXT,
    bio TEXT,
    data_nascimento TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    is_admin INTEGER DEFAULT 0,
    is_superadmin INTEGER DEFAULT 0,
    is_banned INTEGER DEFAULT 0,
    banned_at TEXT,
    ban_reason TEXT,
    suspended_until TEXT
);

CREATE INDEX IF NOT EXISTS idx_user_username ON user(username);
CREATE INDEX IF NOT EXISTS idx_user_email ON user(email);
CREATE INDEX IF NOT EXISTS idx_user_created_at ON user(created_at);

-- Sessões de usuário (para autenticação stateless)
CREATE TABLE IF NOT EXISTS user_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT NOT NULL,
    user_agent TEXT,
    ip_address TEXT,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_session_token ON user_session(token);
CREATE INDEX IF NOT EXISTS idx_session_user ON user_session(user_id);
CREATE INDEX IF NOT EXISTS idx_session_expires ON user_session(expires_at);

-- ============================================================================
-- SEGUIDORES / REDE SOCIAL
-- ============================================================================

CREATE TABLE IF NOT EXISTS seguidores (
    seguidor_id INTEGER NOT NULL,
    seguido_id INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (seguidor_id, seguido_id),
    FOREIGN KEY (seguidor_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (seguido_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_seguidores_seguidor ON seguidores(seguidor_id);
CREATE INDEX IF NOT EXISTS idx_seguidores_seguido ON seguidores(seguido_id);

-- ============================================================================
-- POSTS E INTERAÇÕES
-- ============================================================================

CREATE TABLE IF NOT EXISTS post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    usuario_id INTEGER,
    conteudo TEXT,
    imagem TEXT,
    data TEXT DEFAULT (datetime('now')),
    is_deleted INTEGER DEFAULT 0,
    deleted_at TEXT,
    deleted_by INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES user(id),
    FOREIGN KEY (deleted_by) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_post_usuario_id ON post(usuario_id);
CREATE INDEX IF NOT EXISTS idx_post_data ON post(data);
CREATE INDEX IF NOT EXISTS idx_post_is_deleted ON post(is_deleted);

CREATE TABLE IF NOT EXISTS post_likes (
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comentario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    conteudo TEXT,
    post_id INTEGER,
    data TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuario_id) REFERENCES user(id),
    FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_comentario_post ON comentario(post_id);
CREATE INDEX IF NOT EXISTS idx_comentario_usuario ON comentario(usuario_id);

CREATE TABLE IF NOT EXISTS curtida (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    post_id INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuario_id) REFERENCES user(id),
    FOREIGN KEY (post_id) REFERENCES post(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_curtida_post ON curtida(post_id);

-- ============================================================================
-- CONTEÚDO EDUCACIONAL
-- ============================================================================

CREATE TABLE IF NOT EXISTS edu_topic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area TEXT NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(area, nome)
);

CREATE INDEX IF NOT EXISTS idx_edu_topic_area ON edu_topic(area);

CREATE TABLE IF NOT EXISTS edu_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    titulo TEXT NOT NULL,
    resumo TEXT,
    corpo TEXT,
    url TEXT,
    file_path TEXT,
    extra TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    author_id INTEGER,
    topic_id INTEGER,
    FOREIGN KEY (author_id) REFERENCES user(id),
    FOREIGN KEY (topic_id) REFERENCES edu_topic(id)
);

CREATE INDEX IF NOT EXISTS idx_edu_content_tipo ON edu_content(tipo);
CREATE INDEX IF NOT EXISTS idx_edu_content_created ON edu_content(created_at);

-- ============================================================================
-- EXERCÍCIOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS exercise_topic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS exercise_section (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    ordem INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(topic_id, nome),
    FOREIGN KEY (topic_id) REFERENCES exercise_topic(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_exercise_section_topic ON exercise_section(topic_id);

CREATE TABLE IF NOT EXISTS exercise_question (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    section_id INTEGER,
    enunciado TEXT NOT NULL,
    resposta TEXT,
    dificuldade TEXT,
    tipo TEXT,
    opcoes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (topic_id) REFERENCES exercise_topic(id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES exercise_section(id)
);

CREATE INDEX IF NOT EXISTS idx_exercise_question_topic ON exercise_question(topic_id);
CREATE INDEX IF NOT EXISTS idx_exercise_question_section ON exercise_question(section_id);
CREATE INDEX IF NOT EXISTS idx_exercise_question_tipo ON exercise_question(tipo);

-- ============================================================================
-- DINÂMICAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS dynamic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    titulo TEXT NOT NULL,
    descricao TEXT,
    config TEXT,
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    created_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_dynamic_tipo ON dynamic(tipo);
CREATE INDEX IF NOT EXISTS idx_dynamic_active ON dynamic(active);

CREATE TABLE IF NOT EXISTS dynamic_response (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dynamic_id INTEGER NOT NULL,
    usuario_id INTEGER,
    payload TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (dynamic_id) REFERENCES dynamic(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_dynamic_response_dynamic ON dynamic_response(dynamic_id);
CREATE INDEX IF NOT EXISTS idx_dynamic_response_usuario ON dynamic_response(usuario_id);

CREATE TABLE IF NOT EXISTS word_exclusion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dynamic_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    palavra TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (dynamic_id) REFERENCES dynamic(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES user(id)
);

-- ============================================================================
-- DIVULGAÇÃO E NOVIDADES
-- ============================================================================

CREATE TABLE IF NOT EXISTS divulgacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area TEXT NOT NULL,
    titulo TEXT NOT NULL,
    texto TEXT,
    link TEXT,
    imagem TEXT,
    ordem INTEGER DEFAULT 0,
    ativo INTEGER DEFAULT 1,
    show_on_edu INTEGER DEFAULT 1,
    show_on_index INTEGER DEFAULT 1,
    edu_content_id INTEGER,
    post_id INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (edu_content_id) REFERENCES edu_content(id),
    FOREIGN KEY (post_id) REFERENCES post(id)
);

CREATE INDEX IF NOT EXISTS idx_divulgacao_area ON divulgacao(area);
CREATE INDEX IF NOT EXISTS idx_divulgacao_ativo ON divulgacao(ativo);

CREATE TABLE IF NOT EXISTS edu_novidade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT,
    link TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    author_id INTEGER,
    FOREIGN KEY (author_id) REFERENCES user(id)
);

-- ============================================================================
-- PALAVRAS DO DIA
-- ============================================================================

CREATE TABLE IF NOT EXISTS palavra_do_dia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    palavra TEXT NOT NULL,
    significado TEXT NOT NULL,
    ordem INTEGER DEFAULT 0,
    ativo INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    created_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_palavra_ativo ON palavra_do_dia(ativo);
CREATE INDEX IF NOT EXISTS idx_palavra_ordem ON palavra_do_dia(ordem);

CREATE TABLE IF NOT EXISTS palavra_do_dia_interacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    palavra_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    frase TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (palavra_id) REFERENCES palavra_do_dia(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES user(id)
);

-- ============================================================================
-- MODERAÇÃO
-- ============================================================================

CREATE TABLE IF NOT EXISTS report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    usuario_id INTEGER,
    motivo TEXT,
    category TEXT,
    data TEXT DEFAULT (datetime('now')),
    resolved INTEGER DEFAULT 0,
    resolved_at TEXT,
    FOREIGN KEY (post_id) REFERENCES post(id),
    FOREIGN KEY (usuario_id) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_report_resolved ON report(resolved);

CREATE TABLE IF NOT EXISTS blocked_word (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT UNIQUE NOT NULL,
    category TEXT DEFAULT 'custom',
    created_at TEXT DEFAULT (datetime('now')),
    created_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS support_ticket (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    nome TEXT,
    email TEXT,
    mensagem TEXT NOT NULL,
    status TEXT DEFAULT 'aberto',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT,
    resposta TEXT,
    FOREIGN KEY (usuario_id) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_ticket_status ON support_ticket(status);

-- ============================================================================
-- PROMOÇÕES
-- ============================================================================

CREATE TABLE IF NOT EXISTS promotion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT,
    media_type TEXT DEFAULT 'image',
    media_path TEXT,
    link_destino TEXT,
    ativo INTEGER DEFAULT 1,
    ordem INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    author_id INTEGER,
    FOREIGN KEY (author_id) REFERENCES user(id)
);

-- ============================================================================
-- IMAGENS DE POSTS
-- ============================================================================

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

CREATE TABLE IF NOT EXISTS estudo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    conteudo TEXT NOT NULL
);

-- ============================================================================
-- OUTROS RECURSOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS outro_recurso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT
);
