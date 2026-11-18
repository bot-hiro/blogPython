"""Páginas do Ian: Home, Detalhe do Post, Meus Posts, Formulário de Post, Categorias.

Os templates (HTML) ficam em templates/ian/.
"""
from flask import Blueprint, render_template, request

from models.categoria import Categoria
from models.post import Post

bp = Blueprint("ian", __name__)


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


# TODO (Ian): detalhe do post, meus posts, formulário de post, lista de categorias
