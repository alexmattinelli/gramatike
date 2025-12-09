from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import request, jsonify
from flask_login import login_required, current_user
from flask import Flask

app = Flask(__name__)

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    # Verificação de e-mail
    email_confirmed = db.Column(db.Boolean, default=False)
    email_confirmed_at = db.Column(db.DateTime)
    foto_perfil = db.Column(db.String(255), default='img/perfil.png')
    genero = db.Column(db.String(50))
    pronome = db.Column(db.String(50))
    bio = db.Column(db.Text)
    data_nascimento = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_admin = db.Column(db.Boolean, default=False)
    # Superadmin: não pode ser removide, nem ter admin retirado
    is_superadmin = db.Column(db.Boolean, default=False)
    # Moderação
    is_banned = db.Column(db.Boolean, default=False)
    banned_at = db.Column(db.DateTime)
    ban_reason = db.Column(db.Text)
    suspended_until = db.Column(db.DateTime)

    def __repr__(self):
        return f'<User {self.username}>'

    # Segurança: armazenamento de senha com hash (PBKDF2 por padrão do Werkzeug)
    def set_password(self, raw_password: str):
        if not raw_password:
            raise ValueError('Senha vazia não permitida')
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        try:
            return check_password_hash(self.password or '', raw_password or '')
        except Exception:
            return False

class Estudo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    # Você pode adicionar mais campos, como data, autor, etc.

# --- Novo modelo unificado de conteúdo educacional ---
class EduContent(db.Model):
    """Conteúdos diversos do Gramátike Edu.
    tipo: 'artigo' | 'apostila' | 'podcast' | 'exercicio' | 'redacao_tema' | 'variacao'
    Para podcasts usar campo url; para apostilas futuramente file_path (upload) / url; para variação linguística usar corpo/extra.
    Exercícios complexos ficam em ExerciseTopic / ExerciseQuestion; aqui guardamos só metadados caso necessário.
    """
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(40), index=True, nullable=False)
    titulo = db.Column(db.String(220), nullable=False)
    resumo = db.Column(db.Text)  # unlimited text for summaries
    corpo = db.Column(db.Text)  # texto principal (artigos, apostilas resumo, variação, tema redação)
    url = db.Column(db.String(500))  # link externo (podcast spotify, pdf remoto, etc.)
    file_path = db.Column(db.String(500))  # reservado para upload de PDFs futuramente
    extra = db.Column(db.Text)  # JSON serializado simples para metadados
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User')
    topic_id = db.Column(db.Integer, db.ForeignKey('edu_topic.id'))

    topic = db.relationship('EduTopic', backref=db.backref('contents', lazy='dynamic'))

    def __repr__(self):
        return f'<EduContent {self.tipo}:{self.titulo}>'

class ExerciseTopic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<ExerciseTopic {self.nome}>'

class ExerciseSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('exercise_topic.id'), index=True, nullable=False)
    nome = db.Column(db.String(180), nullable=False)
    descricao = db.Column(db.Text)
    ordem = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    topic = db.relationship('ExerciseTopic', backref=db.backref('sections', lazy='dynamic', order_by='ExerciseSection.ordem.asc()'))
    __table_args__ = (db.UniqueConstraint('topic_id','nome', name='uix_topic_section_nome'),)
    def __repr__(self):
        return f'<ExerciseSection {self.topic_id}:{self.nome}>'

# Novo modelo de tópicos gerais para áreas (Artigos, Apostilas, Exercicios, Podcasts, Redação)
class EduTopic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(40), index=True, nullable=False)  # artigo, apostila, exercicio, podcast, redacao
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    __table_args__ = (db.UniqueConstraint('area','nome', name='uix_area_nome'),)

    def __repr__(self):
        return f'<EduTopic {self.area}:{self.nome}>'

class ExerciseQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('exercise_topic.id'), index=True, nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('exercise_section.id'), index=True)
    enunciado = db.Column(db.Text, nullable=False)
    resposta = db.Column(db.Text)  # pode ser texto ou JSON (alternativas) futuramente
    dificuldade = db.Column(db.String(30))
    # Novo: tipo do exercício (multipla_escolha, arrastar_palavras, discursiva, etc.)
    tipo = db.Column(db.String(40), index=True)
    # Novo: opções ou metadados em JSON simples (armazenado como texto)
    opcoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    topic = db.relationship('ExerciseTopic', backref=db.backref('questions', lazy='dynamic'))
    section = db.relationship('ExerciseSection', backref=db.backref('questions', lazy='dynamic'))
    def __repr__(self):
        return f'<ExerciseQuestion {self.id}>'

post_likes = db.Table('post_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuarie = db.Column(db.String(80))
    usuarie_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Novo campo: id do usuário
    conteudo = db.Column(db.Text)
    imagem = db.Column(db.Text)
    data = db.Column(db.DateTime)
    likes = db.relationship('User', secondary=post_likes, backref='liked_posts')
    # Soft delete
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.Integer, db.ForeignKey('user.id'))

# Removido: PostDelu (legado)

class OutroRecurso(db.Model):
    # Vai para app.db (não precisa de __bind_key__)
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80))

class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuarie_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    usuarie = db.relationship('User')
    conteudo = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    data = db.Column(db.DateTime, default=datetime.utcnow)
    # ... outros campos ...

class Curtida(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuarie_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    usuarie = db.relationship('User')


# Modelo de seguidories (seguindo/seguidories)
seguidories = db.Table('seguidories',
    db.Column('seguidore_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('seguide_id', db.Integer, db.ForeignKey('user.id'))
)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    usuarie_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    motivo = db.Column(db.Text)
    category = db.Column(db.String(40))  # ex.: odio, violencia, assedio, nudez, spam, suicidio, outro
    data = db.Column(db.DateTime, default=datetime.utcnow)
    post = db.relationship('Post')
    usuarie = db.relationship('User')
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime)

class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuarie_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    nome = db.Column(db.String(150))
    email = db.Column(db.String(180))
    mensagem = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='aberto', index=True)  # aberto, em_andamento, resolvido
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime)
    usuarie = db.relationship('User')
    resposta = db.Column(db.Text)

# Adicionar métodos de seguidories ao User
User.seguindo = db.relationship(
    'User', secondary=seguidories,
    primaryjoin=(seguidories.c.seguidore_id == User.id),
    secondaryjoin=(seguidories.c.seguide_id == User.id),
    backref=db.backref('seguidories', lazy='dynamic'),
    lazy='dynamic'
)

# Removidos: modelos LuneMessage, LuneMemory, LuneKnowledge, LuneFeedback


# Divulgação / Promoções (cards de destaque com imagem ou vídeo curto)
class Promotion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(180), nullable=False)
    descricao = db.Column(db.String(400))  # texto curto chamativo
    media_type = db.Column(db.String(20), nullable=False, default='image')  # image | video | embed
    media_path = db.Column(db.String(500))  # caminho do arquivo estático (upload) ou URL
    link_destino = db.Column(db.String(600))  # para onde leva ao clicar
    ativo = db.Column(db.Boolean, default=True, index=True)
    ordem = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    author = db.relationship('User', foreign_keys=[author_id])

    def __repr__(self):
        return f"<Promotion {self.titulo} #{self.id}>"

# Novidades simples (hub Gramátike) - persistência leve
class EduNovidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.String(500))
    link = db.Column(db.String(600))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    author = db.relationship('User')

    def __repr__(self):
        return f"<EduNovidade {self.titulo[:25]}>"

# Feedback de respostas do Lune (sinalização + comentário opcional)

