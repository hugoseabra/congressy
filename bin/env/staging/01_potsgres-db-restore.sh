#!/usr/bin/env bash
set -e
###############################################################################
# CUIDADO!
# Esta script é gerenciado pelo CI. Não altere ou mude sem saber o que está
# fazendo.
###############################################################################
# Este arquivo será inserido dentro do container do postgres para que, ao subir
# container, o arquivo possa ser executado pelo próprio entrypoint da imagem.
#
# Dentro do container, a pasta assistida para ver se há arquivos a executar é
# /docker-entrypoint-initdb.d que será construída apontando para um volume
# local para /tmp/bkp. Lá já deve existir o dump do BD de produção construído
# pelo "STEP: Criar dump do BD de produção".
###############################################################################
BKP_FILE=/docker-entrypoint-initdb.d/backup/"backup-`date +'%Y-%m-%d'`.sql"

if [ -f ${BKP_FILE} ]; then
    PGPASSWORD=${POSTGRES_PASSWORD} pg_restore \
      --host localhost \
      --username ${POSTGRES_USER} \
      --schema public \
      --verbose \
      --dbname ${POSTGRES_DB} < ${BKP_FILE}
fi
