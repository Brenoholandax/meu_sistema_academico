import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

# --- Inicialização das Extensões ---
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, faça o login para acessar esta página."
login_manager.login_message_category = "info"

# --- Definição de TODOS os Modelos ---

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

@login_manager.user_loader
def load_user(user_id):
    return Professor.query.get(int(user_id))

# --- Função para Criar a Aplicação (Factory Pattern) ---
def create_app():
    app = Flask(__name__)
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    instance_path = os.path.join(BASE_DIR, 'instance')
    db_path = os.path.join(instance_path, 'database.db')

    app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-segura'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    os.makedirs(instance_path, exist_ok=True)

    # Inicializa as extensões com a aplicação
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # --- Rotas da Aplicação (AGORA DENTRO DA FUNÇÃO) ---
    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        # (O código desta função continua o mesmo)
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            nome = request.form.get('nome')
            email = request.form.get('email')
            senha = request.form.get('senha')
            existing_user = Professor.query.filter_by(email=email).first()
            if existing_user:
                flash('Este email já está registrado.', 'warning')
                return redirect(url_for('login'))
            senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')
            novo_professor = Professor(nome=nome, email=email, senha_hash=senha_hash)
            db.session.add(novo_professor)
            db.session.commit()
            flash('Conta criada com sucesso! Faça o login.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # (O código desta função continua o mesmo)
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            email = request.form.get('email')
            senha = request.form.get('senha')
            professor = Professor.query.filter_by(email=email).first()
            if professor and bcrypt.check_password_hash(professor.senha_hash, senha):
                login_user(professor)
                return redirect(url_for('dashboard'))
            else:
                flash('Login falhou. Verifique o email e a senha.', 'danger')
        return render_template('login.html')

    @app.route('/dashboard', methods=['GET', 'POST'])
    @login_required
    def dashboard():
        # (Esta é a função que atualizamos no passo anterior)
        if request.method == 'POST':
            nome_turma = request.form.get('nome_turma')
            codigo_turma = request.form.get('codigo_turma')
            turma_existente = Turma.query.filter_by(codigo_turma=codigo_turma).first()
            if turma_existente:
                flash('Já existe uma turma com este código.', 'danger')
            else:
                nova_turma = Turma(nome_turma=nome_turma, codigo_turma=codigo_turma, professor_id=current_user.id)
                db.session.add(nova_turma)
                db.session.commit()
                flash('Turma criada com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        turmas_do_professor = Turma.query.filter_by(professor_id=current_user.id).order_by(Turma.nome_turma).all()
        return render_template('dashboard.html', turmas=turmas_do_professor)

    @app.route('/logout')
    @login_required
    def logout():
        # (O código desta função continua o mesmo)
        logout_user()
        return redirect(url_for('login'))

    return app

# --- Execução da Aplicação ---
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)