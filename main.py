#!/usr/bin/env python3
import sys
from pathlib import Path
from pprint import pprint
import utils
import compute_image_maps
import image_uploader
import interactive_notes_generator

if __name__ == "__main__":

	input_powerpoint_path = Path( sys.argv[ 1 ] )
	config = utils.read_json( sys.argv[ 2 ] )
	slide_image_paths = utils.get_slide_image_paths( sys.argv[ 1 ] )

	# 1.) Compute HTML Image Map Locations
	image_maps_in_slides = compute_image_maps.compute( sys.argv[ 1 ] , config[ "parser" ] )

	# 2.) Interact with Every Blank Slide ( should be every-other-one )
	image_objects = []
	for slide_index , image_maps_in_slide in utils.enumerate2( image_maps_in_slides , 1 , 2 ):
		if slide_index > len( image_maps_in_slides ):
			continue
		print( f"\nSlide === {slide_index+1}" )

		# 1.) Upload to Image Hosting Location
		uploaded_url = image_uploader.upload( str( slide_image_paths[ slide_index ].absolute() ) , config[ "image_upload_server" ] )
		print( uploaded_url )

		image_objects.append([
			f"Slide - {str( slide_index ).zfill( 3 )}" ,
			uploaded_url ,
			image_maps_in_slide
		])

	# 3.) Generate Interactive Games
	html_options = {
		"title": input_powerpoint_path.stem ,
		"images": image_objects ,
		"output_base_dir": input_powerpoint_path.parent.joinpath( f"{input_powerpoint_path.stem} - Interactive" ) ,
	}
	html_options.update( config[ "html" ] )
	interactive_notes_generator.generate( html_options )