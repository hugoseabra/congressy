#!/usr/bin/env bash

# Define settings
export DJANGO_SETTINGS_MODULE=project.manage.settings.prod

# Export all enviorment varibales to file which cron can see it
printenv | grep -v "no_proxy" >> /etc/environment

source /deploy/scripts.sh

# Configura dadosde sincronização.
run_python_script "Configurando SYNC" /deploy/setup/configure-sync.py
run_bash_script "Verificando existência do Bucket" /create-s3bucket.sh

run_python_script "Configurando CRON" /deploy/setup/configure-cron.py

printf " > Setando entradas: "
crontab /crontab.txt
printf "OK"
echo;

run_python_script "Configurando SETTINGS" /deploy/setup/configure-settings.py

/usr/sbin/cron -f -L 15
