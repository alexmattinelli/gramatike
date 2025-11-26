# workers/db.py
# Database helpers para Cloudflare D1
# Este módulo fornece funções para interagir com o D1 SQLite

import json
from datetime import datetime, timedelta
import hashlib
import secrets

# ============================================================================
# HELPERS DE DATABASE
# ============================================================================

def row_to_dict(row, columns):
    """Converte uma row do D1 para dicionário."""
    if row is None:
        return None
    return dict(zip(columns, row))


def rows_to_list(rows, columns):
    """Converte múltiplas rows do D1 para lista de dicionários."""
    return [row_to_dict(row, columns) for row in rows]


# ============================================================================
# AUTENTICAÇÃO
# ============================================================================

def hash_password(password):
    """Hash simples de senha usando SHA-256 + salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{hashed.hex()}"


def verify_password(stored_hash, password):
    """Verifica se a senha corresponde ao hash armazenado."""
    try:
        salt, hashed = stored_hash.split(':')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return new_hash.hex() == hashed
    except:
        return False


def generate_session_token():
    """Gera um token de sessão seguro."""
    return secrets.token_urlsafe(32)


# ============================================================================
# QUERIES - USUÁRIOS
# ============================================================================

async def get_user_by_id(db, user_id):
    """Busca usuário por ID."""
    result = await db.prepare(
        "SELECT * FROM user WHERE id = ?"
    ).bind(user_id).first()
    if result:
        return dict(result)
    return None


async def get_user_by_username(db, username):
    """Busca usuário por username."""
    result = await db.prepare(
        "SELECT * FROM user WHERE username = ?"
    ).bind(username).first()
    if result:
        return dict(result)
    return None


async def get_user_by_email(db, email):
    """Busca usuário por email."""
    result = await db.prepare(
        "SELECT * FROM user WHERE email = ?"
    ).bind(email).first()
    if result:
        return dict(result)
    return None


async def create_user(db, username, email, password, nome=None):
    """Cria um novo usuário."""
    hashed = hash_password(password)
    result = await db.prepare("""
        INSERT INTO user (username, email, password, nome, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        RETURNING id
    """).bind(username, email, hashed, nome).first()
    return result['id'] if result else None


async def update_user_profile(db, user_id, **kwargs):
    """Atualiza o perfil do usuário."""
    allowed = ['nome', 'bio', 'genero', 'pronome', 'foto_perfil', 'data_nascimento']
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not updates:
        return False
    
    set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [user_id]
    
    await db.prepare(f"""
        UPDATE user SET {set_clause} WHERE id = ?
    """).bind(*values).run()
    return True


# ============================================================================
# QUERIES - SESSÕES
# ============================================================================

async def create_session(db, user_id, user_agent=None, ip_address=None):
    """Cria uma nova sessão de usuário."""
    token = generate_session_token()
    expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()
    
    await db.prepare("""
        INSERT INTO user_session (user_id, token, expires_at, user_agent, ip_address)
        VALUES (?, ?, ?, ?, ?)
    """).bind(user_id, token, expires_at, user_agent, ip_address).run()
    
    return token


async def get_session(db, token):
    """Busca sessão pelo token."""
    result = await db.prepare("""
        SELECT s.*, u.username, u.email, u.is_admin, u.is_superadmin, u.is_banned
        FROM user_session s
        JOIN user u ON s.user_id = u.id
        WHERE s.token = ? AND s.expires_at > datetime('now')
    """).bind(token).first()
    if result:
        return dict(result)
    return None


async def delete_session(db, token):
    """Remove uma sessão (logout)."""
    await db.prepare(
        "DELETE FROM user_session WHERE token = ?"
    ).bind(token).run()


async def cleanup_expired_sessions(db):
    """Remove sessões expiradas."""
    await db.prepare(
        "DELETE FROM user_session WHERE expires_at < datetime('now')"
    ).run()


# ============================================================================
# QUERIES - POSTS
# ============================================================================

async def get_posts(db, page=1, per_page=20, user_id=None, include_deleted=False):
    """Lista posts com paginação."""
    offset = (page - 1) * per_page
    
    # Build query with proper parameterization
    if user_id and not include_deleted:
        result = await db.prepare("""
            SELECT p.*, u.username, u.foto_perfil,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                   (SELECT COUNT(*) FROM comentario WHERE post_id = p.id) as comment_count
            FROM post p
            LEFT JOIN user u ON p.usuario_id = u.id
            WHERE p.is_deleted = 0 AND p.usuario_id = ?
            ORDER BY p.data DESC
            LIMIT ? OFFSET ?
        """).bind(user_id, per_page, offset).all()
    elif user_id:
        result = await db.prepare("""
            SELECT p.*, u.username, u.foto_perfil,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                   (SELECT COUNT(*) FROM comentario WHERE post_id = p.id) as comment_count
            FROM post p
            LEFT JOIN user u ON p.usuario_id = u.id
            WHERE p.usuario_id = ?
            ORDER BY p.data DESC
            LIMIT ? OFFSET ?
        """).bind(user_id, per_page, offset).all()
    elif not include_deleted:
        result = await db.prepare("""
            SELECT p.*, u.username, u.foto_perfil,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                   (SELECT COUNT(*) FROM comentario WHERE post_id = p.id) as comment_count
            FROM post p
            LEFT JOIN user u ON p.usuario_id = u.id
            WHERE p.is_deleted = 0
            ORDER BY p.data DESC
            LIMIT ? OFFSET ?
        """).bind(per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT p.*, u.username, u.foto_perfil,
                   (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
                   (SELECT COUNT(*) FROM comentario WHERE post_id = p.id) as comment_count
            FROM post p
            LEFT JOIN user u ON p.usuario_id = u.id
            ORDER BY p.data DESC
            LIMIT ? OFFSET ?
        """).bind(per_page, offset).all()
    
    return [dict(row) for row in result.results] if result.results else []


