"""Tag: responsável Enzo."""
from extensoes import db


class Tag(db.Model):
    __tablename__ = "tag"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), unique=True, nullable=False)
    slug = db.Column(db.String(40), unique=True, nullable=False)

    # TODO (Enzo): criar(), editar(), excluir(), total_posts(), ranking_tags_mais_usadas()
