#!/usr/bin/env sh
set -e
###############################################################################
# CUIDADO!
# Esta script é gerenciado pelo CI. Não altere ou mude sem saber o que está
# fazendo.
###############################################################################
# CI-STEP: Gerenciar banco de dados de ambiente staging (RC)
#
# Criar dump do banco de dados de produção somente se o backup não foi feito no
# dia. Será apenas um backup por dia, pois não há necessidade de se fazer mais
# de uma vez por dia, já que é para testes, pois o backup de produção consome
# recursos do servidor concorrente com a aplicação de produção.
#
# - Verifica se arquivo do dia existe
# - Informa tamanho do arquivo e se será recriado o banco de dados
# - Copia arquivo mais recente do script de restauração
#   (01_potsgres-db-restore.sh) para o local onde será construído o volume do
#   container.
###############################################################################

function error_msg() {
    local RED='\033[1;31m'
    local NC='\033[0m' # No Color
    echo ;
    echo ;
    echo -e "${RED}$RESULT${NC}"
    echo ;
    echo ;
}

BASE=$(dirname "$0")

BKP_DIR="/tmp/bkp"
BKP_DUMP_DIR="$BKP_DIR/backup"

# Cria diretório onde estará o backup
mkdir -p ${BKP_DUMP_DIR}

BKP_FILE_NAME="backup-`date +'%Y-%m-%d'`"
BKP_FILE_PATH="$BKP_DUMP_DIR/$BKP_FILE_NAME.sql"

if [ ! -f "$BKP_FILE_PATH" ]; then
    # Dump do DB
    PGPASSWORD=4UnADjyMjeeB7GSc pg_dump \
          --host congressy.cy6gssymlczu.us-east-1.rds.amazonaws.com \
          --port 5499 \
          --username congressy \
          --format=c \
          --verbose \
          cgsyplatform > ${BKP_FILE_PATH}

    echo "1" > ${BKP_DUMP_DIR}/recreate.txt
else
    echo "0" > ${BKP_DUMP_DIR}/recreate.txt
fi

# Tamanho do arquivo
echo "Backup size: `du -h ${BKP_FILE_PATH}`"

# Assegura que o postgres irá processar o arquivo colocando o bash em um local
# onde onde será contruído o volume do container do cgsy-postgres.
cp ${BASE}/01_potsgres-db-restore.sh ${BKP_DIR}/db-restore.sh
