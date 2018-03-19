#!/usr/bin/env bash

source /scripts.sh

# Configura dadosde sincronização.
run_python_script "Configurando SYNC" /configure-sync.py
run_bash_script "Verificando existência do Bucket" /create-s3bucket.sh

run_python_script "Configurando SYNC" /configure-cron.py

printf " > Setando entradas: "
echo "" >> /crontab.txt
crontab /crontab.txt
printf "OK"
echo;

run_bash_script "Verificando existência do Bucket" /s3bucket.sh
run_python_script "Configurando SETTINGS" /configure-settings.py
run_python_script_with_output "Executando migrate" "manage.py migrate"
run_python_script_with_output "Atualizando Site ID" "manage.py loaddata 000_site"

run_bash_script_with_output "Baixando arquivos do S3" /in-sync.sh
