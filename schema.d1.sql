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

-- ============================================================================
-- TOKENS DE VERIFICAÇÃO E RECUPERAÇÃO DE SENHA
-- ============================================================================

CREATE TABLE IF NOT EXISTS email_token (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    tipo TEXT NOT NULL,  -- 'verify_email', 'reset_password', 'change_email'
    novo_email TEXT,  -- usado para change_email
    created_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT NOT NULL,
    used INTEGER DEFAULT 0,
    used_at TEXT,
    FOREIGN KEY (usuario_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_email_token_token ON email_token(token);
CREATE INDEX IF NOT EXISTS idx_email_token_usuario ON email_token(usuario_id);
CREATE INDEX IF NOT EXISTS idx_email_token_tipo ON email_token(tipo);

-- ============================================================================
-- NOTIFICAÇÕES
-- ============================================================================

CREATE TABLE IF NOT EXISTS notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,  -- 'curtida', 'comentario', 'seguir', 'mencao', 'sistema'
    titulo TEXT,
    mensagem TEXT,
    link TEXT,
    lida INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    -- Referências opcionais
    from_usuario_id INTEGER,
    post_id INTEGER,
    comentario_id INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (from_usuario_id) REFERENCES user(id),
    FOREIGN KEY (post_id) REFERENCES post(id),
    FOREIGN KEY (comentario_id) REFERENCES comentario(id)
);

CREATE INDEX IF NOT EXISTS idx_notification_usuario ON notification(usuario_id);
CREATE INDEX IF NOT EXISTS idx_notification_lida ON notification(lida);
CREATE INDEX IF NOT EXISTS idx_notification_created ON notification(created_at);

-- ============================================================================
-- AMIGUES (relacionamento bidirecional)
-- ============================================================================

CREATE TABLE IF NOT EXISTS amizade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario1_id INTEGER NOT NULL,
    usuario2_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pendente',  -- 'pendente', 'aceita', 'recusada'
    solicitante_id INTEGER NOT NULL,  -- quem enviou o pedido
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT,
    FOREIGN KEY (usuario1_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario2_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (solicitante_id) REFERENCES user(id),
    UNIQUE(usuario1_id, usuario2_id)
);

CREATE INDEX IF NOT EXISTS idx_amizade_usuario1 ON amizade(usuario1_id);
CREATE INDEX IF NOT EXISTS idx_amizade_usuario2 ON amizade(usuario2_id);
CREATE INDEX IF NOT EXISTS idx_amizade_status ON amizade(status);

-- ============================================================================
-- UPLOAD DE IMAGENS (para R2)
-- ============================================================================

CREATE TABLE IF NOT EXISTS upload (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,  -- 'avatar', 'post', 'divulgacao'
    path TEXT NOT NULL,
    filename TEXT,
    content_type TEXT,
    size INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuario_id) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_upload_usuario ON upload(usuario_id);
CREATE INDEX IF NOT EXISTS idx_upload_tipo ON upload(tipo);

-- ============================================================================
-- RATE LIMITING
-- ============================================================================

CREATE TABLE IF NOT EXISTS rate_limit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    attempts INTEGER DEFAULT 1,
    first_attempt TEXT DEFAULT (datetime('now')),
    last_attempt TEXT DEFAULT (datetime('now')),
    blocked_until TEXT,
    UNIQUE(ip_address, endpoint)
);

CREATE INDEX IF NOT EXISTS idx_rate_limit_ip ON rate_limit(ip_address);
CREATE INDEX IF NOT EXISTS idx_rate_limit_endpoint ON rate_limit(endpoint);

-- ============================================================================
-- LOGS DE ATIVIDADE (Auditoria)
-- ============================================================================

CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    acao TEXT NOT NULL,  -- 'login', 'logout', 'post_criar', 'post_curtir', etc.
    descricao TEXT,
    ip_address TEXT,
    user_agent TEXT,
    dados_extra TEXT,  -- JSON com dados adicionais
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuario_id) REFERENCES user(id)
);

