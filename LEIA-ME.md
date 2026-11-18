# Blog ARG: como o grupo trabalha

## Quem mexe em quê

| Pessoa | Classes (pasta `models/`) | Páginas (pasta `rotas/`) | HTML (pasta `templates/`) |
|---|---|---|---|
| Ian | post, categoria, post_tag | `rotas/ian.py` | `templates/ian/` |
| Amanda | usuario, comentario, inscrito, favorito | `rotas/amanda.py` | `templates/amanda/` |
| Enzo | curtida, avaliacao, tag, dashboard | `rotas/enzo.py` | `templates/enzo/` |

**Regra de ouro:** só edite os arquivos da sua linha. Se precisar mudar um arquivo
de outra pessoa (ou `app.py`, `extensoes.py`, `base.html`, `style.css`), avise no grupo antes.

Todas as tabelas já estão criadas com as colunas do diagrama. Os métodos de cada
classe estão marcados com `TODO (Nome)` dentro do arquivo da classe.

## Primeira vez no computador

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python criar_banco.py
    python app.py

Abra http://127.0.0.1:5000. Login de teste: autor@blog.com / autor123

## Rotina com o GitHub Desktop

1. Confira que o topo mostra a **sua branch** (nunca a main).
2. Faça Fetch/Pull origin e, se a main mudou, Branch > Update from main.
3. Programe, teste no seu computador, faça commit e Push origin.
4. Com a parte funcionando, abra um Pull Request para a main.

Mudou a estrutura das tabelas? Rode `python criar_banco.py` de novo (ele recria o banco do zero).
