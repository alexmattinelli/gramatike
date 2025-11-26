-- Gramátike D1 Database Schema
-- Run this script to create tables in Cloudflare D1
-- Command: wrangler d1 execute gramatike --file=schema.sql

-- ============================================================================
-- User table
-- ============================================================================
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    nome TEXT,
    foto_perfil TEXT DEFAULT 'img/perfil.png',
    genero TEXT,
    pronome TEXT,
    bio TEXT,
    data_nascimento TEXT,
    created_at TEXT,
    is_admin INTEGER DEFAULT 0,
    is_superadmin INTEGER DEFAULT 0,
    is_banned INTEGER DEFAULT 0,
    banned_at TEXT,
    ban_reason TEXT,
    suspended_until TEXT,
    email_confirmed INTEGER DEFAULT 0,
    email_confirmed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_user_username ON user(username);
CREATE INDEX IF NOT EXISTS idx_user_email ON user(email);
CREATE INDEX IF NOT EXISTS idx_user_created_at ON user(created_at);

-- ============================================================================
-- Posts table
-- ============================================================================
CREATE TABLE IF NOT EXISTS post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    usuario_id INTEGER,
    conteudo TEXT,
    imagem TEXT,
    data TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_at TEXT,
    deleted_by INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES user(id),
    FOREIGN KEY (deleted_by) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_post_usuario_id ON post(usuario_id);
CREATE INDEX IF NOT EXISTS idx_post_data ON post(data);
CREATE INDEX IF NOT EXISTS idx_post_is_deleted ON post(is_deleted);

-- ============================================================================
-- Post likes (many-to-many)
-- ============================================================================
CREATE TABLE IF NOT EXISTS post_likes (
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (post_id) REFERENCES post(id)
);

-- ============================================================================
-- Comments table
-- ============================================================================
CREATE TABLE IF NOT EXISTS comentario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    conteudo TEXT,
    post_id INTEGER,
    data TEXT,
    FOREIGN KEY (usuario_id) REFERENCES user(id),
    FOREIGN KEY (post_id) REFERENCES post(id)
);

CREATE INDEX IF NOT EXISTS idx_comentario_post_id ON comentario(post_id);
CREATE INDEX IF NOT EXISTS idx_comentario_data ON comentario(data);

-- ============================================================================
-- Followers (many-to-many)
-- ============================================================================
CREATE TABLE IF NOT EXISTS seguidores (
    seguidor_id INTEGER NOT NULL,
    seguido_id INTEGER NOT NULL,
    PRIMARY KEY (seguidor_id, seguido_id),
    FOREIGN KEY (seguidor_id) REFERENCES user(id),
    FOREIGN KEY (seguido_id) REFERENCES user(id)
);

-- ============================================================================
-- Educational Content
-- ============================================================================
CREATE TABLE IF NOT EXISTS edu_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    titulo TEXT NOT NULL,
    resumo TEXT,
    corpo TEXT,
    url TEXT,
    file_path TEXT,
    extra TEXT,
    created_at TEXT,
    author_id INTEGER,
    topic_id INTEGER,
    FOREIGN KEY (author_id) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_edu_content_tipo ON edu_content(tipo);
CREATE INDEX IF NOT EXISTS idx_edu_content_created_at ON edu_content(created_at);

-- ============================================================================
-- Educational Topics
-- ============================================================================
CREATE TABLE IF NOT EXISTS edu_topic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area TEXT NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    created_at TEXT,
    UNIQUE(area, nome)
);

CREATE INDEX IF NOT EXISTS idx_edu_topic_area ON edu_topic(area);

-- ============================================================================
-- Exercise Topics
-- ============================================================================
CREATE TABLE IF NOT EXISTS exercise_topic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    descricao TEXT,
    created_at TEXT
);

-- ============================================================================
-- Exercise Sections
-- ============================================================================
CREATE TABLE IF NOT EXISTS exercise_section (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    ordem INTEGER DEFAULT 0,
    created_at TEXT,
    FOREIGN KEY (topic_id) REFERENCES exercise_topic(id),
    UNIQUE(topic_id, nome)
);

CREATE INDEX IF NOT EXISTS idx_exercise_section_topic_id ON exercise_section(topic_id);

-- ============================================================================
-- Exercise Questions
-- ============================================================================
CREATE TABLE IF NOT EXISTS exercise_question (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    section_id INTEGER,
    enunciado TEXT NOT NULL,
    resposta TEXT,
    dificuldade TEXT,
    tipo TEXT,
    opcoes TEXT,
    created_at TEXT,
    FOREIGN KEY (topic_id) REFERENCES exercise_topic(id),
    FOREIGN KEY (section_id) REFERENCES exercise_section(id)
);

