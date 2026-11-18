"""Avaliacao: responsável Enzo."""
from datetime import datetime

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

    # TODO (Enzo): avaliar(nota), alterar_nota(nota), media_por_post(), distribuicao_notas()
