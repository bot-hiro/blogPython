"""Dashboard (estatísticas): responsável Enzo."""

from extensoes import db
from models.avaliacao import Avaliacao
from models.categoria import Categoria
from models.post import Post
from models.usuario import Usuario


def _consulta_posts_por_categoria():
    total = db.func.count(Post.id).label("total")
    return (
        db.session.query(Categoria.nome, total)
        .join(Post, Post.categoria_id == Categoria.id)
        .filter(Post.status == "PUBLICADO")
        .group_by(Categoria.id, Categoria.nome)
        .order_by(total.desc(), Categoria.nome)
    )


class Dashboard:
    @staticmethod
    def gerar_resumo():
        """Reúne os indicadores e a distribuição de posts publicados."""
        publicados, visualizacoes = (
            db.session.query(db.func.count(Post.id), db.func.coalesce(db.func.sum(Post.visualizacoes), 0))
            .filter(Post.status == "PUBLICADO")
            .one()
        )
        media_avaliacoes = (
            db.session.query(db.func.avg(Avaliacao.nota))
            .join(Post, Avaliacao.post_id == Post.id)
            .filter(Post.status == "PUBLICADO")
            .scalar()
        )
        return {
            "posts_publicados": publicados,
            "visualizacoes": visualizacoes,
            "media_avaliacoes": media_avaliacoes,
            "engajamento_medio": None,
            "posts_por_categoria": _consulta_posts_por_categoria().all(),
        }

    @staticmethod
    def posts_por_mes():
        """Lista a quantidade de publicações por mês em ordem cronológica."""
        mes = db.func.strftime("%Y-%m", Post.data_publicacao).label("mes")
        return (
            db.session.query(mes, db.func.count(Post.id).label("total"))
            .filter(Post.status == "PUBLICADO", Post.data_publicacao.isnot(None))
            .group_by(mes)
            .order_by(mes)
            .all()
        )

    @staticmethod
    def top_5_posts_por_engajamento():
        """Retorna None enquanto o cálculo de Post.engajamento estiver pendente."""
        # Proposta para alinhar com Ian: 100 × (curtidas + comentários aprovados +
        # avaliações) / visualizações. Posts sem visualizações não teriam taxa.
        return None

    @staticmethod
    def autor_mais_lido():
        """Devolve o autor com mais visualizações em posts publicados, se houver."""
        visualizacoes = db.func.sum(Post.visualizacoes).label("visualizacoes")
        return (
            db.session.query(Usuario.nome, visualizacoes)
            .join(Post, Post.autor_id == Usuario.id)
            .filter(Post.status == "PUBLICADO")
            .group_by(Usuario.id, Usuario.nome)
            .having(visualizacoes > 0)
            .order_by(visualizacoes.desc(), Usuario.nome, Usuario.id)
            .first()
        )

    @staticmethod
    def categoria_mais_popular():
        """Devolve a categoria com mais posts publicados, se houver."""
        return _consulta_posts_por_categoria().first()
