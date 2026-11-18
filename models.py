"""Classes do blog. Cada classe vira uma tabela no banco (SQLite).

Os nomes seguem o diagrama de classes (UML) do grupo.
Quem for implementar uma classe nova: copie o estilo de Categoria/Post
e procure os comentários TODO.
"""
from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class Categoria(db.Model):
    __tablename__ = "categoria"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), unique=True, nullable=False)
    slug = db.Column(db.String(60), unique=True, nullable=False)
    descricao = db.Column(db.String(200))
    cor = db.Column(db.String(20))

    posts = db.relationship("Post", back_populates="categoria")

    # TODO: criar(), editar(), excluir(), total_posts(), percentual_do_blog()


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(10), nullable=False, default="LEITOR")  # ADMIN, AUTOR ou LEITOR
    bio = db.Column(db.String(300))
    foto = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship("Post", back_populates="autor")

    def definir_senha(self, senha):
        """Guarda a senha criptografada (nunca a senha pura)."""
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    # TODO: autentica(), cadastrar(), alterar_senha(), promover(), desativar(), totais


class Post(db.Model):
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(160), unique=True, nullable=False)
    resumo = db.Column(db.String(300))
    conteudo = db.Column(db.Text, nullable=False)
    imagem_capa = db.Column(db.String(200))
    status = db.Column(db.String(12), nullable=False, default="RASCUNHO")  # RASCUNHO, PUBLICADO, ARQUIVADO
    visualizacoes = db.Column(db.Integer, default=0)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_publicacao = db.Column(db.DateTime)  # só preenchida ao publicar
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow)
    autor_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)

    autor = db.relationship("Usuario", back_populates="posts")
    categoria = db.relationship("Categoria", back_populates="posts")

    def tempo_leitura(self):
        """Minutos de leitura: número de palavras / 200 (mínimo 1)."""
        palavras = len(self.conteudo.split())
        return max(1, round(palavras / 200))

    # Por enquanto devolvem zero. Quando as classes Curtida, Comentario e
    # Avaliacao existirem, é só trocar o "return 0" pela contagem real.
    def total_curtidas(self):
        return 0  # TODO

    def total_comentarios(self):
        return 0  # TODO (só comentários APROVADOS)

    def media_avaliacoes(self):
        return None  # TODO

    # TODO: criar(), editar(), publicar(), arquivar(), excluir(),
    #       registrar_visualizacao(), engajamento()
