"""Tag: responsável Enzo."""
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import validates

from extensoes import db
from models.post import gerar_slug
from models.post_tag import Post_Tag


class Tag(db.Model):
    __tablename__ = "tag"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), unique=True, nullable=False)
    slug = db.Column(db.String(40), unique=True, nullable=False)

    @validates("nome")
    def _validar_nome(self, _campo, nome):
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError("Informe o nome da tag.")
        nome = nome.strip()
        if len(nome) > 40:
            raise ValueError("O nome da tag deve ter no máximo 40 caracteres.")
        return nome

    @staticmethod
    def _confirmar_alteracoes():
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise

    @classmethod
    def criar(cls, nome):
        """Cria uma tag com slug derivado do nome."""
        tag = cls(nome=nome)
        base = gerar_slug(tag.nome)[:40].rstrip("-")
        slug, numero = base, 2
        while cls.query.filter_by(slug=slug).first():
            sufixo = f"-{numero}"
            slug = f"{base[:40 - len(sufixo)].rstrip('-')}{sufixo}"
            numero += 1
        tag.slug = slug
        db.session.add(tag)
        cls._confirmar_alteracoes()
        return tag

    def editar(self, nome):
        """Renomeia a tag, preservando o endereço já publicado."""
        self.nome = nome
        self._confirmar_alteracoes()
        return self

    def excluir(self):
        """Exclui a tag e seus vínculos em uma única transação."""
        try:
            db.session.execute(db.delete(Post_Tag).where(Post_Tag.tag_id == self.id))
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def total_posts(self):
        """Conta os vínculos com posts, de qualquer status."""
        consulta = db.select(db.func.count()).select_from(Post_Tag).where(Post_Tag.tag_id == self.id)
        return db.session.scalar(consulta)

    @classmethod
    def ranking_tags_mais_usadas(cls):
        """Devolve pares de tag e contagem, incluindo tags sem vínculos."""
        total = db.func.count(Post_Tag.post_id)
        consulta = (
            db.select(cls, total)
            .outerjoin(Post_Tag, Post_Tag.tag_id == cls.id)
            .group_by(cls.id)
            .order_by(total.desc(), cls.nome)
        )
        return db.session.execute(consulta).all()
