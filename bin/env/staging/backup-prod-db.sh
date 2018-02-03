#!/usr/bin/env sh
set -e

##############################################################################
# CUIDADO!
# Esta script será executado dentro do container do postgres.
##############################################################################

BASE=$(dirname "$0")

BKP_PATH="/tmp/bkp/backup"

# Cria diretório onde estará o backup
mkdir -p ${BKP_PATH}

BKP_FILE_NAME="backup-`date +'%Y-%m-%d'`.sql"
BKP_FILE_PATH="$BKP_PATH/$BKP_FILE_NAME"

if [ ! -f "$BKP_FILE_PATH" ]; then
    # Dump do DB
    PGPASSWORD=4UnADjyMjeeB7GSc pg_dump \
          --host congressy.cy6gssymlczu.us-east-1.rds.amazonaws.com \
          --port 5499 \
          --username congressy \
          --format=c \
          --verbose \
          cgsyplatform > ${BKP_FILE_PATH}
    echo "1" > ${BKP_PATH}/recreate.txt
else
    echo "0" > ${BKP_PATH}/recreate.txt
fi

# Tamanho do arquivo
echo "Backup size: `du -h ${BKP_FILE_PATH}`"

# Assegura que o postgres irá processar o arquivo colocando o bash em um
# local onde onde será contruído o volume do container do cgsy-postgres
cp "$BASE/db-restore.sh" /tmp/bkp/.
