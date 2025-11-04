#!/bin/bash

# Instala as dependências
pip install -r requirements.txt

# Exporta a variável de ambiente para que o Flask encontre a aplicação
export FLASK_APP=app.py

# Cria as tabelas do banco de dados
flask db init
flask db migrate -m "Initial migration."
flask db upgrade