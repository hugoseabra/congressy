#!/usr/bin/env bash
set -ex

POSTGRES_IMAGE='postgres:10-alpine'
POSTGRES_CONTAINER_NAME='postgres'

volume_exists() {
    docker volume ls | grep $POSTGRES_CONTAINER_NAME > /dev/null 2>&1
}

network_exists() {
    docker network ls | grep $POSTGRES_CONTAINER_NAME > /dev/null 2>&1
}

image_exists() {
    docker images -q $POSTGRES_IMAGE > /dev/null 2>&1
}

container_active() {
    docker ps -q -f status=running -f name=^/${POSTGRES_CONTAINER_NAME} > /dev/null 2>&1
}

container_exists() {
    docker ps -q -f name=$POSTGRES_CONTAINER_NAME > /dev/null 2>&1
}

if container_exists && ! container_active; then
    docker start $POSTGRES_CONTAINER_NAME
    echo "Aguardando container iniciar"
    sleep 10

elif ! container_exists; then

    if ! image_exists; then
        docker pull $POSTGRES_IMAGE
    fi

    if ! network_exists; then
        docker network create $POSTGRES_CONTAINER_NAME
    fi

    if ! volume_exists; then
        docker volume create $POSTGRES_CONTAINER_NAME
    fi

    docker run -tid \
        -p 5432:5432 \
        -v $POSTGRES_CONTAINER_NAME:/var/lib/postgresql \
        --name $POSTGRES_CONTAINER_NAME \
        --network $POSTGRES_CONTAINER_NAME \
        $POSTGRES_IMAGE

    echo "Aguardando container iniciar"
    sleep 10
fi
