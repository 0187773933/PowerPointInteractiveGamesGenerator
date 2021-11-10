# PowerPoint Interactive Games Generator
> Generates Drag-And-Drop and Typing Prompt Games from Placeholder Textboxes

- Example Image Upload Server: https://github.com/0187773933/ImageUploadServer

1. Create PowerPoint of slides

	- For each question, there needs to be 2 separate slides

	- 1st Slide = Normal one with text inside textboxes

	- 2nd Slide = Exact duplicate of the 1st , only text is removed

		> `Windows Key + "D"` or `Mac Key + "D"` to duplicate slides

	- Caveats :

		- The hex "fill color" of the textboxes must match that in config

	- Example of Slide 1 and Slide 2 for "Question 1"

<img src="https://39363.org/IMAGE_BUCKET/1636525166177-241760869.png" style="zoom:37%;" />

2. Export All Slides as JPEG
3. `cp config_example.json config.json`
4. Fill out config.json
5. run `python3 main.py "./examples/Quiz 5.pptx" config.json`
6. Upload Generated HTML files to File Server

### Todo

- add back button
- auto adjust image scale percentage based on viewport size
- adjust bootstrap columns for drag and drop based on length of longest word
- auto generate blank slides