#!/usr/bin/env bash

# Runs script checking for breaking points
run() {
    local RED='\033[1;31m'
    local NC='\033[0m' # No Color
    local RESULT=`$@`
    if [ -z "$RESULT" ]; then
        printf "OK"
        echo ;
    else
        echo ;
        echo ;
        echo -e "${RED}$RESULT${NC}"
        echo ;
        echo ;
        exit 1
    fi
}

# Runs python script checking for breaking points
run_python_script() {
    printf " > $1: "
    run python $2
}

# Runs bash script checking for breaking points
run_bash_script() {
    printf " > $1: "
    chmod +x "$2"
    run $2
}

# Runs python script without checking for breaking points
run_python_script_with_output() {
    echo ;
    echo "========================================================================"
    echo " > $1: "
    python $2
    echo ;
    echo "========================================================================"
    echo ;
}

# Runs bash script without checking for breaking points
run_bash_script_with_output() {
    echo ;
    echo "========================================================================"
    echo " > $1: "
    chmod +x "$2"
    $2
    echo ;
    echo "========================================================================"
    echo ;
}

echo ;
echo "########################################################################"
echo "PROCESSANDO ENTRY"
echo "########################################################################"
echo ;

run_python_script "Configurando WSGI" /configure-wsgi.py
run_python_script "Configurando NGINX" /configure-nginx.py
run_python_script "Configurando SYNC" /configure-sync.py
run_bash_script "Verificando existência do Bucket" /s3bucket.sh
run_python_script "Configurando SETTINGS" /configure-settings.py
run_python_script "Configurando RODAPÉ" /configure-footer.py
run_python_script "Coletando arquivos estáticos" "manage.py collectstatic --noinput --verbosity 0"
run_python_script_with_output "Executando migrate" "manage.py migrate"
run_python_script_with_output "Populando banco de dados" "manage.py loaddata logtailer_filter logtailer_logfile"

run_bash_script_with_output "Baixando arquivos do S3" /in-sync.sh

echo "Configured: SUCCESS"

echo " > Iniciando SUPERVISOR"
echo ;
echo "########################################################################"
supervisord -n
