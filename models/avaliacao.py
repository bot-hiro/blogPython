"""Avaliacao: responsável Enzo."""
from datetime import datetime

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import validates

from extensoes import db


class Avaliacao(db.Model):
    __tablename__ = "avaliacao"
    __table_args__ = (
        db.UniqueConstraint("post_id", "usuario_id", name="uq_avaliacao_post_usuario"),
        db.CheckConstraint("nota >= 1 AND nota <= 5", name="ck_avaliacao_nota"),
    )

    id = db.Column(db.Integer, primary_key=True)
    nota = db.Column(db.Integer, nullable=False)  # de 1 a 5
    data = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

    @validates("nota")
    def _validar_nota(self, _campo, nota):
        if type(nota) is not int or not 1 <= nota <= 5:
            raise ValueError("Informe uma nota inteira de 1 a 5.")
        return nota

    @classmethod
    def avaliar(cls, usuario_id, post_id, nota):
        """Registra a primeira avaliação do usuário para a publicação."""
        from models.post import Post
        from models.usuario import Usuario

        avaliacao = cls(usuario_id=usuario_id, post_id=post_id, nota=nota)
        if type(usuario_id) is not int or db.session.get(Usuario, usuario_id) is None:
            raise ValueError("Usuário não encontrado.")
        if type(post_id) is not int or db.session.get(Post, post_id) is None:
            raise ValueError("Publicação não encontrada.")

        db.session.add(avaliacao)
        try:
            db.session.commit()
        except IntegrityError as erro:
            db.session.rollback()
            if cls.query.filter_by(usuario_id=usuario_id, post_id=post_id).first() is not None:
                raise ValueError("O usuário já avaliou esta publicação.") from erro
            raise
        except SQLAlchemyError:
            db.session.rollback()
            raise
        return avaliacao

    def alterar_nota(self, nota):
        """Atualiza a nota da avaliação existente."""
        self.nota = nota
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise
        return self

    @classmethod
    def media_por_post(cls, post_id):
        """Retorna a média das notas ou None se não houver avaliações."""
        return db.session.query(db.func.avg(cls.nota)).filter(cls.post_id == post_id).scalar()

    @classmethod
    def distribuicao_notas(cls, post_id=None):
        """Conta as avaliações de cada nota, para um post ou para o blog."""
        consulta = db.session.query(cls.nota, db.func.count(cls.id)).group_by(cls.nota)
        if post_id is not None:
            consulta = consulta.filter(cls.post_id == post_id)
        contagens = dict(consulta.all())
        return {nota: contagens.get(nota, 0) for nota in range(1, 6)}
