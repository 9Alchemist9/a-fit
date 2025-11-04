import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

# --- CONFIGURAÇÃO ---
# As variáveis de ambiente serão lidas do ambiente do Render
MEU_EMAIL = os.environ.get("MEU_EMAIL")
SENHA_APP = os.environ.get("SENHA_APP") # Corrigido para corresponder ao Render

# --- INICIALIZAÇÃO DO APP E BANCO DE DADOS ---
app = Flask(__name__)

# Configuração do banco de dados SQLAlchemy
# O Render cria o arquivo no local correto
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# --- MODELO DO BANCO DE DADOS (TABELA CLIENTES) ---
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    servico_escolhido = db.Column(db.String(100), nullable=False)
    valor_mensal = db.Column(db.Float, nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Cliente {self.nome}>'


# --- ENDPOINT PRINCIPAL DA API ---
@app.route('/submit', methods=['POST'])
def submit():
    dados = request.get_json()

    # Validação simples dos dados recebidos
    if not all(k in dados for k in ['nome', 'email', 'telefone', 'servico', 'valor']):
        return jsonify({"mensagem": "Dados incompletos"}), 400

    try:
        # 1. Salva no banco de dados usando SQLAlchemy
        novo_cliente = Cliente(
            nome=dados['nome'],
            email=dados['email'],
            telefone=dados['telefone'],
            servico_escolhido=dados['servico'],
            valor_mensal=float(dados['valor'])
        )
        db.session.add(novo_cliente)
        db.session.commit()
        print(f"Cliente '{dados['nome']}' salvo no banco de dados com sucesso.")

    except Exception as db_error:
        db.session.rollback()
        print(f"!!!!!!!!!! ERRO DE BANCO DE DADOS: {db_error} !!!!!!!!!!")
        return jsonify({"mensagem": "Erro ao salvar os dados."}), 500

    # 2. Tenta enviar a notificação por e-mail
    try:
        print("Tentando enviar e-mail de notificação...")
        msg = EmailMessage()
        msg['Subject'] = f"Nova Inscrição A-FIT: {dados['nome']}"
        msg['From'] = MEU_EMAIL
        msg['To'] = MEU_EMAIL
        msg.set_content(f"""
        Nova inscrição recebida:

        Nome: {dados['nome']}
        E-mail: {dados['email']}
        Telefone: {dados['telefone']}
        Serviço: {dados['servico']}
        Valor: R$ {float(dados['valor']):.2f}
        Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        """)

        # Usando SMTP_SSL para uma conexão mais segura
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MEU_EMAIL, SENHA_APP)
            server.send_message(msg)
        
        print("E-mail enviado com sucesso!")
        return jsonify({"mensagem": "Inscrição realizada com sucesso!"}), 200

    except Exception as email_error:
        # Se o e-mail falhar, o erro será impresso nos logs do Render.
        # A aplicação não quebra e o usuário ainda vê uma mensagem de sucesso.
        print(f"!!!!!!!!!! ERRO AO ENVIAR E-MAIL: {email_error} !!!!!!!!!!")
        return jsonify({"mensagem": "Sua inscrição foi registrada, mas a notificação por e-mail falhou. Entraremos em contato mesmo assim."}), 200


# --- ROTA PARA SERVIR A PÁGINA PRINCIPAL ---
@app.route('/')
def index():
    return render_template('index.html')


# --- COMANDO PARA INICIAR O BANCO DE DADOS (para ser usado no build.sh) ---
# Não é mais necessário chamar init_db() aqui
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True, port=5001)