# Conteúdos de divulgação (curadoria manual para homepage)
class Divulgacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(20), index=True, nullable=False)  # 'edu', 'delu', 'geral'
    titulo = db.Column(db.String(180), nullable=False)
    texto = db.Column(db.Text)  # preview/descrição
    link = db.Column(db.String(400))  # URL destino
    imagem = db.Column(db.String(400))  # caminho em /static ou URL completa
    ordem = db.Column(db.Integer, default=0, index=True)
    ativo = db.Column(db.Boolean, default=True, index=True)
    # Novos destinos: controle fino de onde exibir os cards
    show_on_edu = db.Column(db.Boolean, default=True, index=True)
    show_on_index = db.Column(db.Boolean, default=True, index=True)
    # removido: show_on_lune
    edu_content_id = db.Column(db.Integer, db.ForeignKey('edu_content.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    edu_content = db.relationship('EduContent', lazy='joined')
    post = db.relationship('Post', lazy='joined')

    def __repr__(self):
        return f"<Divulgacao {self.area}:{self.titulo[:18]}>"

# Imagens de posts (normalização futura)
class PostImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), index=True, nullable=False)
    path = db.Column(db.String(400), nullable=False)
    ordem = db.Column(db.Integer, default=0, index=True)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)

# Dinâmicas (enquetes, formulários simples, palavra única)
class Dynamic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), index=True, nullable=False)  # 'poll' | 'form' | 'oneword'
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.String(500))
    config = db.Column(db.Text)  # JSON com opções/campos
    active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    author = db.relationship('User')

    def __repr__(self):
        return f"<Dynamic {self.tipo}:{self.titulo[:20]}>"

class DynamicResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dynamic_id = db.Column(db.Integer, db.ForeignKey('dynamic.id'), index=True, nullable=False)
    usuarie_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    payload = db.Column(db.Text)  # JSON com voto/entrada
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    dynamic = db.relationship('Dynamic', backref=db.backref('responses', lazy='dynamic'))
    usuarie = db.relationship('User')
    def __repr__(self):
        return f"<DynamicResponse dyn={self.dynamic_id} user={self.usuario_id}>"

# Palavras para evitar na nuvem de palavras (oneword dynamics)
class WordExclusion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dynamic_id = db.Column(db.Integer, db.ForeignKey('dynamic.id'), index=True, nullable=False)
    usuarie_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
    palavra = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    dynamic = db.relationship('Dynamic')
    usuarie = db.relationship('User')
    
    def __repr__(self):
        return f"<WordExclusion dyn={self.dynamic_id} user={self.usuario_id} palavra={self.palavra}>"


# Palavras bloqueadas customizadas (gerenciadas no painel de admin)
class BlockedWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(200), unique=True, nullable=False)
    category = db.Column(db.String(20), default='custom', index=True)  # 'profanity' | 'hate' | 'nudity' | 'custom'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    author = db.relationship('User')

    def __repr__(self):
        return f"<BlockedWord {self.term} ({self.category})>"

# Palavras do Dia (feature educacional inclusiva)
class PalavraDoDia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    palavra = db.Column(db.String(200), nullable=False)
    significado = db.Column(db.Text, nullable=False)  # Explicação curta e inclusiva
    ordem = db.Column(db.Integer, default=0, index=True)  # Para rotação diária
    ativo = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    author = db.relationship('User')

    def __repr__(self):
        return f"<PalavraDoDia {self.palavra}>"

class PalavraDoDiaInteracao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    palavra_id = db.Column(db.Integer, db.ForeignKey('palavra_do_dia.id'), index=True, nullable=False)
    usuarie_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'frase' | 'significado'
    frase = db.Column(db.Text)  # Preenchido apenas se tipo='frase'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    palavra = db.relationship('PalavraDoDia', backref=db.backref('interacoes', lazy='dynamic'))
    usuarie = db.relationship('User')

    def __repr__(self):
        return f"<PalavraDoDiaInteracao palavra={self.palavra_id} user={self.usuario_id} tipo={self.tipo}>"

