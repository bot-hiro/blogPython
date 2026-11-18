"""Post: responsável Ian."""
from datetime import datetime

from extensoes import db


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

    # TODO (Ian): criar(), editar(), publicar(), arquivar(), excluir(),
    #             registrar_visualizacao(), adicionar_tag(), remover_tag(), engajamento()
