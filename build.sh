#!/bin/bash

# Instala as dependências
pip install -r requirements.txt

# Cria as tabelas do banco de dados
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
