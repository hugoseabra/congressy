#!/usr/bin/env bash
set -e

##############################################################################
# CUIDADO!
# Esta script será executado dentro do container do postgres.
##############################################################################

BKP_FILE=/docker-entrypoint-initdb.d/backup/backup.sql

if [ -f ${BKP_FILE} ]; then
    PGPASSWORD=${POSTGRES_PASSWORD} pg_restore \
      --host localhost \
      --username ${POSTGRES_USER} \
      --schema public \
      --verbose \
      --dbname ${POSTGRES_DB} < ${BKP_FILE}
fi
