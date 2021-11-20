# PowerPoint Interactive Games Generator
> Generates Drag-And-Drop and Typing Prompt Games from Placeholder Textboxes

## Local Generation via Docker Server

1. Build the Docker Image `./dockerBuild.sh`
2. Edit `./dockerBuild.sh` with correct absolute path of config.json
3. Run `./dockerRun.sh`
4. Open `http://localhost:17393/local`

## Image and HTML Hosted Generation

1. Run `python3 01_prepare_powerpoint.py input.pptx config.json`
2. Export input.pptx as JPEGS
3. Run `python3 02_upload_and_generate_powerpoint.py input-Blank.pptx config.json`

### Result

![](https://39363.org/IMAGE_BUCKET/1636526211492-992772358.png)

- https://39363.org/CDN/MISC/ExampleDragAndDrop.html
- https://39363.org/CDN/MISC/ExampleTyping.html

### Todo

- add back button
- auto adjust image scale percentage based on viewport size
- adjust bootstrap columns for drag and drop based on length of longest word
- auto generate blank slides
- fix accidental double drop on correct answer overcount