async def get_post_by_id(db, post_id):
    """Busca post por ID."""
    result = await db.prepare("""
        SELECT p.*, u.username, u.foto_perfil,
               (SELECT COUNT(*) FROM post_likes WHERE post_id = p.id) as like_count,
               (SELECT COUNT(*) FROM comentario WHERE post_id = p.id) as comment_count
        FROM post p
        LEFT JOIN user u ON p.usuario_id = u.id
        WHERE p.id = ?
    """).bind(post_id).first()
    if result:
        return dict(result)
    return None


async def create_post(db, usuario_id, conteudo, imagem=None):
    """Cria um novo post."""
    result = await db.prepare("""
        INSERT INTO post (usuario_id, usuario, conteudo, imagem, data)
        SELECT ?, username, ?, ?, datetime('now')
        FROM user WHERE id = ?
        RETURNING id
    """).bind(usuario_id, conteudo, imagem, usuario_id).first()
    return result['id'] if result else None


async def delete_post(db, post_id, deleted_by=None):
    """Soft delete de um post."""
    await db.prepare("""
        UPDATE post SET is_deleted = 1, deleted_at = datetime('now'), deleted_by = ?
        WHERE id = ?
    """).bind(deleted_by, post_id).run()


async def like_post(db, user_id, post_id):
    """Curte um post."""
    try:
        await db.prepare("""
            INSERT INTO post_likes (user_id, post_id) VALUES (?, ?)
        """).bind(user_id, post_id).run()
        return True
    except:
        return False


async def unlike_post(db, user_id, post_id):
    """Remove curtida de um post."""
    await db.prepare("""
        DELETE FROM post_likes WHERE user_id = ? AND post_id = ?
    """).bind(user_id, post_id).run()


async def has_liked(db, user_id, post_id):
    """Verifica se usuário curtiu o post."""
    result = await db.prepare("""
        SELECT 1 FROM post_likes WHERE user_id = ? AND post_id = ?
    """).bind(user_id, post_id).first()
    return result is not None


# ============================================================================
# QUERIES - COMENTÁRIOS
# ============================================================================

async def get_comments(db, post_id, page=1, per_page=50):
    """Lista comentários de um post."""
    offset = (page - 1) * per_page
    
    result = await db.prepare("""
        SELECT c.*, u.username, u.foto_perfil
        FROM comentario c
        LEFT JOIN user u ON c.usuario_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.data ASC
        LIMIT ? OFFSET ?
    """).bind(post_id, per_page, offset).all()
    
    return [dict(row) for row in result.results] if result.results else []


async def create_comment(db, post_id, usuario_id, conteudo):
    """Cria um novo comentário."""
    result = await db.prepare("""
        INSERT INTO comentario (post_id, usuario_id, conteudo, data)
        VALUES (?, ?, ?, datetime('now'))
        RETURNING id
    """).bind(post_id, usuario_id, conteudo).first()
    return result['id'] if result else None


# ============================================================================
# QUERIES - SEGUIDORES
# ============================================================================

async def follow_user(db, seguidor_id, seguido_id):
    """Seguir um usuário."""
    if seguidor_id == seguido_id:
        return False
    try:
        await db.prepare("""
            INSERT INTO seguidores (seguidor_id, seguido_id) VALUES (?, ?)
        """).bind(seguidor_id, seguido_id).run()
        return True
    except:
        return False


async def unfollow_user(db, seguidor_id, seguido_id):
    """Deixar de seguir um usuário."""
    await db.prepare("""
        DELETE FROM seguidores WHERE seguidor_id = ? AND seguido_id = ?
    """).bind(seguidor_id, seguido_id).run()


async def is_following(db, seguidor_id, seguido_id):
    """Verifica se está seguindo."""
    result = await db.prepare("""
        SELECT 1 FROM seguidores WHERE seguidor_id = ? AND seguido_id = ?
    """).bind(seguidor_id, seguido_id).first()
    return result is not None


