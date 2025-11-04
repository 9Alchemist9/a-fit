import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURAÇÃO ---
MEU_EMAIL = os.environ.get("MEU_EMAIL")
SENHA_APP = os.environ.get("SENHA_APP")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ...
db = SQLAlchemy(app)

# Adicione estas duas linhas:
with app.app_context():
    db.create_all()
# ...


# --- MODELO DO BANCO DE DADOS ---
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    servico_escolhido = db.Column(db.String(100), nullable=False)
    valor_mensal = db.Column(db.Float, nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

# --- ENDPOINT SUBMIT ---
@app.route('/submit', methods=['POST'])
def submit():
    dados = request.get_json()
    try:
        novo_cliente = Cliente(
            nome=dados['nome'], email=dados['email'], telefone=dados['telefone'],
            servico_escolhido=dados['servico'], valor_mensal=float(dados['valor'])
        )
        db.session.add(novo_cliente)
        db.session.commit()
        print(f"Cliente '{dados['nome']}' salvo no banco.")
    except Exception as db_error:
        db.session.rollback()
        print(f"!!!!!!!!!! ERRO DE BANCO DE DADOS: {db_error} !!!!!!!!!!")
        return jsonify({"mensagem": "Erro ao salvar os dados."}), 500

    try:
        print("Tentando enviar e-mail...")
        msg = EmailMessage()
        msg['Subject'] = f"Nova Inscrição A-FIT: {dados['nome']}"
        msg['From'] = MEU_EMAIL
        msg['To'] = MEU_EMAIL
        msg.set_content(f"Nova inscrição recebida:\n\nNome: {dados['nome']}\nE-mail: {dados['email']}\nTelefone: {dados['telefone']}\nServiço: {dados['servico']}\nValor: R$ {float(dados['valor']):.2f}")
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MEU_EMAIL, SENHA_APP)
            server.send_message(msg)
        print("E-mail enviado com sucesso!")
        return jsonify({"mensagem": "Inscrição realizada com sucesso!"}), 200
    except Exception as email_error:
        print(f"!!!!!!!!!! ERRO AO ENVIAR E-MAIL: {email_error} !!!!!!!!!!")
        return jsonify({"mensagem": "Inscrição registrada, mas a notificação falhou."}), 200

# --- ROTA INDEX ---
@app.route('/')
def index():
    return render_template('index.html')

