#!/usr/bin/env bash

source /deploy/scripts.sh

# Define settings
export DJANGO_SETTINGS_MODULE=project.manage.settings.prod

run_python_script "Configurando SETTINGS" /deploy/setup/configure-settings.py
run_python_script_with_output "Atualizando Site ID" "manage.py loaddata 000_site"

echo " > Iniciando CELERY"
echo ;
echo "########################################################################"
echo ;
celery --events --loglevel=INFO -A project worker --autoscale=10,1 --loglevel=INFO;