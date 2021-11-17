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
		- it is easy to accidentally move a text box when deleting the text for the second slide in each question

	- Example of Slide 1 and Slide 2 for "Question 1"

<img src="https://39363.org/IMAGE_BUCKET/1636525166177-241760869.png" style="zoom:27%;" />

2. Export All Slides as JPEG
3. `cp config_example.json config.json`
4. Fill out config.json
5. run `python3 main.py "./examples/Quiz 5.pptx" config.json`
6. Upload Generated HTML files to File Server

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
- wrap into docker server , upload zip of .pptx and images , download zip of html files
- add "any position" for generic list