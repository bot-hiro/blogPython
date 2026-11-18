"""Categoria: responsável Ian."""
from extensoes import db


class Categoria(db.Model):
    __tablename__ = "categoria"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), unique=True, nullable=False)
    slug = db.Column(db.String(60), unique=True, nullable=False)
    descricao = db.Column(db.String(200))
    cor = db.Column(db.String(20))

    posts = db.relationship("Post", back_populates="categoria")

    # TODO (Ian): criar(), editar(), excluir(), total_posts(), percentual_do_blog()
