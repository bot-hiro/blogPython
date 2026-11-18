"""Ferramentas compartilhadas por todo o projeto (banco e login).

Não precisa editar este arquivo.
"""
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
