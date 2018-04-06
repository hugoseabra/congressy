#!/usr/bin/env bash

# Define settings
export DJANGO_SETTINGS_MODULE=project.manage.settings.prod

# Export all enviorment varibales to file which cron can see it
printenv | grep -v "no_proxy" >> /etc/environment

source /scripts.sh

# Configura dadosde sincronização.
run_python_script "Configurando SYNC" /configure-sync.py
run_bash_script "Verificando existência do Bucket" /create-s3bucket.sh

run_python_script "Configurando SYNC" /configure-cron.py

printf " > Setando entradas: "
crontab /crontab.txt
printf "OK"
echo;

run_python_script "Configurando SETTINGS" /configure-settings.py
run_python_script_with_output "Executando migrate" "manage.py migrate"

/usr/sbin/cron -f -L 15
