# /app.py - VERSÃO ATUALIZADA COM A ROTA DE UPDATE

import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from flask import Flask, request, jsonify, render_template, Response, redirect, url_for # <<< Adicionado redirect e url_for
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)

# --- CONFIGURAÇÃO E MODELO (Sem alterações) ---
db_path = os.path.join('/tmp', 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    servico_escolhido = db.Column(db.String(100), nullable=False)
    valor_mensal = db.Column(db.Float, nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    forma_pagamento = db.Column(db.String(50), nullable=True, default='Não definido')
    data_inicio = db.Column(db.Date, nullable=True)
    data_fim = db.Column(db.Date, nullable=True)
    parcelas_pagas = db.Column(db.Integer, nullable=True, default=0)

with app.app_context():
    db.create_all()

# --- AUTENTICAÇÃO (Sem alterações) ---
def check_auth(username, password):
    admin_user = os.environ.get("ADMIN_USER")
    admin_pass = os.environ.get("ADMIN_PASS")
    return username == admin_user and password == admin_pass

def authenticate():
    return Response('Acesso negado.', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# --- ROTAS /submit, / e /logout (Sem alterações) ---
@app.route('/submit', methods=['POST'])
def submit():
    # ... (código existente)
    pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    return authenticate()

# --- ROTA /admin (Sem alterações) ---
@app.route('/admin')
@requires_auth
def admin_page():
    todos_os_clientes = Cliente.query.order_by(Cliente.data_hora.desc()).all()
    return render_template('admin.html', clientes=todos_os_clientes)


# --- <<< INÍCIO DA NOVA ROTA: /admin/update >>> ---
@app.route('/admin/update/<int:cliente_id>', methods=['POST'])
@requires_auth # Garante que apenas o admin possa fazer updates
def update_cliente(cliente_id):
    # Busca o cliente específico no banco de dados
    cliente = db.session.get(Cliente, cliente_id)
    if not cliente:
        return "Cliente não encontrado", 404

    try:
        # Pega os dados do formulário enviado
        cliente.forma_pagamento = request.form.get('forma_pagamento')
        
        # Converte as datas de string para objeto date
        data_inicio_str = request.form.get('data_inicio')
        if data_inicio_str:
            cliente.data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()

        data_fim_str = request.form.get('data_fim')
        if data_fim_str:
            cliente.data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()

        # Salva as alterações no banco de dados
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar cliente: {e}")
        # Idealmente, aqui mostraríamos uma mensagem de erro para o usuário

    # Redireciona de volta para a página de administração
    return redirect(url_for('admin_page'))
# --- <<< FIM DA NOVA ROTA >>> ---
