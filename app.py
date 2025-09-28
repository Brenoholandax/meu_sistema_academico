# app.py
import os
from flask import Flask
from models import db

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-segura'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/database.db'
    
    # --- CÓDIGO ADICIONADO ---
    # Garante que a pasta 'instance' exista.
    instance_path = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    # --------------------------

    db.init_app(app)
    
    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        print("Criando o banco de dados...")
        db.create_all()
        print("Banco de dados criado com sucesso!")