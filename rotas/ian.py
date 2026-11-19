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


# ---------- regras de acesso ----------
def exigir_autor():
    """Só AUTOR e ADMIN escrevem posts. Leitor recebe 'acesso negado' (403)."""
    if current_user.perfil not in PERFIS_QUE_ESCREVEM:
        abort(403)


def exigir_admin():
    if current_user.perfil != "ADMIN":
        abort(403)


def carregar_post_permitido(post_id):
    """Regra 4: autor mexe só nos próprios posts; admin mexe em todos."""
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)
    if post.autor_id != current_user.id and current_user.perfil != "ADMIN":
        abort(403)
    return post


# ---------- páginas públicas ----------
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


@bp.route("/categorias")
def categorias():
    todas = Categoria.query.order_by(Categoria.nome).all()
    return render_template("ian/categorias.html", categorias=todas)


@bp.route("/categorias/<slug>")
def posts_por_categoria(slug):
    categoria = Categoria.query.filter_by(slug=slug).first_or_404()
    posts = (
        Post.query.filter_by(categoria_id=categoria.id, status="PUBLICADO")
        .order_by(Post.data_publicacao.desc())
        .all()
    )
    return render_template("ian/categoria_posts.html", categoria=categoria, posts=posts)


# ---------- posts (autor / admin) ----------
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

    return render_template("ian/formulario.html", categorias=categorias, form=request.form, post=None)


@bp.route("/posts/<int:post_id>/editar", methods=["GET", "POST"])
@login_required
def editar_post(post_id):
    exigir_autor()
    post = carregar_post_permitido(post_id)
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
            post.editar(titulo, resumo, conteudo, categoria_id)
            if acao == "publicar" and post.status != "PUBLICADO":
                post.publicar()
            flash("Post atualizado.", "ok")
            return redirect(url_for("ian.meus_posts"))
        form = request.form
    else:
        form = {
            "titulo": post.titulo,
            "resumo": post.resumo or "",
            "conteudo": post.conteudo,
            "categoria": str(post.categoria_id),
        }

    return render_template("ian/formulario.html", categorias=categorias, form=form, post=post)


@bp.route("/posts/<int:post_id>/publicar", methods=["POST"])
@login_required
def publicar_post(post_id):
    exigir_autor()
    post = carregar_post_permitido(post_id)
    post.publicar()
    flash("Post publicado.", "ok")
    return redirect(url_for("ian.meus_posts"))


@bp.route("/posts/<int:post_id>/arquivar", methods=["POST"])
@login_required
def arquivar_post(post_id):
    exigir_autor()
    post = carregar_post_permitido(post_id)
    post.arquivar()
    flash("Post arquivado: ele não aparece mais ao público.", "ok")
    return redirect(url_for("ian.meus_posts"))


@bp.route("/posts/<int:post_id>/excluir", methods=["POST"])
@login_required
def excluir_post(post_id):
    exigir_autor()
    post = carregar_post_permitido(post_id)
    post.excluir()
    flash("Post excluído.", "ok")
    return redirect(url_for("ian.meus_posts"))


# ---------- categorias (só admin) ----------
def _nome_ja_existe(nome, ignorar_id=None):
    existente = Categoria.query.filter(db.func.lower(Categoria.nome) == nome.lower()).first()
    return existente is not None and existente.id != ignorar_id


@bp.route("/admin/categorias", methods=["GET", "POST"])
@login_required
def admin_categorias():
    exigir_admin()
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        if not nome:
            flash("Informe o nome da categoria.", "erro")
        elif _nome_ja_existe(nome):
            flash("Já existe uma categoria com esse nome.", "erro")
        else:
            Categoria.criar(nome, descricao)
            flash("Categoria criada.", "ok")
            return redirect(url_for("ian.admin_categorias"))
    todas = Categoria.query.order_by(Categoria.nome).all()
    return render_template("ian/admin_categorias.html", categorias=todas)


@bp.route("/admin/categorias/<int:categoria_id>/editar", methods=["POST"])
@login_required
def editar_categoria(categoria_id):
    exigir_admin()
    categoria = db.session.get(Categoria, categoria_id) or abort(404)
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    if not nome:
        flash("Informe o nome da categoria.", "erro")
    elif _nome_ja_existe(nome, ignorar_id=categoria.id):
        flash("Já existe uma categoria com esse nome.", "erro")
    else:
        categoria.editar(nome, descricao, categoria.cor)
        flash("Categoria atualizada.", "ok")
    return redirect(url_for("ian.admin_categorias"))


@bp.route("/admin/categorias/<int:categoria_id>/excluir", methods=["POST"])
@login_required
def excluir_categoria(categoria_id):
    exigir_admin()
    categoria = db.session.get(Categoria, categoria_id) or abort(404)
    try:
        categoria.excluir()
        flash("Categoria excluída.", "ok")
    except ValueError as erro:
        flash(str(erro), "erro")
    return redirect(url_for("ian.admin_categorias"))


# TODO (Ian): Post_Tag (depende da Tag do Enzo)
