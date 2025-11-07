# /app.py - VERSÃO ATUALIZADA COM A ROTA /ADMIN

import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from flask import Flask, request, jsonify, render_template, Response
from flask_sqlalchemy import SQLAlchemy
from functools import wraps # Importa a ferramenta para criar nosso decorator

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
db_path = os.path.join('/tmp', 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELO DO BANCO DE DADOS ---
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    servico_escolhido = db.Column(db.String(100), nullable=False)
    valor_mensal = db.Column(db.Float, nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

# Cria as tabelas do banco de dados se não existirem
with app.app_context():
    db.create_all()

# --- INÍCIO DA NOVA SEÇÃO: AUTENTICAÇÃO DO ADMIN ---

# 1. Função que verifica as credenciais
def check_auth(username, password):
    """Verifica se o usuário e senha correspondem às variáveis de ambiente."""
    admin_user = os.environ.get("ADMIN_USER")
    admin_pass = os.environ.get("ADMIN_PASS")
    return username == admin_user and password == admin_pass

# 2. Função que solicita a autenticação
def authenticate():
    """Envia uma resposta 401 para solicitar a autenticação do navegador."""
    return Response(
        'Acesso negado. Você precisa se autenticar para acessar esta página.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

# 3. Decorator que protege uma rota
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# --- FIM DA NOVA SEÇÃO ---


# --- ENDPOINT SUBMIT (Sem alterações) ---
@app.route('/submit', methods=['POST'])
def submit():
    meu_email_remetente = os.environ.get("MEU_EMAIL")
    senha_app_remetente = os.environ.get("SENHA_APP")
    if not meu_email_remetente or not senha_app_remetente:
        return jsonify({"mensagem": "Erro de configuração do servidor."}), 500
    dados = request.get_json()
    try:
        novo_cliente = Cliente(
            nome=dados['nome'], email=dados['email'], telefone=dados['telefone'],
            servico_escolhido=dados['servico'], valor_mensal=float(dados['valor'])
        )
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

# --- ROTA INDEX (Sem alterações) ---
@app.route('/')
def index():
    return render_template('index.html')

# --- INÍCIO DA NOVA ROTA: /ADMIN ---

@app.route('/admin')
@requires_auth  # A MÁGICA ACONTECE AQUI: Esta linha protege a rota
def admin_page():
    # Por enquanto, apenas buscamos os clientes. A exibição virá no próximo passo.
    try:
        todos_os_clientes = Cliente.query.order_by(Cliente.data_hora.desc()).all()
    except Exception as e:
        # Se o banco de dados ainda não existir, cria e retorna uma lista vazia
        db.create_all()
        todos_os_clientes = []
        print(f"Banco de dados criado ou erro ao buscar clientes: {e}")

    # Passa a lista de clientes para o template (que vamos criar agora)
    return render_template('admin.html', clientes=todos_os_clientes)

# --- FIM DA NOVA ROTA ---
