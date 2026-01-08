-- Simplified Schema for Cloudflare D1 (SQLite)
-- Gramátike - TypeScript Migration
-- Updated: 2026-01-08

DROP TABLE IF EXISTS comentario;
DROP TABLE IF EXISTS curtida;
DROP TABLE IF EXISTS post_likes;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS edu_content;
DROP TABLE IF EXISTS user_session;
DROP TABLE IF EXISTS divulgacao;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    nome TEXT,
    foto_perfil TEXT DEFAULT '/static/img/perfil.png',
    bio TEXT,
    genero TEXT,
    pronome TEXT,
    data_nascimento TEXT,
    email_confirmed INTEGER DEFAULT 0,
    email_confirmed_at TEXT,
    is_admin INTEGER DEFAULT 0,
    is_superadmin INTEGER DEFAULT 0,
    is_banned INTEGER DEFAULT 0,
    banned_at TEXT,
    ban_reason TEXT,
    suspended_until TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuarie_id INTEGER NOT NULL,
    conteudo TEXT NOT NULL,
    imagem TEXT,
    is_deleted INTEGER DEFAULT 0,
    deleted_at TEXT,
    deleted_by INTEGER,
    data TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuarie_id) REFERENCES user(id),
    FOREIGN KEY (deleted_by) REFERENCES user(id)
);

CREATE TABLE post_likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    usuarie_id INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (post_id) REFERENCES post(id),
    FOREIGN KEY (usuarie_id) REFERENCES user(id),
    UNIQUE(post_id, usuarie_id)
);

CREATE TABLE comentario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    usuarie_id INTEGER NOT NULL,
    conteudo TEXT NOT NULL,
    parent_id INTEGER,
    is_deleted INTEGER DEFAULT 0,
    data TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (post_id) REFERENCES post(id),
    FOREIGN KEY (usuarie_id) REFERENCES user(id),
    FOREIGN KEY (parent_id) REFERENCES comentario(id)
);

CREATE TABLE divulgacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    texto TEXT,
    imagem TEXT,
    link TEXT,
    ativo INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE user_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL,
    user_agent TEXT,
    ip_address TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE edu_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    titulo TEXT NOT NULL,
    conteudo TEXT,
    resumo TEXT,
    imagem TEXT,
    arquivo_url TEXT,
    link TEXT,
    autor_id INTEGER,
    tema_id INTEGER,
    is_deleted INTEGER DEFAULT 0,
    data TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (autor_id) REFERENCES user(id)
);

CREATE INDEX idx_post_data ON post(data DESC);
CREATE INDEX idx_user_session_token ON user_session(token);
CREATE INDEX idx_user_session_expires ON user_session(expires_at);
CREATE INDEX idx_post_likes_post ON post_likes(post_id);
CREATE INDEX idx_post_likes_user ON post_likes(usuarie_id);
CREATE INDEX idx_comentario_post ON comentario(post_id);

INSERT INTO user (username, email, password, nome, is_superadmin, is_admin)
VALUES ('gramatike', 'contato@gramatike.com', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'Admin', 1, 1);

INSERT INTO divulgacao (titulo, texto) VALUES ('Bem-vindo!', 'Rede social educativa de português');
