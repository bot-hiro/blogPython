import unittest
from datetime import datetime
from pathlib import Path

from flask import Flask

from extensoes import db, login_manager
from models import Avaliacao, Categoria, Curtida, Post, Post_Tag, Tag, Usuario
from rotas import amanda, enzo, ian


class TestRotasEnzo(unittest.TestCase):
    def setUp(self):
        raiz = Path(__file__).resolve().parents[1]
        self.app = Flask(__name__, root_path=str(raiz))
        self.app.config.update(
            TESTING=True, SECRET_KEY="chave-dos-testes", SQLALCHEMY_DATABASE_URI="sqlite://"
        )
        db.init_app(self.app)
        login_manager.init_app(self.app)
        login_manager.login_view = "amanda.login"

        @login_manager.user_loader
        def carregar_usuario(user_id):
            return db.session.get(Usuario, int(user_id))

        self.app.register_blueprint(ian.bp)
        self.app.register_blueprint(amanda.bp)
        self.app.register_blueprint(enzo.bp)
        self.cliente = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            admin = Usuario(nome="Admin", email="admin@example.com", perfil="ADMIN")
            admin.definir_senha("senha")
            leitor = Usuario(nome="Leitor", email="leitor@example.com", perfil="LEITOR")
            leitor.definir_senha("senha")
            categoria = Categoria(nome="Guias", slug="guias")
            publicado = Post(
                titulo="Post para todos", slug="publicado", conteudo="Conteúdo de exemplo",
                categoria=categoria, autor=admin, status="PUBLICADO",
                data_publicacao=datetime(2026, 5, 12), visualizacoes=10,
            )
            rascunho = Post(
                titulo="Post privado", slug="rascunho", conteudo="Conteúdo privado",
                categoria=categoria, autor=admin, status="RASCUNHO", visualizacoes=100,
            )
            db.session.add_all([leitor, publicado, rascunho])
            db.session.commit()
            self.publicado = publicado.id
            self.rascunho = rascunho.id
            self.leitor = leitor.id

    def entrar(self, conta):
        resposta = self.cliente.post("/login", data={"email": f"{conta}@example.com", "senha": "senha"})
        self.assertEqual(resposta.status_code, 302)

    def carregar_token(self, caminho):
        self.assertEqual(self.cliente.get(caminho).status_code, 200)
        with self.cliente.session_transaction() as sessao:
            return sessao["csrf_enzo"]

    def test_acesso_publico_e_links_do_blog(self):
        home = self.cliente.get("/").get_data(as_text=True)
        self.assertIn('href="/tags"', home)
        self.assertIn('href="/post/publicado"', home)
        self.assertIn("Nenhuma tag cadastrada", self.cliente.get("/tags").get_data(as_text=True))
        detalhe = self.cliente.get("/post/publicado").get_data(as_text=True)
        self.assertIn("Entre para curtir e avaliar", detalhe)
        self.assertIn("Sem avaliações", detalhe)
        self.assertEqual(self.cliente.get("/post/rascunho").status_code, 404)
        self.assertEqual(self.cliente.get("/dashboard").status_code, 302)
        self.assertEqual(self.cliente.post("/post/publicado/curtida").status_code, 302)

    def test_admin_cria_edita_lista_e_exclui_tag(self):
        self.entrar("admin")
        token = self.carregar_token("/tags")
        formulario = {"csrf_token": token, "nome": "  Organização  "}
        self.assertEqual(self.cliente.post("/tags", data=formulario).status_code, 303)
        duplicata = self.cliente.post("/tags", data=formulario, follow_redirects=True)
        self.assertIn("Já existe uma tag", duplicata.get_data(as_text=True))
        with self.app.app_context():
            tag = Tag.query.filter_by(nome="Organização").one()
            tag_id = tag.id
            db.session.add_all([
                Post_Tag(tag_id=tag_id, post_id=self.publicado),
                Post_Tag(tag_id=tag_id, post_id=self.rascunho),
            ])
            db.session.commit()

        edicao = self.cliente.post(
            f"/tags/{tag_id}/editar", data={"csrf_token": token, "nome": "Equipe"}, follow_redirects=True
        )
        self.assertIn("Equipe", edicao.get_data(as_text=True))
        listagem = self.cliente.get("/tags/organizacao").get_data(as_text=True)
        self.assertIn("Post para todos", listagem)
        self.assertNotIn("Post privado", listagem)
        exclusao = self.cliente.post(f"/tags/{tag_id}/excluir", data={"csrf_token": token})
        self.assertEqual(exclusao.status_code, 303)
        self.assertEqual(self.cliente.get("/tags/organizacao").status_code, 404)
        self.assertEqual(self.cliente.get("/post/publicado").status_code, 200)
        with self.app.app_context():
            self.assertEqual(Post_Tag.query.filter_by(tag_id=tag_id).count(), 0)
            self.assertEqual(Post.query.count(), 2)

    def test_autorizacao_e_token_dos_formularios(self):
        self.entrar("leitor")
        token = self.carregar_token("/post/publicado")
        self.assertEqual(self.cliente.get("/dashboard").status_code, 403)
        self.assertEqual(self.cliente.post("/tags", data={"csrf_token": token, "nome": "Nova"}).status_code, 403)
        self.assertEqual(self.cliente.post("/post/publicado/curtida", data={"acao": "curtir"}).status_code, 400)
        self.assertEqual(self.cliente.post("/post/publicado/avaliacao", data={"csrf_token": "á", "nota": "5"}).status_code, 400)
        self.assertEqual(self.cliente.post("/post/rascunho/avaliacao", data={"csrf_token": token, "nota": "5"}).status_code, 404)

    def test_curtidas_e_avaliacoes_no_detalhe_e_na_home(self):
        self.entrar("leitor")
        token = self.carregar_token("/post/publicado")
        for _ in range(2):
            resposta = self.cliente.post(
                "/post/publicado/curtida", data={"csrf_token": token, "acao": "curtir"}, follow_redirects=True
            )
            self.assertIn("Descurtir (1)", resposta.get_data(as_text=True))
        for nota in ("5", "3"):
            resposta = self.cliente.post(
                "/post/publicado/avaliacao", data={"csrf_token": token, "nota": nota}, follow_redirects=True
            )
            self.assertIn(f"Média {nota},0 de 5", resposta.get_data(as_text=True))
        invalida = self.cliente.post(
            "/post/publicado/avaliacao", data={"csrf_token": token, "nota": "2.5"}, follow_redirects=True
        )
        self.assertIn("Informe uma nota inteira de 1 a 5.", invalida.get_data(as_text=True))
        home = self.cliente.get("/").get_data(as_text=True)
        self.assertIn("1 curtida", home)
        self.assertIn("3,0", home)
        resposta = self.cliente.post(
            "/post/publicado/curtida", data={"csrf_token": token, "acao": "descurtir"}, follow_redirects=True
        )
        self.assertIn("Curtir (0)", resposta.get_data(as_text=True))
        with self.app.app_context():
            self.assertEqual(Curtida.query.count(), 0)
            avaliacao = Avaliacao.query.one()
            self.assertEqual((avaliacao.nota, avaliacao.usuario_id), (3, self.leitor))

    def test_dashboard_usa_dados_reais_e_indica_ranking_pendente(self):
        self.entrar("admin")
        with self.app.app_context():
            Avaliacao.avaliar(self.leitor, self.publicado, 4)
            Avaliacao.avaliar(self.leitor, self.rascunho, 1)
        painel = self.cliente.get("/dashboard")
        self.assertEqual(painel.status_code, 200)
        html = painel.get_data(as_text=True)
        self.assertIn("Dashboard", html)
        self.assertIn("<dd>10</dd>", html)
        self.assertIn("4,0", html)
        self.assertIn("2026-05", html)
        self.assertIn("ranking por engajamento aguarda", html)
        self.assertNotIn("<dd>110</dd>", html)
