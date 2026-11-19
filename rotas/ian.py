"""Páginas do Ian: Home, Detalhe do Post, Meus Posts, Formulário de Post, Categorias.

Os templates (HTML) ficam em templates/ian/.
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensoes import db
from models.categoria import Categoria
from models.post import Post

bp = Blueprint("ian", __name__)

PERFIS_QUE_ESCREVEM = ("AUTOR", "ADMIN")


def exigir_autor():
    """Só AUTOR e ADMIN escrevem posts. Leitor recebe 'acesso negado' (403)."""
    if current_user.perfil not in PERFIS_QUE_ESCREVEM:
        abort(403)


@bp.route("/")
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
        "ian/home.html", posts=posts, categorias=categorias, busca=busca, categoria_id=categoria_id
    )


@bp.route("/post/<slug>")
def detalhe(slug):
    """Só posts PUBLICADOS aparecem ao público; cada abertura soma 1 visualização."""
    post = Post.query.filter_by(slug=slug, status="PUBLICADO").first_or_404()
    post.registrar_visualizacao()
    return render_template("ian/detalhe.html", post=post)


@bp.route("/posts/novo", methods=["GET", "POST"])
@login_required
def novo_post():
    exigir_autor()
    categorias = Categoria.query.order_by(Categoria.nome).all()

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        resumo = request.form.get("resumo", "").strip()
        conteudo = request.form.get("conteudo", "").strip()
        categoria_id = request.form.get("categoria", type=int)
        acao = request.form.get("acao")

        if not titulo or not conteudo or not db.session.get(Categoria, categoria_id or 0):
            flash("Preencha o título, o conteúdo e escolha uma categoria.", "erro")
        else:
            post = Post.criar(titulo, resumo, conteudo, current_user.id, categoria_id)
            if acao == "publicar":
                post.publicar()
                return redirect(url_for("ian.detalhe", slug=post.slug))
            flash("Rascunho salvo.", "ok")
            return redirect(url_for("ian.meus_posts"))

    return render_template("ian/formulario.html", categorias=categorias, form=request.form)


@bp.route("/meus-posts")
@login_required
def meus_posts():
    """Autor vê os próprios posts; admin vê todos."""
    exigir_autor()
    consulta = Post.query
    if current_user.perfil != "ADMIN":
        consulta = consulta.filter_by(autor_id=current_user.id)
    posts = consulta.order_by(Post.data_criacao.desc()).all()
    return render_template("ian/meus_posts.html", posts=posts)


@bp.route("/posts/<int:post_id>/publicar", methods=["POST"])
@login_required
def publicar_post(post_id):
    exigir_autor()
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)
    # Regra: autor só mexe nos próprios posts; admin mexe em todos.
    if post.autor_id != current_user.id and current_user.perfil != "ADMIN":
        abort(403)
    post.publicar()
    flash("Post publicado.", "ok")
    return redirect(url_for("ian.meus_posts"))


# TODO (Ian): editar e excluir post, lista de categorias
