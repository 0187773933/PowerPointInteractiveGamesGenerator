#!/bin/bash
APP_NAME="public-ppt-interactive-generator-server"
sudo docker rm $APP_NAME -f || echo "failed to remove existing ssh server"
id=$(sudo docker run -dit --restart='always' \
--name $APP_NAME \
--mount type=bind,source=/home/morphs/DOCKER_IMAGES/PowerPointInteractiveGamesGenerator/config.json,target=/home/config.json \
-p 17393:9379 \
$APP_NAME config.json)
echo "ID = $id"
sudo docker logs -f "$id"