async def get_followers(db, user_id):
    """Lista seguidores de um usuário."""
    result = await db.prepare("""
        SELECT u.id, u.username, u.nome, u.foto_perfil
        FROM seguidores s
        JOIN user u ON s.seguidor_id = u.id
        WHERE s.seguido_id = ?
    """).bind(user_id).all()
    return [dict(row) for row in result.results] if result.results else []


async def get_following(db, user_id):
    """Lista quem o usuário segue."""
    result = await db.prepare("""
        SELECT u.id, u.username, u.nome, u.foto_perfil
        FROM seguidores s
        JOIN user u ON s.seguido_id = u.id
        WHERE s.seguidor_id = ?
    """).bind(user_id).all()
    return [dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - CONTEÚDO EDUCACIONAL
# ============================================================================

async def get_edu_contents(db, tipo=None, page=1, per_page=20):
    """Lista conteúdos educacionais."""
    offset = (page - 1) * per_page
    
    if tipo:
        result = await db.prepare("""
            SELECT e.*, u.username as author_name, t.nome as topic_name
            FROM edu_content e
            LEFT JOIN user u ON e.author_id = u.id
            LEFT JOIN edu_topic t ON e.topic_id = t.id
            WHERE tipo = ?
            ORDER BY e.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(tipo, per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT e.*, u.username as author_name, t.nome as topic_name
            FROM edu_content e
            LEFT JOIN user u ON e.author_id = u.id
            LEFT JOIN edu_topic t ON e.topic_id = t.id
            ORDER BY e.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(per_page, offset).all()
    
    return [dict(row) for row in result.results] if result.results else []


async def get_edu_content_by_id(db, content_id):
    """Busca conteúdo educacional por ID."""
    result = await db.prepare("""
        SELECT e.*, u.username as author_name, t.nome as topic_name
        FROM edu_content e
        LEFT JOIN user u ON e.author_id = u.id
        LEFT JOIN edu_topic t ON e.topic_id = t.id
        WHERE e.id = ?
    """).bind(content_id).first()
    if result:
        return dict(result)
    return None


async def search_edu_contents(db, query, tipo=None):
    """Pesquisa conteúdos educacionais."""
    search_term = f"%{query}%"
    
    if tipo:
        result = await db.prepare("""
            SELECT e.*, u.username as author_name
            FROM edu_content e
            LEFT JOIN user u ON e.author_id = u.id
            WHERE (e.titulo LIKE ? OR e.resumo LIKE ? OR e.corpo LIKE ?)
            AND tipo = ?
            ORDER BY e.created_at DESC
            LIMIT 50
        """).bind(search_term, search_term, search_term, tipo).all()
    else:
        result = await db.prepare("""
            SELECT e.*, u.username as author_name
            FROM edu_content e
            LEFT JOIN user u ON e.author_id = u.id
            WHERE (e.titulo LIKE ? OR e.resumo LIKE ? OR e.corpo LIKE ?)
            ORDER BY e.created_at DESC
            LIMIT 50
        """).bind(search_term, search_term, search_term).all()
    
    return [dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - EXERCÍCIOS
# ============================================================================

async def get_exercise_topics(db):
    """Lista tópicos de exercícios."""
    result = await db.prepare("""
        SELECT t.*, 
               (SELECT COUNT(*) FROM exercise_question WHERE topic_id = t.id) as question_count
        FROM exercise_topic t
        ORDER BY t.nome
    """).all()
    return [dict(row) for row in result.results] if result.results else []


async def get_exercise_questions(db, topic_id=None, section_id=None):
    """Lista questões de exercícios."""
    if topic_id and section_id:
        result = await db.prepare("""
            SELECT q.*, t.nome as topic_name, s.nome as section_name
            FROM exercise_question q
            LEFT JOIN exercise_topic t ON q.topic_id = t.id
            LEFT JOIN exercise_section s ON q.section_id = s.id
            WHERE q.topic_id = ? AND q.section_id = ?
            ORDER BY q.created_at DESC
        """).bind(topic_id, section_id).all()
    elif topic_id:
        result = await db.prepare("""
            SELECT q.*, t.nome as topic_name, s.nome as section_name
            FROM exercise_question q
            LEFT JOIN exercise_topic t ON q.topic_id = t.id
            LEFT JOIN exercise_section s ON q.section_id = s.id
            WHERE q.topic_id = ?
            ORDER BY q.created_at DESC
        """).bind(topic_id).all()
    elif section_id:
        result = await db.prepare("""
            SELECT q.*, t.nome as topic_name, s.nome as section_name
            FROM exercise_question q
            LEFT JOIN exercise_topic t ON q.topic_id = t.id
            LEFT JOIN exercise_section s ON q.section_id = s.id
            WHERE q.section_id = ?
            ORDER BY q.created_at DESC
        """).bind(section_id).all()
    else:
        result = await db.prepare("""
            SELECT q.*, t.nome as topic_name, s.nome as section_name
            FROM exercise_question q
            LEFT JOIN exercise_topic t ON q.topic_id = t.id
            LEFT JOIN exercise_section s ON q.section_id = s.id
            ORDER BY q.created_at DESC
        """).all()
    
    return [dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - DINÂMICAS
# ============================================================================

async def get_dynamics(db, active_only=True):
    """Lista dinâmicas."""
    if active_only:
        result = await db.prepare("""
            SELECT d.*, u.username as author_name,
                   (SELECT COUNT(*) FROM dynamic_response WHERE dynamic_id = d.id) as response_count
            FROM dynamic d
            LEFT JOIN user u ON d.created_by = u.id
            WHERE active = 1
            ORDER BY d.created_at DESC
        """).all()
    else:
        result = await db.prepare("""
            SELECT d.*, u.username as author_name,
                   (SELECT COUNT(*) FROM dynamic_response WHERE dynamic_id = d.id) as response_count
            FROM dynamic d
            LEFT JOIN user u ON d.created_by = u.id
            ORDER BY d.created_at DESC
        """).all()
    
    return [dict(row) for row in result.results] if result.results else []


async def get_dynamic_by_id(db, dynamic_id):
    """Busca dinâmica por ID."""
    result = await db.prepare("""
        SELECT d.*, u.username as author_name
        FROM dynamic d
        LEFT JOIN user u ON d.created_by = u.id
        WHERE d.id = ?
    """).bind(dynamic_id).first()
    if result:
        return dict(result)
    return None


async def get_dynamic_responses(db, dynamic_id):
    """Lista respostas de uma dinâmica."""
    result = await db.prepare("""
        SELECT r.*, u.username
        FROM dynamic_response r
        LEFT JOIN user u ON r.usuario_id = u.id
        WHERE r.dynamic_id = ?
        ORDER BY r.created_at DESC
    """).bind(dynamic_id).all()
    
    return [dict(row) for row in result.results] if result.results else []


async def submit_dynamic_response(db, dynamic_id, usuario_id, payload):
    """Submete resposta para uma dinâmica."""
    payload_json = json.dumps(payload) if isinstance(payload, dict) else payload
    
    result = await db.prepare("""
        INSERT INTO dynamic_response (dynamic_id, usuario_id, payload)
        VALUES (?, ?, ?)
        RETURNING id
    """).bind(dynamic_id, usuario_id, payload_json).first()
    return result['id'] if result else None


# ============================================================================
# QUERIES - PALAVRAS DO DIA
# ============================================================================

async def get_palavras_do_dia(db, ativas_only=True):
    """Lista palavras do dia."""
    if ativas_only:
        result = await db.prepare("""
            SELECT p.*, 
                   (SELECT COUNT(*) FROM palavra_do_dia_interacao WHERE palavra_id = p.id) as interacao_count
            FROM palavra_do_dia p
            WHERE ativo = 1
            ORDER BY p.ordem, p.created_at DESC
        """).all()
    else:
        result = await db.prepare("""
            SELECT p.*, 
                   (SELECT COUNT(*) FROM palavra_do_dia_interacao WHERE palavra_id = p.id) as interacao_count
            FROM palavra_do_dia p
            ORDER BY p.ordem, p.created_at DESC
        """).all()
    
    return [dict(row) for row in result.results] if result.results else []


async def get_palavra_do_dia_atual(db):
    """Busca a palavra do dia atual (primeira ativa)."""
    result = await db.prepare("""
        SELECT * FROM palavra_do_dia 
        WHERE ativo = 1 
        ORDER BY ordem, created_at DESC 
        LIMIT 1
    """).first()
    if result:
        return dict(result)
    return None


# ============================================================================
# QUERIES - DIVULGAÇÃO / NOVIDADES
# ============================================================================

async def get_divulgacoes(db, area=None, show_on_edu=None, show_on_index=None):
    """Lista divulgações."""
    # Build query based on conditions - using parameterized queries
    if area and show_on_edu and show_on_index:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND area = ? AND show_on_edu = 1 AND show_on_index = 1
            ORDER BY ordem, created_at DESC
        """).bind(area).all()
    elif area and show_on_edu:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND area = ? AND show_on_edu = 1
            ORDER BY ordem, created_at DESC
        """).bind(area).all()
    elif area and show_on_index:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND area = ? AND show_on_index = 1
            ORDER BY ordem, created_at DESC
        """).bind(area).all()
    elif show_on_edu and show_on_index:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND show_on_edu = 1 AND show_on_index = 1
            ORDER BY ordem, created_at DESC
        """).all()
    elif area:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND area = ?
            ORDER BY ordem, created_at DESC
        """).bind(area).all()
    elif show_on_edu:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND show_on_edu = 1
            ORDER BY ordem, created_at DESC
        """).all()
    elif show_on_index:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1 AND show_on_index = 1
            ORDER BY ordem, created_at DESC
        """).all()
    else:
        result = await db.prepare("""
            SELECT * FROM divulgacao
            WHERE ativo = 1
            ORDER BY ordem, created_at DESC
        """).all()
    
    return [dict(row) for row in result.results] if result.results else []


