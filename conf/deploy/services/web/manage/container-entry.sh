#!/usr/bin/env bash

source /scripts.sh

# Define settings
export DJANGO_SETTINGS_MODULE=project.manage.settings.prod

# Celery correction - https://github.com/celery/celery/pull/4078
export FORKED_BY_MULTIPROCESSING=1

run_python_script "Configurando WSGI" /configure-wsgi.py
run_python_script "Configurando NGINX" /configure-nginx.py

run_python_script "Configurando SETTINGS" /configure-settings.py
run_python_script "Configurando RABBITMQ" /configure-rabbitmq.py
run_python_script "Configurando VERSÃO" /configure-version.py
run_python_script "Coletando arquivos estáticos" "manage.py collectstatic --noinput --verbosity 0"
run_python_script_with_output "Atualizando Site ID" "manage.py loaddata 000_site"

echo " > Iniciando SUPERVISOR"
echo ;
echo "########################################################################"
echo ;
supervisord -n