CREATE INDEX IF NOT EXISTS idx_activity_log_usuario ON activity_log(usuario_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_acao ON activity_log(acao);
CREATE INDEX IF NOT EXISTS idx_activity_log_created ON activity_log(created_at);

-- ============================================================================
-- GAMIFICAÇÃO - PONTOS E BADGES
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL UNIQUE,
    pontos_total INTEGER DEFAULT 0,
    pontos_exercicios INTEGER DEFAULT 0,
    pontos_posts INTEGER DEFAULT 0,
    pontos_dinamicas INTEGER DEFAULT 0,
    nivel INTEGER DEFAULT 1,
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuario_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_points_usuario ON user_points(usuario_id);
CREATE INDEX IF NOT EXISTS idx_user_points_total ON user_points(pontos_total);

CREATE TABLE IF NOT EXISTS badge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    icone TEXT,  -- emoji ou URL do ícone
    categoria TEXT,  -- 'exercicios', 'social', 'engajamento', 'especial'
    pontos_necessarios INTEGER DEFAULT 0,
    condicao TEXT,  -- descrição da condição para ganhar
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS user_badge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    badge_id INTEGER NOT NULL,
    earned_at TEXT DEFAULT (datetime('now')),
    UNIQUE(usuario_id, badge_id),
    FOREIGN KEY (usuario_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badge(id)
);

CREATE INDEX IF NOT EXISTS idx_user_badge_usuario ON user_badge(usuario_id);

-- ============================================================================
-- PROGRESSO EM EXERCÍCIOS (com controle de pontuação)
-- ============================================================================

CREATE TABLE IF NOT EXISTS exercise_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    resposta_usuarie TEXT,
    correto INTEGER DEFAULT 0,
    pontos_ganhos INTEGER DEFAULT 0,  -- 0 se refez após acerto
    primeira_tentativa INTEGER DEFAULT 1,  -- 1 se é primeira vez
    tempo_resposta INTEGER,  -- tempo em segundos
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuario_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES exercise_question(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_exercise_progress_usuario ON exercise_progress(usuario_id);
CREATE INDEX IF NOT EXISTS idx_exercise_progress_question ON exercise_progress(question_id);

-- Controle de exercícios já pontuados (não pode ganhar ponto novamente)
CREATE TABLE IF NOT EXISTS exercise_scored (
    usuario_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    scored_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (usuario_id, question_id),
    FOREIGN KEY (usuario_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES exercise_question(id) ON DELETE CASCADE
);

-- Listas personalizadas de exercícios
CREATE TABLE IF NOT EXISTS exercise_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    modo TEXT DEFAULT 'estudo',  -- 'estudo' ou 'quiz'
    tempo_limite INTEGER,  -- tempo limite em minutos (para quiz)
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuario_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exercise_list_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    ordem INTEGER DEFAULT 0,
    FOREIGN KEY (list_id) REFERENCES exercise_list(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES exercise_question(id) ON DELETE CASCADE
);

-- Quiz results
CREATE TABLE IF NOT EXISTS quiz_result (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    list_id INTEGER,
    topic_id INTEGER,
    acertos INTEGER DEFAULT 0,
    erros INTEGER DEFAULT 0,
    pontos_ganhos INTEGER DEFAULT 0,
    tempo_total INTEGER,  -- em segundos
    completed_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuario_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (list_id) REFERENCES exercise_list(id),
    FOREIGN KEY (topic_id) REFERENCES exercise_topic(id)
);

-- ============================================================================
-- FLASHCARDS
-- ============================================================================

CREATE TABLE IF NOT EXISTS flashcard_deck (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,  -- NULL = público
    titulo TEXT NOT NULL,
    descricao TEXT,
    is_public INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuario_id) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS flashcard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_id INTEGER NOT NULL,
    frente TEXT NOT NULL,  -- pergunta/termo
    verso TEXT NOT NULL,   -- resposta/definição
    dica TEXT,
    ordem INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (deck_id) REFERENCES flashcard_deck(id) ON DELETE CASCADE
);

-- Progresso de revisão espaçada (Spaced Repetition)
CREATE TABLE IF NOT EXISTS flashcard_review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    flashcard_id INTEGER NOT NULL,
    ease_factor REAL DEFAULT 2.5,  -- Fator de facilidade (algoritmo SM-2)
    interval_days INTEGER DEFAULT 1,  -- Intervalo para próxima revisão
    repetitions INTEGER DEFAULT 0,  -- Número de acertos consecutivos
    next_review TEXT,  -- Data da próxima revisão
    last_review TEXT,
    UNIQUE(usuario_id, flashcard_id),
    FOREIGN KEY (usuario_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (flashcard_id) REFERENCES flashcard(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_flashcard_review_usuario ON flashcard_review(usuario_id);
CREATE INDEX IF NOT EXISTS idx_flashcard_review_next ON flashcard_review(next_review);

-- ============================================================================
-- FAVORITOS/SALVOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS favorito (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,  -- 'post', 'artigo', 'exercicio', 'flashcard', 'dinamica'
    item_id INTEGER NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(usuario_id, tipo, item_id),
    FOREIGN KEY (usuario_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_favorito_usuario ON favorito(usuario_id);
CREATE INDEX IF NOT EXISTS idx_favorito_tipo ON favorito(tipo);

-- ============================================================================
-- HISTÓRICO DE ATIVIDADES DO USUÁRIE
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,  -- 'view', 'complete', 'interact'
    item_tipo TEXT NOT NULL,  -- 'artigo', 'exercicio', 'dinamica', etc.
    item_id INTEGER NOT NULL,
    dados TEXT,  -- JSON com dados extras
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuario_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_history_usuario ON user_history(usuario_id);
CREATE INDEX IF NOT EXISTS idx_user_history_created ON user_history(created_at);

-- ============================================================================
-- PREFERÊNCIAS DE USUÁRIE (UX/Acessibilidade)
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL UNIQUE,
    -- Tema
    tema TEXT DEFAULT 'auto',  -- 'auto', 'light', 'dark', 'high-contrast'
    -- Fonte
    fonte_tamanho TEXT DEFAULT 'normal',  -- 'small', 'normal', 'large', 'extra-large'
    fonte_familia TEXT DEFAULT 'default',  -- 'default', 'dyslexic', 'serif', 'mono'
    -- Acessibilidade
    alto_contraste INTEGER DEFAULT 0,
    animacoes_reduzidas INTEGER DEFAULT 0,
    -- Libras e áudio
    exibir_libras INTEGER DEFAULT 0,
    audio_habilitado INTEGER DEFAULT 0,
    velocidade_audio REAL DEFAULT 1.0,
    -- Notificações
    notificacoes_email INTEGER DEFAULT 1,
    notificacoes_push INTEGER DEFAULT 1,
    -- Outros
    idioma TEXT DEFAULT 'pt-BR',
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (usuario_id) REFERENCES user(id) ON DELETE CASCADE
);

-- ============================================================================
-- CONTEÚDO DE ACESSIBILIDADE (Libras e Áudio)
-- ============================================================================

CREATE TABLE IF NOT EXISTS accessibility_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_conteudo TEXT NOT NULL,  -- 'artigo', 'exercicio', 'dinamica', etc.
    conteudo_id INTEGER NOT NULL,
    -- Libras
    video_libras_url TEXT,
    -- Áudio
    audio_url TEXT,
    audio_duracao INTEGER,  -- duração em segundos
    transcricao TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(tipo_conteudo, conteudo_id)
);

-- ============================================================================
-- MENSAGENS DIRETAS
-- ============================================================================

CREATE TABLE IF NOT EXISTS mensagem_direta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    remetente_id INTEGER NOT NULL,
    destinatarie_id INTEGER NOT NULL,
    conteudo TEXT NOT NULL,
    lida INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (remetente_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (destinatarie_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_mensagem_remetente ON mensagem_direta(remetente_id);
CREATE INDEX IF NOT EXISTS idx_mensagem_destinatarie ON mensagem_direta(destinatarie_id);
CREATE INDEX IF NOT EXISTS idx_mensagem_created ON mensagem_direta(created_at);

-- ============================================================================
-- GRUPOS DE ESTUDO
-- ============================================================================

CREATE TABLE IF NOT EXISTS grupo_estudo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    imagem TEXT,
    criador_id INTEGER NOT NULL,
    is_public INTEGER DEFAULT 1,
    max_membros INTEGER DEFAULT 50,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (criador_id) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS grupo_membro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grupo_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    role TEXT DEFAULT 'membro',  -- 'admin', 'moderador', 'membro'
    joined_at TEXT DEFAULT (datetime('now')),
    UNIQUE(grupo_id, usuario_id),
    FOREIGN KEY (grupo_id) REFERENCES grupo_estudo(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS grupo_mensagem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grupo_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    conteudo TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (grupo_id) REFERENCES grupo_estudo(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES user(id)
);

-- ============================================================================
-- INSERIR BADGES PADRÃO
-- ============================================================================

INSERT OR IGNORE INTO badge (nome, descricao, icone, categoria, pontos_necessarios) VALUES
    ('Iniciante', 'Primeiros passos no Gramátike', '🌱', 'engajamento', 0),
    ('Estudante', 'Completou 10 exercícios', '📚', 'exercicios', 100),
    ('Dedicade', 'Completou 50 exercícios', '🎯', 'exercicios', 500),
    ('Mestre', 'Completou 100 exercícios', '🏆', 'exercicios', 1000),
    ('Social', 'Fez 5 amigues', '👥', 'social', 50),
    ('Popular', 'Recebeu 10 curtidas', '❤️', 'social', 100),
    ('Escritor', 'Criou 5 posts', '✍️', 'engajamento', 50),
    ('Explorador', 'Visitou todas as seções', '🧭', 'engajamento', 75),
    ('Flashcard Pro', 'Criou um deck de flashcards', '🃏', 'exercicios', 30),
    ('Quiz Champion', 'Acertou 10 questões seguidas', '🏅', 'exercicios', 150);

-- ============================================================================
-- INSERIR PREFERÊNCIAS PADRÃO PARA USUÁRIES EXISTENTES
-- ============================================================================

INSERT OR IGNORE INTO user_preferences (usuario_id)
SELECT id FROM user WHERE id NOT IN (SELECT usuario_id FROM user_preferences);
