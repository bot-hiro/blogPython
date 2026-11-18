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

    # TODO (Amanda): favoritar(), desfavoritar(), total_favoritos_por_post()
