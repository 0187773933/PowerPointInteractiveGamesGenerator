# PowerPoint Interactive Games Generator

### Generates DragAndDrop and Typing Prompt Games from Placeholder Textboxes

- The background color for placeholder rectangles must match the hex string in config.json
- Every slide to be generated needs to be in a pair ( SlideWithTextBoxesFilled , SlideWithBlankTextBoxes )
- Example Image Upload Server: https://github.com/0187773933/ImageUploadServer

1. Create Some PowerPoint modeled after one of the examples
2. Export Slides as JPEG
3. `cp config_example.json config.json`
4. Fill out config.json
5. run `python3 main.py "./examples/Quiz 5.pptx" config.json`
6. Upload Generated HTML files to File Server


### Todo
- add back button
- auto adjust image scale percentage based on viewport size
- adjust bootstrap columns for drag and drop based on length of longest word