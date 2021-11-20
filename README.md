# PowerPoint Interactive Games Generator
> Generates Drag-And-Drop and Typing Prompt Games from Placeholder Textboxes

## Local Generation - Docker Hub
- https://hub.docker.com/r/xp6qhg9fmuolztbd2ixwdbtd1/ppt-interactive-generator-server
- `sudo docker pull xp6qhg9fmuolztbd2ixwdbtd1/ppt-interactive-generator-server`
- Run `sudo docker rm "public-ppt-interactive-generator-server" -f || echo "failed to remove existing server" && \
sudo docker run -dit --restart="always" --name "public-ppt-interactive-generator-server" \
--mount type=bind,source=/home/morphs/DOCKER_IMAGES/PowerPointInteractiveGameGenerator/config.json,target=/home/config.json \
-p 17393:9379 xp6qhg9fmuolztbd2ixwdbtd1/ppt-interactive-generator-server config.json`

## Local Generation - Build Docker Server

1. Build the Docker Image `./dockerBuild.sh`
2. Edit `./dockerBuild.sh` with correct absolute path of config.json
3. Run `./dockerRun.sh`
4. Open http://localhost:17393/local

## Image and HTML Hosted Generation

1. Run `python3 01_prepare_powerpoint.py input.pptx config.json`
2. Export input.pptx as JPEGS
4. Run `python3 02_upload_and_generate_powerpoint.py input-Blank.pptx config.json`

### Result

![](https://39363.org/IMAGE_BUCKET/1636526211492-992772358.png)

- https://39363.org/CDN/MISC/ExampleDragAndDrop.html
- https://39363.org/CDN/MISC/ExampleTyping.html
- In Typing Mode :
	- `Control` = Show Hint
	- `Control + Z` = Auto Enter Current Label

### Todo

- add back button
- auto adjust image scale percentage based on viewport size
- adjust bootstrap columns for drag and drop based on length of longest word
- fix accidental double drop on correct answer overcount