"""Curtida: responsável Enzo."""
from datetime import datetime

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from extensoes import db


class Curtida(db.Model):
    __tablename__ = "curtida"
    __table_args__ = (db.UniqueConstraint("post_id", "usuario_id", name="uq_curtida_post_usuario"),)

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

    @classmethod
    def curtir(cls, usuario_id, post_id):
        """Cria uma curtida ou devolve a que já existe para o par."""
        from models.post import Post
        from models.usuario import Usuario

        if type(usuario_id) is not int or db.session.get(Usuario, usuario_id) is None:
            raise ValueError("Usuário não encontrado.")
        if type(post_id) is not int or db.session.get(Post, post_id) is None:
            raise ValueError("Publicação não encontrada.")

        consulta = cls.query.filter_by(usuario_id=usuario_id, post_id=post_id)
        existente = consulta.first()
        if existente is not None:
            return existente

        curtida = cls(usuario_id=usuario_id, post_id=post_id)
        db.session.add(curtida)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            existente = consulta.first()
            if existente is not None:
                return existente
            raise
        except SQLAlchemyError:
            db.session.rollback()
            raise
        return curtida

    @classmethod
    def descurtir(cls, usuario_id, post_id):
        """Remove a curtida e indica se havia uma para remover."""
        try:
            removidas = cls.query.filter_by(usuario_id=usuario_id, post_id=post_id).delete()
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise
        return removidas > 0

    @classmethod
    def usuario_curtiu(cls, usuario_id, post_id):
        return cls.query.filter_by(usuario_id=usuario_id, post_id=post_id).first() is not None

    @classmethod
    def contar_por_post(cls, post_id):
        return cls.query.filter_by(post_id=post_id).count()

    @classmethod
    def contar_por_autor(cls, autor_id):
        """Conta as curtidas recebidas pelos posts do autor."""
        from models.post import Post

        return cls.query.join(Post, cls.post_id == Post.id).filter(Post.autor_id == autor_id).count()
