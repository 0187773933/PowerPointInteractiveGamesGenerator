#!/usr/bin/env python3
import sys
from pathlib import Path
from pprint import pprint

import utils
import image_uploader
import compute_image_maps
import interactive_notes_generator

if __name__ == "__main__":
	input_powerpoint_path = Path( sys.argv[ 1 ] )
	config = utils.read_json( sys.argv[ 2 ] )
	blank_powerpoint_path = input_powerpoint_path.parent.joinpath( f"{input_powerpoint_path.stem}-Blank.pptx" )
	slide_image_paths = utils.get_slide_image_paths( str( blank_powerpoint_path ) )
	if len( slide_image_paths ) < 1:
		print( blank_powerpoint_path )
		print( "You didn't export blank slides as jpegs" )
		sys.exit( 1 )
	print( len( slide_image_paths ) )

	# 1.) Compute HTML Image Map Locations
	image_maps_in_slides = compute_image_maps.compute( sys.argv[ 1 ] , config[ "parser" ] )
	print( len( image_maps_in_slides ) )

	if len( slide_image_paths ) != len( image_maps_in_slides ):
		print( "Lengths of Slide Images and Slide Image Maps Don't Match" )
		# print( "This could mean some slides don't have any thing but" )
		sys.exit( 1 )

	image_objects = []
	for slide_index , image_maps_in_slide in enumerate( image_maps_in_slides ):
		print( f"\nSlide === {slide_index+1}" )

		# 1.) Upload to Image Hosting Location
		uploaded_url = image_uploader.upload( str( slide_image_paths[ slide_index ].absolute() ) , config[ "image_upload_server" ] )

		image_objects.append([
			f"Slide" ,
			uploaded_url ,
			image_maps_in_slide
		])

	# 3.) Generate Interactive Games
	html_output_base_dir = input_powerpoint_path.parent.joinpath( f"{input_powerpoint_path.stem} - Interactive" )
	html_options = config[ "html" ]
	html_options[ "title" ] = input_powerpoint_path.stem.replace( " " , "-" )
	html_options[ "images" ] = image_objects
	html_options[ "output_base_dir" ] = html_output_base_dir
	interactive_notes_generator.generate( html_options )

	# 4.) Save Config File Used
	json_save = {
		"config": config ,
		"html_options": html_options
	}
	json_save[ "html_options" ][ "output_base_dir" ] = str( json_save[ "html_options" ][ "output_base_dir" ] )
	utils.write_json( html_output_base_dir.joinpath( "config.json" ) , json_save )