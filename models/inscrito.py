"""Inscrito (newsletter): responsável Amanda."""
from datetime import datetime

from extensoes import db


class Inscrito(db.Model):
    __tablename__ = "inscrito"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    data_inscricao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))  # opcional

    # TODO (Amanda): inscrever(), cancelar(), total_ativos(), crescimento_por_mes()