CREATE INDEX IF NOT EXISTS idx_exercise_question_topic_id ON exercise_question(topic_id);
CREATE INDEX IF NOT EXISTS idx_exercise_question_section_id ON exercise_question(section_id);

-- ============================================================================
-- Reports (content moderation)
-- ============================================================================
CREATE TABLE IF NOT EXISTS report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    usuario_id INTEGER,
    motivo TEXT,
    category TEXT,
    data TEXT,
    resolved INTEGER DEFAULT 0,
    resolved_at TEXT,
    FOREIGN KEY (post_id) REFERENCES post(id),
    FOREIGN KEY (usuario_id) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_report_resolved ON report(resolved);

-- ============================================================================
-- Support Tickets
-- ============================================================================
CREATE TABLE IF NOT EXISTS support_ticket (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    nome TEXT,
    email TEXT,
    mensagem TEXT NOT NULL,
    status TEXT DEFAULT 'aberto',
    created_at TEXT,
    updated_at TEXT,
    resposta TEXT,
    FOREIGN KEY (usuario_id) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_support_ticket_status ON support_ticket(status);
CREATE INDEX IF NOT EXISTS idx_support_ticket_created_at ON support_ticket(created_at);

-- ============================================================================
-- Divulgacao (featured content cards)
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
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (edu_content_id) REFERENCES edu_content(id),
    FOREIGN KEY (post_id) REFERENCES post(id)
);

CREATE INDEX IF NOT EXISTS idx_divulgacao_area ON divulgacao(area);
CREATE INDEX IF NOT EXISTS idx_divulgacao_ativo ON divulgacao(ativo);

-- ============================================================================
-- Dynamic Activities (polls, forms, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS dynamic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    titulo TEXT NOT NULL,
    descricao TEXT,
    config TEXT,
    active INTEGER DEFAULT 1,
    created_at TEXT,
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
    created_at TEXT,
    FOREIGN KEY (dynamic_id) REFERENCES dynamic(id),
    FOREIGN KEY (usuario_id) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_dynamic_response_dynamic_id ON dynamic_response(dynamic_id);

-- ============================================================================
-- Word of the Day
-- ============================================================================
CREATE TABLE IF NOT EXISTS palavra_do_dia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    palavra TEXT NOT NULL,
    significado TEXT NOT NULL,
    ordem INTEGER DEFAULT 0,
    ativo INTEGER DEFAULT 1,
    created_at TEXT,
    created_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_palavra_do_dia_ativo ON palavra_do_dia(ativo);
CREATE INDEX IF NOT EXISTS idx_palavra_do_dia_ordem ON palavra_do_dia(ordem);

CREATE TABLE IF NOT EXISTS palavra_do_dia_interacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    palavra_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    frase TEXT,
    created_at TEXT,
    FOREIGN KEY (palavra_id) REFERENCES palavra_do_dia(id),
    FOREIGN KEY (usuario_id) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_palavra_interacao_palavra_id ON palavra_do_dia_interacao(palavra_id);

-- ============================================================================
-- Blocked Words (content moderation)
-- ============================================================================
CREATE TABLE IF NOT EXISTS blocked_word (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT UNIQUE NOT NULL,
    category TEXT DEFAULT 'custom',
    created_at TEXT,
    created_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_blocked_word_category ON blocked_word(category);

-- ============================================================================
-- Post Images (normalized)
-- ============================================================================
CREATE TABLE IF NOT EXISTS post_image (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    ordem INTEGER DEFAULT 0,
    width INTEGER,
    height INTEGER,
    FOREIGN KEY (post_id) REFERENCES post(id)
);

CREATE INDEX IF NOT EXISTS idx_post_image_post_id ON post_image(post_id);

-- ============================================================================
-- Edu Novidades (news/updates)
-- ============================================================================
CREATE TABLE IF NOT EXISTS edu_novidade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT,
    link TEXT,
    created_at TEXT,
    author_id INTEGER,
    FOREIGN KEY (author_id) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_edu_novidade_created_at ON edu_novidade(created_at);

-- ============================================================================
-- Insert demo user for testing (password: demo123)
-- Hash format: salt:hash where hash = SHA256(salt + password)
-- ============================================================================
INSERT OR IGNORE INTO user (id, username, email, password, nome, is_admin, is_superadmin, created_at)
VALUES (1, 'demo', 'demo@gramatike.com', 
        'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6:' || 
        lower(hex(sha256('a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6demo123'))),
        'Demo User', 1, 0, datetime('now'));
