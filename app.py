"""Programa principal do site. Para rodar: python app.py"""
import os

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

from models import Categoria, Post, Usuario, db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "troque-esta-chave-antes-de-publicar")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def carregar_usuario(user_id):
    return db.session.get(Usuario, int(user_id))


@app.route("/")
def home():
    busca = request.args.get("q", "").strip()
    categoria_id = request.args.get("categoria", type=int)

    consulta = Post.query.filter_by(status="PUBLICADO")
    if busca:
        consulta = consulta.filter(
            Post.titulo.ilike(f"%{busca}%") | Post.resumo.ilike(f"%{busca}%")
        )
    if categoria_id:
        consulta = consulta.filter_by(categoria_id=categoria_id)

    posts = consulta.order_by(Post.data_publicacao.desc()).all()
    categorias = Categoria.query.order_by(Categoria.nome).all()
    return render_template(
        "home.html", posts=posts, categorias=categorias, busca=busca, categoria_id=categoria_id
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        usuario = Usuario.query.filter_by(email=email, ativo=True).first()
        if usuario and usuario.verificar_senha(senha):
            login_user(usuario)
            return redirect(url_for("home"))
        flash("E-mail ou senha incorretos.")
    return render_template("login.html")


@app.route("/sair")
@login_required
def sair():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
