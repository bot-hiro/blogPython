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

    def definir_senha(self, senha):
        """Guarda a senha criptografada (nunca a senha pura)."""
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    # TODO (Amanda): autentica(), cadastrar(), alterar_senha(), promover(), desativar(),
    #                total_posts(), total_visualizacoes_autor(), total_comentarios()
