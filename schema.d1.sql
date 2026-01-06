-- Simplified Schema for Cloudflare D1 (SQLite)
-- Gramátike - TypeScript Migration

DROP TABLE IF EXISTS comentario;
DROP TABLE IF EXISTS curtida;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS divulgacao;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    nome TEXT,
    foto_perfil TEXT DEFAULT '/static/img/perfil.png',
    is_admin INTEGER DEFAULT 0,
    is_superadmin INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuarie_id INTEGER NOT NULL,
    conteudo TEXT NOT NULL,
    imagem TEXT,
    deletado INTEGER DEFAULT 0,
    data TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuarie_id) REFERENCES user(id)
);

CREATE TABLE curtida (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    usuarie_id INTEGER NOT NULL,
    data TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (post_id) REFERENCES post(id),
    UNIQUE(post_id, usuarie_id)
);

CREATE TABLE comentario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    usuarie_id INTEGER NOT NULL,
    conteudo TEXT NOT NULL,
    deletado INTEGER DEFAULT 0,
    data TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (post_id) REFERENCES post(id)
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

CREATE INDEX idx_post_data ON post(data DESC);

INSERT INTO user (username, email, senha_hash, nome, is_superadmin, is_admin)
VALUES ('gramatike', 'contato@gramatike.com', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'Admin', 1, 1);

INSERT INTO divulgacao (titulo, texto) VALUES ('Bem-vindo!', 'Rede social educativa de português');
