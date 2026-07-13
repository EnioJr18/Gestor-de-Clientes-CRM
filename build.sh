#!/usr/bin/env bash
# Sair se der erro
set -o errexit

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-setup.settings.production}"

# Instalar as dependências
pip install -r requirements.txt

# Juntar os arquivos estáticos (CSS do Bootstrap, etc)
python manage.py collectstatic --no-input

# Rodar as migrações no banco de dados
python manage.py migrate
