import sqlite3
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from datetime import datetime
from flask import Flask, request, jsonify, render_template # Adicione render_template aqui


# --- CONFIGURAÇÃO ---
# Altere estas variáveis com seus dados
MEU_EMAIL = os.environ.get("MEU_EMAIL")
SENHA_DE_APP = os.environ.get("SENHA_DE_APP")
NOME_DO_REMETENTE = "Notificação A-FIT"

# --- INICIALIZAÇÃO DO APP FLASK ---
app = Flask(__name__)

# --- FUNÇÃO PARA INICIAR O BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Cria a tabela se ela não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT NOT NULL,
            servico_escolhido TEXT NOT NULL,
            valor_mensal REAL NOT NULL,
            data_hora TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# --- FUNÇÃO PARA ENVIAR E-MAIL DE NOTIFICAÇÃO ---
def enviar_notificacao(dados_cliente):
    try:
        # Corpo do e-mail
        corpo_email = f"""
        <h1>Novo Cliente Registrado!</h1>
        <p>Um novo cliente se registrou para seus serviços de assessoria.</p>
        <h2>Detalhes do Cliente:</h2>
        <ul>
            <li><strong>Nome:</strong> {dados_cliente['nome']}</li>
            <li><strong>Email:</strong> {dados_cliente['email']}</li>
            <li><strong>Telefone:</strong> {dados_cliente['telefone']}</li>
            <li><strong>Serviço:</strong> {dados_cliente['servico']}</li>
            <li><strong>Valor:</strong> R$ {dados_cliente['valor']:.2f}</li>
            <li><strong>Data:</strong> {dados_cliente['data']}</li>
        </ul>
        <p>Entre em contato o mais rápido possível!</p>
        """

        msg = MIMEText(corpo_email, 'html')
        msg['From'] = NOME_DO_REMETENTE
        msg['To'] = MEU_EMAIL
        msg['Subject'] = f"Novo Cliente: {dados_cliente['nome']}"

        # Conexão com o servidor SMTP do Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MEU_EMAIL, SENHA_DE_APP)
        server.sendmail(MEU_EMAIL, MEU_EMAIL, msg.as_string())
        server.quit()
        print("Notificação por e-mail enviada com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")


# --- ENDPOINT PRINCIPAL DA API ---
@app.route('/submit', methods=['POST'])
def handle_submission():
    # 1. Pega os dados enviados pelo formulário (frontend)
    dados = request.get_json()

    # Validação simples dos dados recebidos
    if not all(k in dados for k in ['nome', 'email', 'telefone', 'servico', 'valor']):
        return jsonify({"status": "erro", "mensagem": "Dados incompletos"}), 400

    # 2. Prepara os dados para o banco
    nome = dados['nome']
    email = dados['email']
    telefone = dados['telefone']
    servico = dados['servico']
    valor = float(dados['valor'])
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 3. Salva no banco de dados
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clientes (nome, email, telefone, servico_escolhido, valor_mensal, data_hora) VALUES (?, ?, ?, ?, ?, ?)",
            (nome, email, telefone, servico, valor, data_hora)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar no banco de dados: {e}")
        return jsonify({"status": "erro", "mensagem": "Erro interno no servidor"}), 500

    # 4. Envia a notificação por e-mail
    dados_email = {
        'nome': nome, 'email': email, 'telefone': telefone, 
        'servico': servico, 'valor': valor, 'data': data_hora
    }
    enviar_notificacao(dados_email)

    # 5. Retorna uma resposta de sucesso para o frontend
    return jsonify({"status": "sucesso", "mensagem": "Dados recebidos e processados!"})

# --- ROTA PARA SERVIR A PÁGINA PRINCIPAL ---
@app.route('/')
def index():
    # Renderiza o template a partir da pasta 'templates'
    return render_template('index.html')

# --- EXECUÇÃO DO APP ---
if __name__ == '__main__':
    init_db()  # Garante que o banco de dados e a tabela existam ao iniciar
    app.run(debug=True, port=5001) # Executa o servidor em modo de depuração