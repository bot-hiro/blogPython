"""Tags, interações e estatísticas do blog."""
from secrets import compare_digest, token_urlsafe

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from extensoes import db
from models.avaliacao import Avaliacao
from models.curtida import Curtida
from models.dashboard import Dashboard
from models.post import Post
from models.post_tag import Post_Tag
from models.tag import Tag

bp = Blueprint("enzo", __name__)


def _csrf_enzo():
    token = session.get("csrf_enzo")
    if token is None:
        token = token_urlsafe(32)
        session["csrf_enzo"] = token
    return token


@bp.before_request
def _validar_formulario():
    if request.method == "POST" and current_user.is_authenticated:
        esperado = session.get("csrf_enzo", "")
        enviado = request.form.get("csrf_token", "")
        if not esperado or not compare_digest(esperado.encode(), enviado.encode()):
            abort(400)


def _avaliacao_do_usuario(post_id):
    return Avaliacao.query.filter_by(post_id=post_id, usuario_id=current_user.id).one_or_none()


def _estado_interacoes(post_id):
    avaliacao = _avaliacao_do_usuario(post_id)
    return {
        "curtiu": Curtida.usuario_curtiu(current_user.id, post_id),
        "nota": avaliacao.nota if avaliacao else None,
    }


@bp.app_context_processor
def _contexto_enzo():
    return {"csrf_enzo": _csrf_enzo, "estado_interacoes_enzo": _estado_interacoes}


def _exigir_admin():
    if current_user.perfil != "ADMIN":
        abort(403)


@bp.get("/tags")
def listar_tags():
    tags = Tag.query.order_by(Tag.nome).all()
    return render_template("enzo/tags.html", tags=tags)


@bp.post("/tags")
@login_required
def criar_tag():
    _exigir_admin()
    try:
        Tag.criar(request.form.get("nome"))
    except ValueError as erro:
        flash(str(erro), "enzo_erro")
    except IntegrityError:
        flash("Já existe uma tag com esse nome ou endereço.", "enzo_erro")
    return redirect(url_for("enzo.listar_tags"), code=303)


@bp.post("/tags/<int:tag_id>/editar")
@login_required
def editar_tag(tag_id):
    _exigir_admin()
    tag = db.get_or_404(Tag, tag_id)
    try:
        tag.editar(request.form.get("nome"))
    except ValueError as erro:
        flash(str(erro), "enzo_erro")
    except IntegrityError:
        flash("Já existe uma tag com esse nome.", "enzo_erro")
    return redirect(url_for("enzo.listar_tags"), code=303)


@bp.post("/tags/<int:tag_id>/excluir")
@login_required
def excluir_tag(tag_id):
    _exigir_admin()
    tag = db.get_or_404(Tag, tag_id)
    tag.excluir()
    return redirect(url_for("enzo.listar_tags"), code=303)


@bp.get("/tags/<slug>")
def posts_por_tag(slug):
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    posts = (
        Post.query.join(Post_Tag, Post_Tag.post_id == Post.id)
        .filter(Post_Tag.tag_id == tag.id, Post.status == "PUBLICADO")
        .order_by(Post.data_publicacao.desc(), Post.id.desc())
        .all()
    )
    return render_template("enzo/posts_por_tag.html", tag=tag, posts=posts)


def _post_publicado(slug):
    return Post.query.filter_by(slug=slug, status="PUBLICADO").first_or_404()


@bp.post("/post/<slug>/curtida")
@login_required
def curtir_post(slug):
    post = _post_publicado(slug)
    acao = request.form.get("acao")
    if acao == "curtir":
        Curtida.curtir(current_user.id, post.id)
    elif acao == "descurtir":
        Curtida.descurtir(current_user.id, post.id)
    else:
        abort(400)
    return redirect(url_for("ian.detalhe", slug=post.slug, _anchor="interacoes"), code=303)


@bp.post("/post/<slug>/avaliacao")
@login_required
def avaliar_post(slug):
    post = _post_publicado(slug)
    nota = request.form.get("nota", type=int)
    avaliacao = _avaliacao_do_usuario(post.id)
    try:
        if avaliacao is None:
            Avaliacao.avaliar(current_user.id, post.id, nota)
        else:
            avaliacao.alterar_nota(nota)
    except ValueError as erro:
        flash(str(erro), "enzo_erro")
    return redirect(url_for("ian.detalhe", slug=post.slug, _anchor="interacoes"), code=303)


@bp.get("/dashboard")
@login_required
def dashboard():
    _exigir_admin()
    return render_template(
        "enzo/dashboard.html",
        resumo=Dashboard.gerar_resumo(),
        posts_por_mes=Dashboard.posts_por_mes(),
        ranking=Dashboard.top_5_posts_por_engajamento(),
        autor_mais_lido=Dashboard.autor_mais_lido(),
        categoria_mais_popular=Dashboard.categoria_mais_popular(),
    )
