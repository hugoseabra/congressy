#!/usr/bin/env bash

source /deploy/scripts.sh

# Define settings
export DJANGO_SETTINGS_MODULE=project.admin_intranet.settings.prod

run_python_script "Configurando WSGI" /deploy/setup/configure-wsgi.py

run_python_script "Configurando SETTINGS" /deploy/setup/configure-settings.py
run_python_script "Configurando VERSÃO" /deploy/setup/configure-version.py
run_python_script "Coletando arquivos estáticos" "manage.py collectstatic --noinput --verbosity 0"
run_python_script_with_output "Atualizando Site ID" "manage.py loaddata 000_site"

echo " > Iniciando SERVER"
echo ;
echo "########################################################################"
echo ;
source /deploy/uwsgi-env.sh
uwsgi --enable-threads --cache 5000 --thunder-lock --show-config
