import unittest
from datetime import datetime

from flask import Flask
from sqlalchemy.exc import IntegrityError

from extensoes import db
from models import Avaliacao, Categoria, Curtida, Dashboard, Post, Post_Tag, Tag, Usuario


class BancoIsolado(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
        db.init_app(app)
        contexto = app.app_context()
        contexto.push()
        self.addCleanup(db.engine.dispose)
        self.addCleanup(contexto.pop)
        with db.engine.connect() as conexao:
            conexao.exec_driver_sql("PRAGMA foreign_keys = ON")
        db.create_all()

    def persistir(self, objeto):
        db.session.add(objeto)
        db.session.flush()
        return objeto

    def usuario(self, nome):
        return self.persistir(Usuario(nome=nome, email=f"{nome.lower()}@example.com", senha_hash="teste"))

    def categoria(self, nome):
        return self.persistir(Categoria(nome=nome, slug=nome.lower()))

    def post(self, slug, autor, categoria, publicado_em=None, visualizacoes=0, status="PUBLICADO"):
        return self.persistir(
            Post(
                titulo=slug,
                slug=slug,
                conteudo="Conteúdo para teste.",
                autor_id=autor.id,
                categoria_id=categoria.id,
                status=status,
                data_publicacao=publicado_em,
                visualizacoes=visualizacoes,
            )
        )


class TestTag(BancoIsolado):
    def test_slug_unico_com_limite_e_preservado_ao_editar(self):
        tag = Tag.criar("  Ciência de Dados  ")
        outra = Tag.criar("Ciencia de Dados")
        self.assertEqual(tag.nome, "Ciência de Dados")
        self.assertEqual(tag.slug, "ciencia-de-dados")
        self.assertEqual(outra.slug, "ciencia-de-dados-2")

        tag.editar("Dados")
        self.assertEqual((tag.nome, tag.slug), ("Dados", "ciencia-de-dados"))

        longa = Tag.criar("A" * 40)
        longa_com_sufixo = Tag.criar("a" * 40)
        self.assertEqual(longa_com_sufixo.slug, "a" * 38 + "-2")
        self.assertNotEqual(longa_com_sufixo.slug, longa.slug)

    def test_nome_invalido_ou_duplicado_e_rollback(self):
        primeira = Tag.criar("Python")
        segunda = Tag.criar("Flask")
        for nome in ("", "   ", "x" * 41, None):
            with self.subTest(nome=nome), self.assertRaises(ValueError):
                Tag.criar(nome)
        with self.assertRaises(IntegrityError):
            Tag.criar(" Python ")
        with self.assertRaises(IntegrityError):
            segunda.editar("Python")
        self.assertEqual(segunda.nome, "Flask")
        self.assertEqual(primeira.editar("Programação").nome, "Programação")

    def test_contagem_ranking_e_exclusao_preservam_outros_vinculos(self):
        self.assertEqual(db.session.scalar(db.text("PRAGMA foreign_keys")), 1)
        autor, categoria = self.usuario("Autor"), self.categoria("Tecnologia")
        primeiro = self.post("primeiro", autor, categoria)
        segundo = self.post("segundo", autor, categoria, status="RASCUNHO")
        python, web, vazia = Tag.criar("Python"), Tag.criar("Web"), Tag.criar("Vazia")
        db.session.add_all(
            [
                Post_Tag(post_id=primeiro.id, tag_id=python.id),
                Post_Tag(post_id=segundo.id, tag_id=python.id),
                Post_Tag(post_id=primeiro.id, tag_id=web.id),
            ]
        )
        db.session.commit()

        self.assertEqual(python.total_posts(), 2)
        self.assertEqual(vazia.total_posts(), 0)
        self.assertEqual(
            [(tag.nome, total) for tag, total in Tag.ranking_tags_mais_usadas()],
            [("Python", 2), ("Web", 1), ("Vazia", 0)],
        )

        tag_id = python.id
        python.excluir()
        self.assertIsNone(db.session.get(Tag, tag_id))
        self.assertEqual(Post.query.count(), 2)
        self.assertEqual(
            [(vinculo.post_id, vinculo.tag_id) for vinculo in Post_Tag.query.all()],
            [(primeiro.id, web.id)],
        )


class TestCurtida(BancoIsolado):
    def test_curtidas_idempotentes_e_contagem_por_post_e_autor(self):
        ana, bia, caio = self.usuario("Ana"), self.usuario("Bia"), self.usuario("Caio")
        categoria = self.categoria("Tecnologia")
        primeiro = self.post("primeiro", ana, categoria)
        segundo = self.post("segundo", ana, categoria)
        terceiro = self.post("terceiro", bia, categoria)

        self.assertFalse(Curtida.usuario_curtiu(bia.id, primeiro.id))
        curtida = Curtida.curtir(bia.id, primeiro.id)
        self.assertEqual(Curtida.curtir(bia.id, primeiro.id).id, curtida.id)
        Curtida.curtir(caio.id, primeiro.id)
        Curtida.curtir(bia.id, segundo.id)
        Curtida.curtir(ana.id, terceiro.id)
        self.assertTrue(Curtida.usuario_curtiu(bia.id, primeiro.id))
        self.assertEqual(Curtida.contar_por_post(primeiro.id), 2)
        self.assertEqual(Curtida.contar_por_autor(ana.id), 3)
        self.assertEqual(Curtida.contar_por_autor(bia.id), 1)
        self.assertTrue(Curtida.descurtir(bia.id, primeiro.id))
        self.assertFalse(Curtida.descurtir(bia.id, primeiro.id))
        self.assertFalse(Curtida.usuario_curtiu(bia.id, primeiro.id))
        self.assertEqual(Curtida.contar_por_post(primeiro.id), 1)
        self.assertEqual(Curtida.contar_por_autor(ana.id), 2)

    def test_referencias_ausentes(self):
        usuario, categoria = self.usuario("Ana"), self.categoria("Tecnologia")
        post = self.post("teste", usuario, categoria)
        with self.assertRaises(ValueError):
            Curtida.curtir(999, post.id)
        with self.assertRaises(ValueError):
            Curtida.curtir(usuario.id, 999)
        self.assertEqual(Curtida.query.count(), 0)


class TestAvaliacao(BancoIsolado):
    def test_media_distribuicao_e_atualizacao_da_avaliacao_unica(self):
        ana, bia = self.usuario("Ana"), self.usuario("Bia")
        categoria = self.categoria("Tecnologia")
        primeiro = self.post("primeiro", ana, categoria)
        segundo = self.post("segundo", ana, categoria)

        self.assertIsNone(Avaliacao.media_por_post(primeiro.id))
        self.assertEqual(Avaliacao.distribuicao_notas(primeiro.id), dict.fromkeys(range(1, 6), 0))
        avaliacao = Avaliacao.avaliar(ana.id, primeiro.id, 3)
        with self.assertRaises(ValueError):
            Avaliacao.avaliar(ana.id, primeiro.id, 4)
        self.assertIs(avaliacao.alterar_nota(5), avaliacao)
        Avaliacao.avaliar(bia.id, primeiro.id, 2)
        Avaliacao.avaliar(ana.id, segundo.id, 5)

        self.assertEqual(Avaliacao.query.count(), 3)
        self.assertEqual(Avaliacao.media_por_post(primeiro.id), 3.5)
        self.assertEqual(Avaliacao.distribuicao_notas(primeiro.id), {1: 0, 2: 1, 3: 0, 4: 0, 5: 1})
        self.assertEqual(Avaliacao.distribuicao_notas(), {1: 0, 2: 1, 3: 0, 4: 0, 5: 2})

    def test_validacao_da_nota_e_de_referencias(self):
        usuario, categoria = self.usuario("Ana"), self.categoria("Tecnologia")
        post = self.post("teste", usuario, categoria)
        for nota in (0, 6, 1.5, 5.0, True, "5", None):
            with self.subTest(nota=nota), self.assertRaises(ValueError):
                Avaliacao.avaliar(usuario.id, post.id, nota)
        with self.assertRaises(ValueError):
            Avaliacao.avaliar(999, post.id, 4)
        with self.assertRaises(ValueError):
            Avaliacao.avaliar(usuario.id, 999, 4)
        avaliacao = Avaliacao.avaliar(usuario.id, post.id, 1)
        with self.assertRaises(ValueError):
            avaliacao.alterar_nota(0)
        self.assertEqual(avaliacao.nota, 1)


class TestDashboard(BancoIsolado):
    def test_banco_vazio(self):
        resumo = Dashboard.gerar_resumo()
        self.assertEqual(resumo["posts_publicados"], 0)
        self.assertEqual(resumo["visualizacoes"], 0)
        self.assertIsNone(resumo["media_avaliacoes"])
        self.assertIsNone(resumo["engajamento_medio"])
        self.assertEqual(resumo["posts_por_categoria"], [])
        self.assertEqual(Dashboard.posts_por_mes(), [])
        self.assertIsNone(Dashboard.autor_mais_lido())
        self.assertIsNone(Dashboard.categoria_mais_popular())
        self.assertIsNone(Dashboard.top_5_posts_por_engajamento())

    def test_estatisticas_reais_excluem_rascunhos_e_arquivados(self):
        ana, bia = self.usuario("Ana"), self.usuario("Bia")
        ciencia, arte = self.categoria("Ciencia"), self.categoria("Arte")
        janeiro, fevereiro = datetime(2026, 1, 10), datetime(2026, 2, 12)
        primeiro = self.post("primeiro", ana, ciencia, janeiro, 3)
        self.post("segundo", ana, ciencia, fevereiro, 7)
        terceiro = self.post("terceiro", bia, arte, fevereiro, 2)
        rascunho = self.post("rascunho", bia, arte, janeiro, 100, "RASCUNHO")
        arquivado = self.post("arquivado", bia, arte, janeiro, 100, "ARQUIVADO")

        Avaliacao.avaliar(ana.id, primeiro.id, 2)
        Avaliacao.avaliar(bia.id, primeiro.id, 5)
        Avaliacao.avaliar(ana.id, terceiro.id, 5)
        Avaliacao.avaliar(ana.id, rascunho.id, 1)
        Avaliacao.avaliar(bia.id, arquivado.id, 1)

        resumo = Dashboard.gerar_resumo()
        self.assertEqual(resumo["posts_publicados"], 3)
        self.assertEqual(resumo["visualizacoes"], 12)
        self.assertEqual(resumo["media_avaliacoes"], 4.0)
        self.assertEqual(resumo["posts_por_categoria"], [("Ciencia", 2), ("Arte", 1)])
        self.assertEqual(Dashboard.posts_por_mes(), [("2026-01", 1), ("2026-02", 2)])
        self.assertEqual(Dashboard.autor_mais_lido(), ("Ana", 10))
        self.assertEqual(Dashboard.categoria_mais_popular(), ("Ciencia", 2))


if __name__ == "__main__":
    unittest.main()
