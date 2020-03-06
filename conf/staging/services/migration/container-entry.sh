#!/usr/bin/env bash

source /deploy/scripts.sh

# Define settings
export DJANGO_SETTINGS_MODULE=project.manage.settings.staging

run_python_script "Configurando SETTINGS" /deploy/setup/configure-settings.py

run_python_script_with_output "Executando migrate" "manage.py migrate"
run_python_script_with_output "Criado tabelas de cache" "manage.py createcachetable"
run_python_script_with_output "Atualizando Site ID" "manage.py loaddata 000_site_staging"
run_python_script_with_output "Refazendo senha do admin padrão: hugo@congressy.com / mudar123@" "manage.py loaddata 001_admin_staging"
run_python_script_with_output "Recriando token de acesso de teste" "manage.py update_drf_token -u 5 -t 4352cababfd0f7912869a5c7d2b90144e963dff1"

# ADICIONA SUPER USUÁRIOS ÀS ORGANIZAÇÕES COM EVENTOS
run_python_script_with_output "Adicionando admins à organizações" "manage.py admins_to_organizations"
