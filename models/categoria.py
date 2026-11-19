"""Categoria: responsável Ian."""
from extensoes import db
from models.post import Post, gerar_slug


class Categoria(db.Model):
    __tablename__ = "categoria"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), unique=True, nullable=False)
    slug = db.Column(db.String(60), unique=True, nullable=False)
    descricao = db.Column(db.String(200))
    cor = db.Column(db.String(20))

    posts = db.relationship("Post", back_populates="categoria")

    @classmethod
    def criar(cls, nome, descricao=None, cor=None):
        base = gerar_slug(nome)
        slug, n = base, 2
        while cls.query.filter_by(slug=slug).first():  # slug precisa ser único
            slug = f"{base}-{n}"
            n += 1
        categoria = cls(nome=nome, slug=slug, descricao=descricao, cor=cor)
        db.session.add(categoria)
        db.session.commit()
        return categoria

    def editar(self, nome, descricao=None, cor=None):
        self.nome = nome
        self.descricao = descricao
        self.cor = cor
        db.session.commit()

    def excluir(self):
        """Regra 5: categoria com posts não pode ser excluída (regra a definir pelo grupo)."""
        if self.posts:
            raise ValueError("Esta categoria tem posts e não pode ser excluída.")
        db.session.delete(self)
        db.session.commit()

    def total_posts(self):
        """Quantidade de posts PUBLICADOS nesta categoria."""
        return Post.query.filter_by(categoria_id=self.id, status="PUBLICADO").count()

    def percentual_do_blog(self):
        """Percentual dos posts publicados do blog que estão nesta categoria."""
        total = Post.query.filter_by(status="PUBLICADO").count()
        return round(100 * self.total_posts() / total, 1) if total else 0.0
