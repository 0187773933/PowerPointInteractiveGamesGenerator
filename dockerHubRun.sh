#!/bin/bash
APP_NAME="public-ppt-interactive-generator-server"
sudo docker rm $APP_NAME -f || echo "failed to remove existing server"
id=$(sudo docker run -dit --restart="always" \
--name $APP_NAME \
--mount type=bind,source=/home/morphs/DOCKER_IMAGES/PowerPointInteractiveGamesGenerator/config.json,target=/home/config.json \
-p 17393:9379 \
xp6qhg9fmuolztbd2ixwdbtd1/ppt-interactive-generator-server config.json)
echo "ID = $id"
sudo docker logs -f "$id"
# sudo docker run --rm -it --entrypoint bash b30b9f9f73bd