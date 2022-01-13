#!/bin/bash
APP_NAME="public-ppt-interactive-generator-server"
sudo docker rm $APP_NAME -f || echo "failed to remove existing ssh server"

id=$(sudo docker run -dit --restart='always' \
--name $APP_NAME \
--volume /mnt/blockstorage/PPTIG/IMAGES:/home/morphs/STORAGE/IMAGES \
--volume /mnt/blockstorage/PPTIG/BLOBS:/home/morphs/STORAGE/BLOBS \
--mount type=bind,source=/home/morphs/DOCKER_IMAGES/PowerPointInteractiveGamesGenerator/config.json,target=/home/config.json \
-p 17393:9379 \
$APP_NAME config.json)
echo "ID = $id"

sudo docker logs -f "$id"


# sudo docker rm -f "spotify-dbus-controller"

# sudo docker run -it --privileged='true' --restart='always' \
# --name 'spotify-dbus-controller' \
# --network host \
# --mount type=bind,source=/run/user/1000/bus,target=/run/user/1000/bus \
# spotify-dbus-controller

#sudo docker logs -f $ID


# --volume /sys/fs/cgroup:/sys/fs/cgroup:ro \
# --volume /run/user/1000/bus:/run/user/1000/bus \
# --env DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" \
#--volume /var/run/dbus:/var/run/dbus \
#--volume /run/dbus/system_bus_socket:/run/dbus/system_bus_socket \