async def get_novidades(db, limit=5):
    """Lista últimas novidades."""
    result = await db.prepare("""
        SELECT n.*, u.username as author_name
        FROM edu_novidade n
        LEFT JOIN user u ON n.author_id = u.id
        ORDER BY n.created_at DESC
        LIMIT ?
    """).bind(limit).all()
    
    return [dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - TOKENS DE EMAIL (Verificação e Recuperação de Senha)
# ============================================================================

def generate_email_token():
    """Gera um token de email seguro."""
    return secrets.token_urlsafe(32)


async def create_email_token(db, usuario_id, tipo, expires_hours=24, novo_email=None):
    """Cria um token de verificação/recuperação."""
    token = generate_email_token()
    expires_at = (datetime.utcnow() + timedelta(hours=expires_hours)).isoformat()
    
    if novo_email:
        await db.prepare("""
            INSERT INTO email_token (usuario_id, token, tipo, novo_email, expires_at)
            VALUES (?, ?, ?, ?, ?)
        """).bind(usuario_id, token, tipo, novo_email, expires_at).run()
    else:
        await db.prepare("""
            INSERT INTO email_token (usuario_id, token, tipo, expires_at)
            VALUES (?, ?, ?, ?)
        """).bind(usuario_id, token, tipo, expires_at).run()
    
    return token


async def verify_email_token(db, token, tipo):
    """Verifica e retorna dados do token se válido."""
    result = await db.prepare("""
        SELECT * FROM email_token
        WHERE token = ? AND tipo = ? AND used = 0 AND expires_at > datetime('now')
    """).bind(token, tipo).first()
    
    if result:
        return dict(result)
    return None


async def use_email_token(db, token):
    """Marca token como usado."""
    await db.prepare("""
        UPDATE email_token SET used = 1, used_at = datetime('now')
        WHERE token = ?
    """).bind(token).run()


async def confirm_user_email(db, usuario_id):
    """Confirma o email de usuárie."""
    await db.prepare("""
        UPDATE user SET email_confirmed = 1, email_confirmed_at = datetime('now')
        WHERE id = ?
    """).bind(usuario_id).run()


async def update_user_password(db, usuario_id, new_password):
    """Atualiza a senha de usuárie."""
    hashed = hash_password(new_password)
    await db.prepare("""
        UPDATE user SET password = ?
        WHERE id = ?
    """).bind(hashed, usuario_id).run()


async def update_user_email(db, usuario_id, new_email):
    """Atualiza o email de usuárie."""
    await db.prepare("""
        UPDATE user SET email = ?, email_confirmed = 0
        WHERE id = ?
    """).bind(new_email, usuario_id).run()


# ============================================================================
# QUERIES - NOTIFICAÇÕES
# ============================================================================

async def create_notification(db, usuario_id, tipo, titulo=None, mensagem=None, link=None,
                              from_usuario_id=None, post_id=None, comentario_id=None):
    """Cria uma notificação para usuárie."""
    result = await db.prepare("""
        INSERT INTO notification 
        (usuario_id, tipo, titulo, mensagem, link, from_usuario_id, post_id, comentario_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING id
    """).bind(usuario_id, tipo, titulo, mensagem, link, 
              from_usuario_id, post_id, comentario_id).first()
    return result['id'] if result else None


async def get_notifications(db, usuario_id, apenas_nao_lidas=False, page=1, per_page=20):
    """Lista notificações de usuárie."""
    offset = (page - 1) * per_page
    
    if apenas_nao_lidas:
        result = await db.prepare("""
            SELECT n.*, u.username as from_username, u.foto_perfil as from_foto
            FROM notification n
            LEFT JOIN user u ON n.from_usuario_id = u.id
            WHERE n.usuario_id = ? AND n.lida = 0
            ORDER BY n.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(usuario_id, per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT n.*, u.username as from_username, u.foto_perfil as from_foto
            FROM notification n
            LEFT JOIN user u ON n.from_usuario_id = u.id
            WHERE n.usuario_id = ?
            ORDER BY n.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(usuario_id, per_page, offset).all()
    
    return [dict(row) for row in result.results] if result.results else []


async def count_unread_notifications(db, usuario_id):
    """Conta notificações não lidas de usuárie."""
    result = await db.prepare("""
        SELECT COUNT(*) as count FROM notification
        WHERE usuario_id = ? AND lida = 0
    """).bind(usuario_id).first()
    return result['count'] if result else 0


async def mark_notification_read(db, notification_id, usuario_id):
    """Marca notificação como lida."""
    await db.prepare("""
        UPDATE notification SET lida = 1
        WHERE id = ? AND usuario_id = ?
    """).bind(notification_id, usuario_id).run()


async def mark_all_notifications_read(db, usuario_id):
    """Marca todas as notificações como lidas."""
    await db.prepare("""
        UPDATE notification SET lida = 1
        WHERE usuario_id = ? AND lida = 0
    """).bind(usuario_id).run()


# ============================================================================
# QUERIES - AMIGUES
# ============================================================================

async def send_friend_request(db, solicitante_id, destinatarie_id):
    """Envia pedido de amizade."""
    # Verifica se já existe relação
    existing = await db.prepare("""
        SELECT * FROM amizade
        WHERE (usuario1_id = ? AND usuario2_id = ?)
           OR (usuario1_id = ? AND usuario2_id = ?)
    """).bind(solicitante_id, destinatarie_id, destinatarie_id, solicitante_id).first()
    
    if existing:
        return None, "Já existe uma solicitação de amizade"
    
    # Cria solicitação
    result = await db.prepare("""
        INSERT INTO amizade (usuario1_id, usuario2_id, solicitante_id, status)
        VALUES (?, ?, ?, 'pendente')
        RETURNING id
    """).bind(solicitante_id, destinatarie_id, solicitante_id).first()
    
    # Notifica destinatárie
    await create_notification(db, destinatarie_id, 'amizade_pedido',
                              titulo='Novo pedido de amizade',
                              from_usuario_id=solicitante_id)
    
    return result['id'] if result else None, None


async def respond_friend_request(db, amizade_id, usuario_id, aceitar=True):
    """Responde a pedido de amizade."""
    # Verifica se o pedido existe e é para este usuárie
    amizade = await db.prepare("""
        SELECT * FROM amizade
        WHERE id = ? AND status = 'pendente'
        AND (usuario1_id = ? OR usuario2_id = ?)
        AND solicitante_id != ?
    """).bind(amizade_id, usuario_id, usuario_id, usuario_id).first()
    
    if not amizade:
        return False, "Pedido não encontrado"
    
    status = 'aceita' if aceitar else 'recusada'
    await db.prepare("""
        UPDATE amizade SET status = ?, updated_at = datetime('now')
        WHERE id = ?
    """).bind(status, amizade_id).run()
    
    # Notifica solicitante
    solicitante_id = amizade['solicitante_id']
    if aceitar:
        await create_notification(db, solicitante_id, 'amizade_aceita',
                                  titulo='Pedido de amizade aceito!',
                                  from_usuario_id=usuario_id)
    
    return True, None


async def get_amigues(db, usuario_id):
    """Lista amigues de usuárie (amizades aceitas)."""
    result = await db.prepare("""
        SELECT u.id, u.username, u.nome, u.foto_perfil, a.created_at as amigues_desde
        FROM amizade a
        JOIN user u ON (
            (a.usuario1_id = ? AND a.usuario2_id = u.id)
            OR (a.usuario2_id = ? AND a.usuario1_id = u.id)
        )
        WHERE a.status = 'aceita'
        ORDER BY u.nome, u.username
    """).bind(usuario_id, usuario_id).all()
    
    return [dict(row) for row in result.results] if result.results else []


async def get_pending_friend_requests(db, usuario_id):
    """Lista pedidos de amizade pendentes recebidos."""
    result = await db.prepare("""
        SELECT a.*, u.username, u.nome, u.foto_perfil
        FROM amizade a
        JOIN user u ON a.solicitante_id = u.id
        WHERE (a.usuario1_id = ? OR a.usuario2_id = ?)
        AND a.status = 'pendente'
        AND a.solicitante_id != ?
        ORDER BY a.created_at DESC
    """).bind(usuario_id, usuario_id, usuario_id).all()
    
    return [dict(row) for row in result.results] if result.results else []


async def are_amigues(db, usuario1_id, usuario2_id):
    """Verifica se dois usuáries são amigues."""
    result = await db.prepare("""
        SELECT 1 FROM amizade
        WHERE ((usuario1_id = ? AND usuario2_id = ?)
            OR (usuario1_id = ? AND usuario2_id = ?))
        AND status = 'aceita'
    """).bind(usuario1_id, usuario2_id, usuario2_id, usuario1_id).first()
    return result is not None


async def remove_amizade(db, usuario_id, amigue_id):
    """Remove amizade."""
    await db.prepare("""
        DELETE FROM amizade
        WHERE ((usuario1_id = ? AND usuario2_id = ?)
            OR (usuario1_id = ? AND usuario2_id = ?))
        AND status = 'aceita'
    """).bind(usuario_id, amigue_id, amigue_id, usuario_id).run()


# ============================================================================
# QUERIES - DENÚNCIAS
# ============================================================================

async def create_report(db, post_id, usuario_id, motivo, category=None):
    """Cria uma denúncia de post."""
    result = await db.prepare("""
        INSERT INTO report (post_id, usuario_id, motivo, category)
        VALUES (?, ?, ?, ?)
        RETURNING id
    """).bind(post_id, usuario_id, motivo, category).first()
    return result['id'] if result else None


async def get_reports(db, apenas_pendentes=True, page=1, per_page=20):
    """Lista denúncias (para admin)."""
    offset = (page - 1) * per_page
    
    if apenas_pendentes:
        result = await db.prepare("""
            SELECT r.*, p.conteudo as post_conteudo, u.username as reporter_username
            FROM report r
            LEFT JOIN post p ON r.post_id = p.id
            LEFT JOIN user u ON r.usuario_id = u.id
            WHERE r.resolved = 0
            ORDER BY r.data DESC
            LIMIT ? OFFSET ?
        """).bind(per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT r.*, p.conteudo as post_conteudo, u.username as reporter_username
            FROM report r
            LEFT JOIN post p ON r.post_id = p.id
            LEFT JOIN user u ON r.usuario_id = u.id
            ORDER BY r.data DESC
            LIMIT ? OFFSET ?
        """).bind(per_page, offset).all()
    
    return [dict(row) for row in result.results] if result.results else []


async def resolve_report(db, report_id, resolver_id=None):
    """Resolve uma denúncia."""
    await db.prepare("""
        UPDATE report SET resolved = 1, resolved_at = datetime('now')
        WHERE id = ?
    """).bind(report_id).run()


async def count_pending_reports(db):
    """Conta denúncias pendentes."""
    result = await db.prepare("""
        SELECT COUNT(*) as count FROM report WHERE resolved = 0
    """).first()
    return result['count'] if result else 0


# ============================================================================
# QUERIES - SUPORTE/TICKETS
# ============================================================================

async def create_support_ticket(db, mensagem, usuario_id=None, nome=None, email=None):
    """Cria um ticket de suporte."""
    result = await db.prepare("""
        INSERT INTO support_ticket (usuario_id, nome, email, mensagem)
        VALUES (?, ?, ?, ?)
        RETURNING id
    """).bind(usuario_id, nome, email, mensagem).first()
    return result['id'] if result else None


async def get_support_tickets(db, status=None, page=1, per_page=20):
    """Lista tickets de suporte (para admin)."""
    offset = (page - 1) * per_page
    
    if status:
        result = await db.prepare("""
            SELECT t.*, u.username
            FROM support_ticket t
            LEFT JOIN user u ON t.usuario_id = u.id
            WHERE t.status = ?
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(status, per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT t.*, u.username
            FROM support_ticket t
            LEFT JOIN user u ON t.usuario_id = u.id
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
        """).bind(per_page, offset).all()
    
    return [dict(row) for row in result.results] if result.results else []


async def get_user_tickets(db, usuario_id):
    """Lista tickets de usuárie."""
    result = await db.prepare("""
        SELECT * FROM support_ticket
        WHERE usuario_id = ?
        ORDER BY created_at DESC
    """).bind(usuario_id).all()
    
    return [dict(row) for row in result.results] if result.results else []


async def respond_ticket(db, ticket_id, resposta):
    """Responde a um ticket de suporte."""
    await db.prepare("""
        UPDATE support_ticket 
        SET resposta = ?, status = 'respondido', updated_at = datetime('now')
        WHERE id = ?
    """).bind(resposta, ticket_id).run()


async def close_ticket(db, ticket_id):
    """Fecha um ticket de suporte."""
    await db.prepare("""
        UPDATE support_ticket 
        SET status = 'fechado', updated_at = datetime('now')
        WHERE id = ?
    """).bind(ticket_id).run()


# ============================================================================
# QUERIES - DIVULGAÇÃO/PROMOÇÕES
# ============================================================================

async def create_divulgacao(db, area, titulo, texto=None, link=None, imagem=None, 
                            show_on_edu=True, show_on_index=True, author_id=None):
    """Cria uma divulgação."""
    # Nota: A tabela divulgacao não tem coluna author_id diretamente, 
    # mas podemos vincular via edu_content_id ou post_id se necessário
    result = await db.prepare("""
        INSERT INTO divulgacao (area, titulo, texto, link, imagem, show_on_edu, show_on_index)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        RETURNING id
    """).bind(area, titulo, texto, link, imagem, 
              1 if show_on_edu else 0, 1 if show_on_index else 0).first()
    return result['id'] if result else None


async def update_divulgacao(db, divulgacao_id, titulo=None, texto=None, link=None, 
                            imagem=None, ativo=None, ordem=None, 
                            show_on_edu=None, show_on_index=None):
    """Atualiza uma divulgação com parâmetros explícitos (evita SQL injection)."""
    # Construir updates de forma segura
    updates = []
    values = []
    
    if titulo is not None:
        updates.append("titulo = ?")
        values.append(titulo)
    if texto is not None:
        updates.append("texto = ?")
        values.append(texto)
    if link is not None:
        updates.append("link = ?")
        values.append(link)
    if imagem is not None:
        updates.append("imagem = ?")
        values.append(imagem)
    if ativo is not None:
        updates.append("ativo = ?")
        values.append(1 if ativo else 0)
    if ordem is not None:
        updates.append("ordem = ?")
        values.append(ordem)
    if show_on_edu is not None:
        updates.append("show_on_edu = ?")
        values.append(1 if show_on_edu else 0)
    if show_on_index is not None:
        updates.append("show_on_index = ?")
        values.append(1 if show_on_index else 0)
    
    if not updates:
        return False
    
    updates.append("updated_at = datetime('now')")
    values.append(divulgacao_id)
    
    set_clause = ", ".join(updates)
    
    await db.prepare(f"""
        UPDATE divulgacao SET {set_clause}
        WHERE id = ?
    """).bind(*values).run()
    return True


async def delete_divulgacao(db, divulgacao_id):
    """Remove uma divulgação."""
    await db.prepare("""
        DELETE FROM divulgacao WHERE id = ?
    """).bind(divulgacao_id).run()


# ============================================================================
# QUERIES - UPLOAD DE IMAGENS
# ============================================================================

async def save_upload(db, usuario_id, tipo, path, filename=None, content_type=None, size=None):
    """Registra um upload de imagem."""
    result = await db.prepare("""
        INSERT INTO upload (usuario_id, tipo, path, filename, content_type, size)
        VALUES (?, ?, ?, ?, ?, ?)
        RETURNING id
    """).bind(usuario_id, tipo, path, filename, content_type, size).first()
    return result['id'] if result else None


async def get_user_uploads(db, usuario_id, tipo=None):
    """Lista uploads de usuárie."""
    if tipo:
        result = await db.prepare("""
            SELECT * FROM upload
            WHERE usuario_id = ? AND tipo = ?
            ORDER BY created_at DESC
        """).bind(usuario_id, tipo).all()
    else:
        result = await db.prepare("""
            SELECT * FROM upload
            WHERE usuario_id = ?
            ORDER BY created_at DESC
        """).bind(usuario_id).all()
    
    return [dict(row) for row in result.results] if result.results else []


# ============================================================================
# QUERIES - ADMIN
# ============================================================================

async def get_all_usuaries(db, page=1, per_page=20, search=None):
    """Lista todes usuáries (para admin)."""
    offset = (page - 1) * per_page
    
    if search:
        search_term = f"%{search}%"
        result = await db.prepare("""
            SELECT id, username, nome, email, foto_perfil, is_admin, is_superadmin, 
                   is_banned, created_at, email_confirmed
            FROM user
            WHERE username LIKE ? OR nome LIKE ? OR email LIKE ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """).bind(search_term, search_term, search_term, per_page, offset).all()
    else:
        result = await db.prepare("""
            SELECT id, username, nome, email, foto_perfil, is_admin, is_superadmin, 
                   is_banned, created_at, email_confirmed
            FROM user
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """).bind(per_page, offset).all()
    
    return [dict(row) for row in result.results] if result.results else []


async def ban_usuarie(db, usuario_id, reason=None, admin_id=None):
    """Bane usuárie."""
    await db.prepare("""
        UPDATE user SET is_banned = 1, banned_at = datetime('now'), ban_reason = ?
        WHERE id = ?
    """).bind(reason, usuario_id).run()


async def unban_usuarie(db, usuario_id):
    """Remove ban de usuárie."""
    await db.prepare("""
        UPDATE user SET is_banned = 0, banned_at = NULL, ban_reason = NULL
        WHERE id = ?
    """).bind(usuario_id).run()


async def suspend_usuarie(db, usuario_id, until_date):
    """Suspende usuárie temporariamente."""
    await db.prepare("""
        UPDATE user SET suspended_until = ?
        WHERE id = ?
    """).bind(until_date, usuario_id).run()


async def make_admin(db, usuario_id, is_admin=True):
    """Torna usuárie admin ou remove permissão."""
    await db.prepare("""
        UPDATE user SET is_admin = ?
        WHERE id = ?
    """).bind(1 if is_admin else 0, usuario_id).run()


async def get_admin_stats(db):
    """Estatísticas para painel admin."""
    stats = {}
    
    # Total de usuáries
    result = await db.prepare("SELECT COUNT(*) as count FROM user").first()
    stats['total_usuaries'] = result['count'] if result else 0
    
    # Usuáries ativos (últimos 7 dias)
    result = await db.prepare("""
        SELECT COUNT(DISTINCT user_id) as count FROM user_session
        WHERE created_at > datetime('now', '-7 days')
    """).first()
    stats['usuaries_ativos'] = result['count'] if result else 0
    
    # Total de posts
    result = await db.prepare("SELECT COUNT(*) as count FROM post WHERE is_deleted = 0").first()
    stats['total_posts'] = result['count'] if result else 0
    
    # Denúncias pendentes
    stats['denuncias_pendentes'] = await count_pending_reports(db)
    
    # Tickets abertos
    result = await db.prepare("SELECT COUNT(*) as count FROM support_ticket WHERE status = 'aberto'").first()
    stats['tickets_abertos'] = result['count'] if result else 0
    
    return stats
