"""Páginas da Amanda: Login, Cadastro, Meu Perfil, Moderação de Comentários,
Lista de Inscritos, Meus Favoritos.

Os templates (HTML) ficam em templates/amanda/.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from models.usuario import Usuario

bp = Blueprint("amanda", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        usuario = Usuario.query.filter_by(email=email, ativo=True).first()
        if usuario and usuario.verificar_senha(senha):
            login_user(usuario)
            return redirect(url_for("ian.home"))
        flash("E-mail ou senha incorretos.")
    return render_template("amanda/login.html")


@bp.route("/sair")
@login_required
def sair():
    logout_user()
    return redirect(url_for("ian.home"))


# TODO (Amanda): cadastro, meu perfil, moderação de comentários, inscritos, favoritos
