"""Inscrito (newsletter): responsável Amanda."""
from datetime import datetime

from sqlalchemy import func
from extensoes import db


class Inscrito(db.Model):
    __tablename__ = "inscrito"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    data_inscricao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"))  # opcional

    # Relacionamento (opcional, mas útil para saber quem é o usuário, se houver)
    usuario = db.relationship("Usuario", back_populates="inscricoes")

    @classmethod
    def inscrever(cls, email, usuario_id=None):
        """Inscreve um e-mail novo. Se já existir, devolve None."""
        ja_existe = cls.query.filter_by(email=email).first()
        if ja_existe:
            return None
        
        novo = cls(email=email, usuario_id=usuario_id, ativo=True)
        db.session.add(novo)
        db.session.commit()
        return novo

    def cancelar(self):
        """Cancela a inscrição (soft delete: apenas desativa)."""
        self.ativo = False
        db.session.commit()

    @classmethod
    def total_ativos(cls):
        """Quantos inscritos estão ativos."""
        return cls.query.filter_by(ativo=True).count()

    @classmethod
    def crescimento_por_mes(cls):
        """Agrupa a quantidade de inscritos por mês."""
        resultado = (
            db.session.query(
                func.strftime("%Y-%m", cls.data_inscricao).label("mes"),
                func.count(cls.id).label("total")
            )
            .group_by("mes")
            .order_by("mes")
            .all()
        )
        return [{"mes": item.mes, "total": item.total} for item in resultado]