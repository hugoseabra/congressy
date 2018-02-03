#!/usr/bin/env sh
set -e
###############################################################################
# CUIDADO!
# Esta script é gerenciado pelo CI. Não altere ou mude sem saber o que está
# fazendo.
###############################################################################
# CI-STEP: Gerenciar banco de dados de ambiente staging (RC)
#
# SUB-STEP 2:
# Criar dump do banco de dados de produção somente se o backup não foi feito no
# dia. Será apenas um backup por dia, pois não há necessidade de se fazer mais
# de uma vez por dia, já que é para testes, pois o backup de produção consome
# recursos do servidor concorrente com a aplicação de produção.
#
# SUB-STEP 2:
# O backup será restaurado somente se houveR um novo dump dia. Não há necessi-
# dade destruir o banco de dados do container se não há novo dump, mantendo os
# dados criados/modificados/deletados na versão RC mesmo fazendo as devidas mo-
# dificações.
#
# OBS: deve-se ter certeza que o container subiu.
###############################################################################
BASE=$(dirname "$0")

BKP_DIR="/tmp/bkp"
BKP_DUMP_DIR="$BKP_DIR/backup"

# Cria diretório onde estará o backup
mkdir -p ${BKP_DUMP_DIR}

BKP_FILE_NAME="backup-`date +'%Y-%m-%d'`"
BKP_FILE_PATH="$BKP_DUMP_DIR/$BKP_FILE_NAME.sql"

# =============================================================================
# SUB-STEP 1
# - Verifica se arquivo do dia existe
# - Informa tamanho do arquivo e se será recriado o banco de dados
# - Copia arquivo mais recente do script de restauração
#   (01_potsgres-db-restore.sh) para o local onde será construído o volume do
#   container.
# =============================================================================
echo "========================================================================"
echo "SUB-STEP 1: iniciando"
echo "========================================================================"
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

echo "========================================================================"
echo "SUB-STEP 1: finalizado"
echo "========================================================================"

# =============================================================================
# SUB-STEP 2
# - (Re)Cria banco de dados completo, caso o dump do dia seja novo.
# - Verifica se container realmente subiu.
# =============================================================================]
RECREATE=$(cat ${BKP_PATH}/recreate.txt)

echo "========================================================================"
echo "SUB-STEP 2: iniciando"
echo "========================================================================"
if [ "$RECREATE" == "1" ]; then
    echo "Recriando banco de dados."

    # o docker-compose do staging pode depender de um env-file que pode não
    # existir
    touch ./bin/env/staging/env-cgsy-staging

    # cgsy-staging depende da rede criada pelo stack do banco. Devemos ter
    # certeza que o container não está rodando para destruir o banco, caso
    # contrário, o Docker não irá destruir informando que há um container
    # utilizando a rede.
    docker-compose -f ./bin/env/staging/docker-compose.yml down

    # Mata image e destroi rede, volumes e container
    docker-compose -f ./bin/env/docker-compose.yml down

    # Recria tudo novamente
    docker-compose -f ./bin/env/docker-compose.yml up -d
    sleep 5

    RUNNING=$(docker inspect -f {{.State.Running}} cgsy-postgres)
    if [ "$RUNNING" != "true" ]; then
        echo "Container não subiu."
        exit 1
    fi
else:
    echo "Banco de dados não será recriado."
fi
echo "========================================================================"
echo "SUB-STEP 2: finalizado"
echo "========================================================================"