#!/bin/bash

IMAGE_NAME="autotrading:v1"
BITHUMB_CONTAINER_NAME="bithumb"

EXIST_BLUE=$(sudo docker-compose -p $BITHUMB_CONTAINER_NAME-blue -f docker-compose.blue.yaml ps | grep Up)
IMAGE_ID=$(sudo docker images -q $IMAGE_NAME)

if [ -z "$EXIST_BLUE" ]; then
  echo "blue up"
  sudo docker stop upbit-green
  sudo docker stop bithumb-green
  sudo docker rm upbit-green
  sudo docker rm bithumb-green
  sudo docker-compose -p $BITHUMB_CONTAINER_NAME-blue -f docker-compose.blue.yaml up -d --build
else
  echo "green up"
  sudo docker stop upbit-blue
  sudo docker stop bithumb-blue
  sudo docker rm upbit-blue
  sudo docker rm bithumb-blue
  sudo docker-compose -p $BITHUMB_CONTAINER_NAME-green -f docker-compose.green.yaml up -d --build
fi

sleep 10

sudo docker rmi "$IMAGE_ID"
