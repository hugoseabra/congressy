#!/usr/bin/env bash

source /scripts.sh

# Define settings
export DJANGO_SETTINGS_MODULE=project.manage.settings.prod

run_python_script "Configurando SETTINGS" /configure-settings.py
run_python_script "Configurando RABBITMQ" /configure-rabbitmq.py

run_python_script_with_output "Executando migrate" "manage.py migrate"

# ADICIONA SUPER USUÁRIOS ÀS ORGANIZAÇÕES COM EVENTOS
run_python_script_with_output "Adicionando admins à organizações" "manage.py admins_to_organizations"

# TEMP
run_python_script_with_output "Migrando infraestrutura de debitos" "manage.py update_debts"
run_python_script_with_output "Migrando infraestrutura de pagamento" "manage.py update_payments"
