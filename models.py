"""Classes do blog. Cada classe vira uma tabela no banco (SQLite).

Os nomes seguem o diagrama de classes (UML) do grupo.
Quem for implementar uma classe nova: copie o estilo de Categoria/Post
e procure os comentários TODO.
"""
from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import validates
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


class Tag(db.Model):
    __tablename__ = "tag"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), unique=True, nullable=False)

    @validates("nome")
    def _validar_nome(self, _campo, nome):
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("Informe o nome da tag.")
        nome = nome.strip()
        if len(nome) > 60:
            raise ValueError("O nome da tag deve ter no máximo 60 caracteres.")
        return nome

    @staticmethod
    def _confirmar_alteracoes():
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def criar_tag(cls, nome):
        """Cria e devolve a tag cadastrada."""
        tag = cls(nome=nome)
        db.session.add(tag)
        cls._confirmar_alteracoes()
        return tag

    @classmethod
    def listar_tags(cls):
        """Devolve as tags em ordem de nome."""
        return cls.query.order_by(cls.nome).all()

    @classmethod
    def atualizar_tag(cls, tag_id, nome):
        """Altera o nome e devolve a tag, ou None se ela não existir."""
        tag = db.session.get(cls, tag_id)
        if tag is not None:
            tag.nome = nome
            cls._confirmar_alteracoes()
        return tag

    @classmethod
    def excluir_tag(cls, tag_id):
        """Exclui a tag e seus vínculos. Devolve False se ela não existir."""
        tag = db.session.get(cls, tag_id)
        if tag is None:
            return False

        post_tag = db.metadata.tables.get("post_tag")
        try:
            if post_tag is not None:
                db.session.execute(post_tag.delete().where(post_tag.c.tag_id == tag_id))
            db.session.delete(tag)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise
        return True

    @staticmethod
    def listar_posts_por_tag(tag_id):
        """Devolve os posts associados pela tabela post_tag."""
        post_tag = db.metadata.tables.get("post_tag")
        if post_tag is None:
            raise RuntimeError("A consulta por tag depende da tabela post_tag.")

        consulta = Post.query.join(post_tag, Post.id == post_tag.c.post_id)
        return consulta.filter(post_tag.c.tag_id == tag_id).order_by(
            Post.data_publicacao.desc(), Post.id.desc()
        ).all()
