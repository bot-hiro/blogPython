"""Programa principal. Para rodar: python app.py

Este arquivo já registra as páginas (rotas) de cada pessoa.
Em condições normais, ninguém precisa editar aqui.
"""
import os

from flask import Flask

from extensoes import db, login_manager
from models.usuario import Usuario
from rotas import amanda, enzo, ian

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "troque-esta-chave-antes-de-publicar")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "amanda.login"


@login_manager.user_loader
def carregar_usuario(user_id):
    return db.session.get(Usuario, int(user_id))


app.register_blueprint(ian.bp)
app.register_blueprint(amanda.bp)
app.register_blueprint(enzo.bp)

if __name__ == "__main__":
    app.run(debug=True)
