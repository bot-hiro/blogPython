"""Comentario: responsável Amanda."""
from datetime import datetime

from extensoes import db


class Comentario(db.Model):
    __tablename__ = "comentario"

    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(10), nullable=False, default="PENDENTE")  # PENDENTE, APROVADO, REJEITADO
    data = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    comentario_pai_id = db.Column(db.Integer, db.ForeignKey("comentario.id"))  # opcional (resposta)

    # TODO (Amanda): comentar(), responder(texto), aprovar(), rejeitar(), excluir(), total_respostas()
