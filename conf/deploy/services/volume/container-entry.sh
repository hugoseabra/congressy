#!/usr/bin/env bash

source /scripts.sh

# Configura dadosde sincronização.
run_python_script "Configurando SYNC" /configure-sync.py

run_bash_script "Verificando existência do Bucket" /create-s3bucket.sh

# Puxa arquivos do S3, se necessário.
run_bash_script_with_output "Baixando arquivos do S3" /in-sync.sh
