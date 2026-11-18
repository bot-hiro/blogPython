"""Cria o banco e coloca dados de exemplo. Rode uma vez: python criar_banco.py"""
from datetime import datetime

from app import app
from models import Categoria, Post, Usuario, db

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = Usuario(nome="Administrador", email="admin@blog.com", perfil="ADMIN")
    admin.definir_senha("admin123")  # só para testes: troque antes de publicar
    autor = Usuario(nome="Autor Exemplo", email="autor@blog.com", perfil="AUTOR")
    autor.definir_senha("autor123")

    guias = Categoria(nome="Guias", slug="guias", descricao="Como começar e se organizar")
    casos = Categoria(nome="Casos", slug="casos", descricao="ARGs que marcaram época")
    bastidores = Categoria(nome="Bastidores", slug="bastidores", descricao="Como o blog é feito")
    db.session.add_all([admin, autor, guias, casos, bastidores])
    db.session.commit()

    texto = "Texto de exemplo para o post. " * 40
    exemplos = [
        ("O que é um ARG e como começar a jogar", "o-que-e-um-arg",
         "Uma introdução simples ao jogo de realidade alternativa, sem termos difíceis.", guias),
        ("Como organizar uma equipe para decifrar pistas", "equipe-pistas",
         "Dividir tarefas, registrar descobertas e não perder nenhuma pista no caminho.", guias),
        ("Do protótipo ao site: os bastidores do blog", "bastidores-do-blog",
         "O que o grupo decidiu antes de começar a programar com Python.", bastidores),
    ]
    for titulo, slug, resumo, categoria in exemplos:
        db.session.add(Post(
            titulo=titulo, slug=slug, resumo=resumo, conteudo=texto,
            status="PUBLICADO", data_publicacao=datetime.utcnow(),
            autor_id=autor.id, categoria_id=categoria.id,
        ))
    db.session.commit()
    print("Banco criado. Login de teste: autor@blog.com / autor123")
