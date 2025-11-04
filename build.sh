#!/bin/bash

# Instala as dependências
pip install -r requirements.txt

# Executa os comandos de migração do banco de dados
# passando a variável de ambiente diretamente em cada chamada
FLASK_APP=app.py flask db init
FLASK_APP=app.py flask db migrate -m "Initial migration."
FLASK_APP=app.py flask db upgrade
