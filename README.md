# PowerPoint Interactive Games Generator

- The background color for placeholder rectangles must match the hex string in config.json
- Every slide to be generated needs to be in a pair ( SlideWithTextBoxesFilled , SlideWithBlankTextBoxes )
- Example Image Upload Server: https://github.com/0187773933/ImageUploadServer

1. Create Some PowerPoint modeled after one of the examples
2. `cp config_example.json config.json`
3. Fill out config.json
4. run `python3 main.py "./examples/Quiz 5.pptx" config.json`
5. Upload Generated HTML files to File Server