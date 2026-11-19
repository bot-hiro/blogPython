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

    # Relacionamentos
    post = db.relationship("Post", back_populates="comentarios")
    usuario = db.relationship("Usuario", back_populates="comentarios")
    respostas = db.relationship("Comentario", backref="pai", remote_side=[id])
    

    def comentar(self):
        """Todo comentário novo entra como PENDENTE (regra 2 do documento)."""
        self.status = "PENDENTE"
        db.session.add(self)
        db.session.commit()
        return self

    def responder(self, texto):
        """Cria uma resposta a este comentário."""
        nova_resposta = Comentario(
            texto=texto,
            status="PENDENTE",
            post_id=self.post_id,
            usuario_id=self.usuario_id,
            comentario_pai_id=self.id
        )
        db.session.add(nova_resposta)
        db.session.commit()
        return nova_resposta

    def aprovar(self):
        """Admin aprova: comentário fica visível ao público."""
        self.status = "APROVADO"
        db.session.commit()

    def rejeitar(self):
        """Admin rejeita: comentário não aparece."""
        self.status = "REJEITADO"
        db.session.commit()

    def excluir(self):
        """Remove o comentário e suas respostas."""
        db.session.delete(self)
        db.session.commit()

    def total_respostas(self):
        """Quantas respostas este comentário recebeu (aparece no Detalhe do Post)."""
        return Comentario.query.filter_by(comentario_pai_id=self.id).count()