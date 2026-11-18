"""Post: responsável Ian."""
import re
import unicodedata
from datetime import datetime

from extensoes import db


def gerar_slug(texto):
    """'Olá, Mundo!' vira 'ola-mundo' (usado no endereço do post)."""
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-").lower()
    return texto or "post"


class Post(db.Model):
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(160), unique=True, nullable=False)
    resumo = db.Column(db.String(300))
    conteudo = db.Column(db.Text, nullable=False)
    imagem_capa = db.Column(db.String(200))
    status = db.Column(db.String(12), nullable=False, default="RASCUNHO")  # RASCUNHO, PUBLICADO, ARQUIVADO
    visualizacoes = db.Column(db.Integer, default=0)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_publicacao = db.Column(db.DateTime)  # só preenchida ao publicar
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow)
    autor_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"), nullable=False)

    autor = db.relationship("Usuario", back_populates="posts")
    categoria = db.relationship("Categoria", back_populates="posts")

    # ---------- métodos do Ian ----------
    @classmethod
    def criar(cls, titulo, resumo, conteudo, autor_id, categoria_id, imagem_capa=None):
        """Cria um post como RASCUNHO e devolve o post."""
        base = gerar_slug(titulo)
        slug, n = base, 2
        while cls.query.filter_by(slug=slug).first():  # slug precisa ser único
            slug = f"{base}-{n}"
            n += 1
        post = cls(
            titulo=titulo, slug=slug, resumo=resumo, conteudo=conteudo,
            imagem_capa=imagem_capa, autor_id=autor_id, categoria_id=categoria_id,
        )
        db.session.add(post)
        db.session.commit()
        return post

    def publicar(self):
        """Muda para PUBLICADO e preenche a data de publicação (só na primeira vez)."""
        self.status = "PUBLICADO"
        if self.data_publicacao is None:
            self.data_publicacao = datetime.utcnow()
        db.session.commit()

    def registrar_visualizacao(self):
        """Cada abertura do detalhe soma 1."""
        self.visualizacoes = (self.visualizacoes or 0) + 1
        db.session.commit()

    def tempo_leitura(self):
        """Minutos de leitura: número de palavras / 200 (mínimo 1)."""
        palavras = len(self.conteudo.split())
        return max(1, round(palavras / 200))

    # Estes três devolvem valores provisórios. Enzo e Amanda: quando a sua
    # classe estiver pronta, troquem o "return" pela contagem real.
    def total_curtidas(self):
        return 0  # TODO (Enzo): usar Curtida.contar_por_post()

    def total_comentarios(self):
        return 0  # TODO (Amanda): só comentários APROVADOS

    def media_avaliacoes(self):
        return None  # TODO (Enzo): usar Avaliacao.media_por_post()

    # TODO (Ian): editar(), arquivar(), excluir(), adicionar_tag(), remover_tag(), engajamento()
