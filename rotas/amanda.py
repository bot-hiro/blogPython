"""Páginas da Amanda: Login, Cadastro, Meu Perfil, Moderação de Comentários,
Lista de Inscritos, Meus Favoritos.

Os templates (HTML) ficam em templates/amanda/.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user, current_user

from models.usuario import Usuario
from models.favorito import Favorito
from models.inscrito import Inscrito
from models.comentario import Comentario 
from extensoes import db
from models.post import Post

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


# ==========================================
# ROTAS DA AMANDA (IMPLEMENTADAS)
# ==========================================

@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha")
        
        novo_usuario = Usuario.cadastrar(nome=nome, email=email, senha=senha)
        if novo_usuario:
            flash("Cadastro realizado com sucesso! Faça login.")
            return redirect(url_for("amanda.login"))
        else:
            flash("Este e-mail já está cadastrado.")
            
    return render_template("amanda/cadastro.html")


@bp.route("/meu-perfil")
@login_required
def meu_perfil():
    #o Flask-Login dá o current_user
    return render_template("amanda/perfil.html", usuario=current_user)


@bp.route("/meus-favoritos")
@login_required
def meus_favoritos():
    favoritos = Favorito.query.filter_by(usuario_id=current_user.id).all()
    return render_template("amanda/favoritos.html", favoritos=favoritos)


@bp.route("/favoritar/<int:post_id>")
@login_required
def favoritar(post_id):
    resultado = Favorito.favoritar(post_id=post_id, usuario_id=current_user.id)
    if resultado:
        flash("Post salvo nos favoritos!")
    else:
        # Se der None, é porque já existia (regra de negócio)
        flash("Você já favoritou este post.")
    
    # Redireciona para a página do post (assumindo que o Ian criou essa rota)
    post = Post.query.get_or_404(post_id)
    return redirect(url_for("ian.detalhe", slug=post.slug))


@bp.route("/comentar/<int:post_id>", methods=["POST"])
@login_required
def comentar(post_id):
    texto = request.form.get("texto")
    if texto:
        novo_comentario = Comentario(
            texto=texto, 
            post_id=post_id, 
            usuario_id=current_user.id
        )
        novo_comentario.comentar() # Salva como PENDENTE
        flash("Comentário enviado! Ele aparecerá após a aprovação do admin.")
    
    post = Post.query.get_or_404(post_id)
    return redirect(url_for("ian.detalhe", slug=post.slug))


@bp.route("/moderacao")
@login_required
def moderacao():
    # Só admin pode ver isso (regra de negócio)
    if current_user.perfil != "ADMIN":
        flash("Acesso negado. Apenas administradores.")
        return redirect(url_for("ian.home"))
    
    # Pega todos os comentários que estão pendentes
    pendentes = Comentario.query.filter_by(status="PENDENTE").all()
    return render_template("amanda/moderacao.html", comentarios=pendentes)


@bp.route("/aprovar-comentario/<int:id>")
@login_required
def aprovar_comentario(id):
    if current_user.perfil == "ADMIN":
        comentario = Comentario.query.get_or_404(id)
        comentario.aprovar()
        flash("Comentário aprovado!")
    return redirect(url_for("amanda.moderacao"))


@bp.route("/rejeitar-comentario/<int:id>")
@login_required
def rejeitar_comentario(id):
    if current_user.perfil == "ADMIN":
        comentario = Comentario.query.get_or_404(id)
        comentario.rejeitar()
        flash("Comentário rejeitado.")
    return redirect(url_for("amanda.moderacao"))


@bp.route("/inscrever", methods=["POST"])
def inscrever():
    email = request.form.get("email")
    if email:
        resultado = Inscrito.inscrever(email=email)
        if resultado:
            flash("Inscrição na newsletter realizada com sucesso!")
        else:
            flash("Este e-mail já está na nossa lista.")
    
    # Redireciona para a home (de onde veio o formulário)
    return redirect(url_for("ian.home"))


@bp.route("/lista-inscritos")
@login_required
def lista_inscritos():
    if current_user.perfil != "ADMIN":
        flash("Acesso negado.")
        return redirect(url_for("ian.home"))
    
    inscritos = Inscrito.query.order_by(Inscrito.data_inscricao.desc()).all()
    return render_template("amanda/inscritos.html", inscritos=inscritos)