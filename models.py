# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Professor(db.Model, UserMixin):
    __tablename__ = 'professores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(150), nullable=False)
    turmas = db.relationship('Turma', backref='professor', lazy=True)

class Turma(db.Model):
    __tablename__ = 'turmas'
    id = db.Column(db.Integer, primary_key=True)
    nome_turma = db.Column(db.String(100), nullable=False)
    codigo_turma = db.Column(db.String(20), unique=True, nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professores.id'), nullable=False)
    alunos = db.relationship('Aluno', backref='turma', lazy=True, cascade="all, delete-orphan")

class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    nome_aluno = db.Column(db.String(150), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)
    notas = db.relationship('Nota', backref='aluno', lazy=True, cascade="all, delete-orphan")

class Nota(db.Model):
    __tablename__ = 'notas'
    id = db.Column(db.Integer, primary_key=True)
    avaliacao_nome = db.Column(db.String(100), nullable=False)
    valor_nota = db.Column(db.Float, nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)