"""Usuario: responsável Amanda."""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensoes import db


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(10), nullable=False, default="LEITOR")  # ADMIN, AUTOR ou LEITOR
    bio = db.Column(db.String(300))
    foto = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, default=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship("Post", back_populates="autor")
    favoritos = db.relationship("Favorito", back_populates="usuario")
    comentarios = db.relationship("Comentario", back_populates="usuario")
    inscricoes = db.relationship("Inscrito", back_populates="usuario")

    def definir_senha(self, senha):
        """Guarda a senha criptografada (nunca a senha pura)."""
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @classmethod
    def autenticar(cls, email, senha):
        """Verifica e-mail e senha. Devolve o usuário se estiver tudo certo."""
        usuario = cls.query.filter_by(email=email, ativo=True).first()
        if usuario and usuario.verificar_senha(senha):
            return usuario
        return None

    @classmethod
    def cadastrar(cls, nome, email, senha, perfil="LEITOR"):
        """Cria um usuário novo, já com a senha criptografada."""
        if cls.query.filter_by(email=email).first():
            return None  # E-mail já cadastrado
        novo_usuario = cls(nome=nome, email=email, perfil=perfil)
        novo_usuario.definir_senha(senha)
        db.session.add(novo_usuario)
        db.session.commit()
        return novo_usuario

    def alterar_senha(self, senha_nova):
        """Troca a senha de um usuário que já existe."""
        self.definir_senha(senha_nova)
        db.session.commit()

    def promover(self, novo_perfil):
        """Muda o perfil (ex: de LEITOR para AUTOR)."""
        self.perfil = novo_perfil
        db.session.commit()

    def desativar(self):
        """Desativa a conta (soft delete)."""
        self.ativo = False
        db.session.commit()

    def total_posts(self):
        """Quantos posts este usuário escreveu."""
        return len(self.posts)

    def total_visualizacoes_autor(self):
        """Soma as visualizações de todos os posts deste autor."""
        return sum(post.visualizacoes for post in self.posts)

    def total_comentarios(self):
        """Quantos comentários este usuário fez (apenas os aprovados)."""
        return sum(1 for c in self.comentarios if c.status == "APROVADO")
