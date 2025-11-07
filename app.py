# /app.py - VERSÃO ATUALIZADA COM LÓGICA DE PARCELAS

import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from flask import Flask, request, jsonify, render_template, Response, redirect, url_for
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
    meu_email_remetente = os.environ.get("MEU_EMAIL")
    senha_app_remetente = os.environ.get("SENHA_APP")
    if not meu_email_remetente or not senha_app_remetente:
        return jsonify({"mensagem": "Erro de configuração do servidor."}), 500
    dados = request.get_json()
    try:
        novo_cliente = Cliente(nome=dados['nome'], email=dados['email'], telefone=dados['telefone'], servico_escolhido=dados['servico'], valor_mensal=float(dados['valor']))
        db.session.add(novo_cliente)
        db.session.commit()
    except Exception as db_error:
        db.session.rollback()
        return jsonify({"mensagem": "Erro ao salvar os dados."}), 500
    try:
        msg = EmailMessage()
        msg['Subject'] = f"Nova Inscrição A-FIT: {dados['nome']}"
        msg['From'] = meu_email_remetente
        msg['To'] = meu_email_remetente
        msg.set_content(f"Nova inscrição recebida:\n\nNome: {dados['nome']}\nE-mail: {dados['email']}\nTelefone: {dados['telefone']}\nServiço: {dados['servico']}\nValor: R$ {float(dados['valor']):.2f}")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(meu_email_remetente, senha_app_remetente)
            server.send_message(msg)
        return jsonify({"mensagem": "Inscrição realizada com sucesso!"}), 200
    except Exception as email_error:
        return jsonify({"mensagem": "Inscrição registrada, mas a notificação falhou."}), 200

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

# --- ROTA /admin/update (COM LÓGICA DE PARCELAS) ---
@app.route('/admin/update/<int:cliente_id>', methods=['POST'])
@requires_auth
def update_cliente(cliente_id):
    cliente = db.session.get(Cliente, cliente_id)
    if not cliente:
        return "Cliente não encontrado", 404

    try:
        # --- Lógica existente (sem alterações) ---
        cliente.forma_pagamento = request.form.get('forma_pagamento')
        data_inicio_str = request.form.get('data_inicio')
        if data_inicio_str:
            cliente.data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim_str = request.form.get('data_fim')
        if data_fim_str:
            cliente.data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()

        # --- <<< INÍCIO DA NOVA LÓGICA DE PARCELAS >>> ---
        # O formulário enviará uma lista de todos os checkboxes marcados.
        # O nome de cada checkbox será 'parcela_paga'.
        # request.form.getlist('parcela_paga') pega todos eles.
        parcelas_marcadas = request.form.getlist('parcela_paga')
        # A quantidade de itens na lista é o número de parcelas pagas.
        cliente.parcelas_pagas = len(parcelas_marcadas)
        # --- <<< FIM DA NOVA LÓGICA DE PARCELAS >>> ---

        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar cliente: {e}")

    return redirect(url_for('admin_page'))
