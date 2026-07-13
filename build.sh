#!/usr/bin/env bash
# Sair se der erro
set -o errexit

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.production}"

# Instalar as dependências
pip install -r backend/requirements.txt

# Juntar os arquivos estáticos (CSS do Bootstrap, etc)
python backend/manage.py collectstatic --no-input

# Rodar as migrações no banco de dados
python backend/manage.py migrate
