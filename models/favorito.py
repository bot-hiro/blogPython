"""Favorito: responsável Amanda."""
from datetime import datetime

from extensoes import db


class Favorito(db.Model):
    __tablename__ = "favorito"
    __table_args__ = (db.UniqueConstraint("post_id", "usuario_id", name="uq_favorito_post_usuario"),)

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

    # Relacionamentos: permitem acessar favorito.post e favorito.usuario
    post = db.relationship("Post", back_populates="favoritos")
    usuario = db.relationship("Usuario", back_populates="favoritos")
   

    @classmethod
    def favoritar(cls, post_id, usuario_id):
        """Cria um favorito. Se já existir, devolve None (regra: 1 por usuário/post)."""
        ja_existe = cls.query.filter_by(post_id=post_id, usuario_id=usuario_id).first()
        if ja_existe:
            return None
        novo = cls(post_id=post_id, usuario_id=usuario_id)
        db.session.add(novo)
        db.session.commit()
        return novo

    @classmethod
    def desfavoritar(cls, post_id, usuario_id):
        """Remove o favorito. Devolve True se removeu, False se não existia."""
        favorito = cls.query.filter_by(post_id=post_id, usuario_id=usuario_id).first()
        if not favorito:
            return False
        db.session.delete(favorito)
        db.session.commit()
        return True

    @classmethod
    def total_favoritos_por_post(cls, post_id):
        """Quantos favoritos um post tem (entra no cálculo de engajamento)."""
        return cls.query.filter_by(post_id=post_id).count()