# Integração das classes de Enzo

## Testes

No PowerShell, na raiz do repositório, execute os testes com o ambiente virtual existente. A suíte usa SQLite em memória.

```powershell
& '.\.venv\Scripts\python.exe' -B -m unittest discover -s tests -v
```

## Demonstração no navegador

Na raiz do repositório, use uma cópia descartável para criar o banco de demonstração e vincular uma tag a um post de exemplo. Interrompa o servidor com `Ctrl+C` ao terminar.

```powershell
$python = (Resolve-Path -LiteralPath '.\.venv\Scripts\python.exe').Path
$demo = Join-Path ([IO.Path]::GetTempPath()) ('blog-enzo-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $demo | Out-Null
Copy-Item -LiteralPath @('app.py', 'extensoes.py', 'criar_banco.py', 'models', 'rotas', 'static', 'templates') -Destination $demo -Recurse
Push-Location -LiteralPath $demo
try {
    & $python -B criar_banco.py
    if ($LASTEXITCODE -ne 0) { throw 'Falha na inicialização da cópia de demonstração.' }
    & $python -B -c "from app import app; from extensoes import db; from models import Post, Post_Tag, Tag; ctx = app.app_context(); ctx.push(); tag = Tag.criar('Guias'); post = Post.query.filter_by(slug='o-que-e-um-arg').one(); db.session.add(Post_Tag(post_id=post.id, tag_id=tag.id)); db.session.commit(); ctx.pop()"
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao vincular a tag de demonstração.' }
    & $python -B -m flask --app app run
} finally {
    Pop-Location
}
```

- Abra [a página inicial](http://127.0.0.1:5000/) e entre com `autor@blog.com` e senha `autor123` para testar curtidas e notas no detalhe de um post.
- Em [Tags](http://127.0.0.1:5000/tags), abra **Guias** para conferir a lista de posts publicados associados.
- Entre com `admin@blog.com` e senha `admin123` para criar, editar e excluir tags e abrir o [Dashboard](http://127.0.0.1:5000/dashboard).

Para rodar com um banco local compatível e já inicializado, use `& '.\.venv\Scripts\python.exe' -B -m flask --app app run` na raiz do repositório. O `criar_banco.py` apaga tabelas. Um banco antigo com a tabela `tag` sem `slug` precisa de uma migração que preserve os registros existentes antes de ser usado com esta branch.

## Pontos de integração

- O detalhe de post já inclui as ações de Enzo. O formulário de publicação do Ian poderá listar `Tag` e persistir os vínculos usando `Post_Tag` quando estiver disponível.
- O Dashboard usa os posts publicados e as visualizações já registradas. Média e ranking de engajamento aguardam alinhamento com Ian. A proposta é medir interações por 100 visualizações, calculando `100 × (curtidas + comentários aprovados + avaliações) / visualizações`. Posts sem visualizações ficam sem taxa. A fórmula e a forma de agregar as taxas no painel precisam ser acordadas antes da ativação.
