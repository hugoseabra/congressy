#!/usr/bin/env bash

source /deploy/scripts.sh

# Define settings
export DJANGO_SETTINGS_MODULE=project.manage.settings.staging

run_python_script "Configurando SETTINGS" /deploy/setup/configure-settings.py
run_python_script_with_output "Atualizando Site ID" "manage.py loaddata 000_site_staging"

echo " > Iniciando CELERY"
echo ;
echo "########################################################################"
echo ;
celery --events --loglevel=INFO -A project worker --autoscale=5,2 --loglevel=INFO;
