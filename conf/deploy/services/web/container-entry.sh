#!/usr/bin/env bash


run_python_script "Configurando WSGI" /configure-wsgi.py
run_python_script "Configurando NGINX" /configure-nginx.py

run_python_script "Configurando SETTINGS" /configure-settings.py
run_python_script "Configurando VERSÃO" /configure-version.py
run_python_script "Coletando arquivos estáticos" "manage.py collectstatic --noinput --verbosity 0"
run_python_script_with_output "Executando migrate" "manage.py migrate"
run_python_script_with_output "Atualizando Site ID" "manage.py loaddata 000_site"
