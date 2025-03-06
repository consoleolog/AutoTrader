#!/bin/bash

UPBIT_CONTAINER_NAME=upbit

EXIST_UPBIT_BLUE=$(sudo docker-compose -p "$UPBIT_CONTAINER_NAME-blue" -f docker-compose.blue.yaml ps | grep Up)

if [ -z "$EXIST_UPBIT_BLUE" ]; then 
    echo "---------------"
    echo " upbit blue up "
    echo "---------------"
    sudo docker-compose -p "$UPBIT_CONTAINER_NAME-blue" -f docker-compose.blue.yaml up -d --build 
    UPBIT_BEFORE_COMPOSE_COLOR="green"
    UPBIT_AFTER_COMPOSE_COLOR="blue"
else
    echo "----------------"
    echo " upbit green up "
    echo "----------------"
    sudo docker-compose -p "$UPBIT_CONTAINER_NAME-green" -f docker-compose.green.yaml up -d --build 
    UPBIT_BEFORE_COMPOSE_COLOR="blue"
    UPBIT_AFTER_COMPOSE_COLOR="green"
fi

#IMAGE_ID=$(sudo docker images -q $IMAGE_NAME)

sleep 5

UPBIT_EXIST_AFTER=$(sudo docker-compose -p "$UPBIT_CONTAINER_NAME-$UPBIT_AFTER_COMPOSE_COLOR" -f docker-compose.$UPBIT_AFTER_COMPOSE_COLOR.yaml ps | grep Up)
if [ -n "$UPBIT_EXIST_AFTER" ]; then
    sudo docker-compose -p "$UPBIT_CONTAINER_NAME-$UPBIT_BEFORE_COMPOSE_COLOR" -f docker-compose.$UPBIT_BEFORE_COMPOSE_COLOR.yaml down
    echo "------------------"
    echo " upbit $UPBIT_BEFORE_COMPOSE_COLOR down"
    echo "------------------"
#    sudo docker rmi "$IMAGE_ID"
fi