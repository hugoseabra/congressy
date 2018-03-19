#!/usr/bin/env bash

source /scripts.sh

run_python_script "Configurando VOLUME" /configure-volume.py


run_bash_script_with_output "Baixando arquivos do S3" /in-sync.sh
