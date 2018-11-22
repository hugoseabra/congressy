#!/usr/bin/env sh
set -ex

BKP_DIR="/tmp/bkp"
BKP_DUMP_DIR="$BKP_DIR/backup"

BKP_FILE_NAME="backup-`date +'%Y-%m-%d'`"
BKP_FILE_PATH="$BKP_DUMP_DIR/$BKP_FILE_NAME.sql"

PROD_BKP_FILE_NAME="prod_backup_`date +'%Y-%m-%d'`"
PROD_BKP_FILE_PATH="$BKP_DUMP_DIR/$PROD_BKP_FILE_NAME.sql"

if [ -f "$BKP_FILE_PATH" ]; then

      mv $BKP_FILE_PATH $PROD_BKP_FILE_PATH

    PGPASSWORD=congressy pg_dump \
        --host localhost \
        --port 5432 \
        --username congressy \
        --schema public \
        --format=c \
        --verbose \
    cgsyplatform > ${BKP_FILE_PATH}

fi

