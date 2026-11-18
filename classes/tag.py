"""Modelo e operações de tags do blog."""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import validates

from extensions import db


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

        from models import Post

        consulta = Post.query.join(post_tag, Post.id == post_tag.c.post_id)
        return consulta.filter(post_tag.c.tag_id == tag_id).order_by(
            Post.data_publicacao.desc(), Post.id.desc()
        ).all()
