#!/bin/bash
# sudo docker buildx build -m 8g --platform linux/arm/v6 -t xp6qhg9fmuolztbd2ixwdbtd1/raspi-motion-tracker-frame-consumer:arm32 --push .
# --platform linux/amd64,linux/arm64,linux/arm/v7,linux/arm/v6
#sudo docker buildx build -t ppt-interactive-generator-server:latest --push .
sudo docker push xp6qhg9fmuolztbd2ixwdbtd1/ppt-interactive-generator-server
