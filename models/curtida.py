"""Curtida: responsável Enzo."""
from datetime import datetime

from extensoes import db


class Curtida(db.Model):
    __tablename__ = "curtida"
    __table_args__ = (db.UniqueConstraint("post_id", "usuario_id", name="uq_curtida_post_usuario"),)

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

    # TODO (Enzo): curtir(), descurtir(), usuario_curtiu(), contar_por_post(), contar_por_autor()
