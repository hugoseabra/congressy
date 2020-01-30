#!/usr/bin/env bash

source /deploy/scripts.sh

# Define settings
export DJANGO_SETTINGS_MODULE=project.manage.settings.prod

run_python_script "Configurando SETTINGS" /deploy/setup/configure-settings.py

run_python_script_with_output "Executando migrate" "manage.py migrate"
run_python_script_with_output "Criado tabelas de cache" "manage.py createcachetable"
run_python_script_with_output "Atualizando Site ID" "manage.py loaddata 000_site"

# ADICIONA SUPER USUÁRIOS ÀS ORGANIZAÇÕES COM EVENTOS
run_python_script_with_output "Adicionando admins à organizações" "manage.py admins_to_organizations"
