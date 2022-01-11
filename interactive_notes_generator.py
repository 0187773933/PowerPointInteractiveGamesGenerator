#!/usr/bin/env python3
import sys
from pprint import pprint
from pathlib import Path
import shutil
import json
import base64

def write_json( file_path , python_object ):
	with open( file_path , 'w', encoding='utf-8' ) as f:
		json.dump( python_object , f , ensure_ascii=False , indent=4 )

def read_json( file_path ):
	with open( file_path ) as f:
		return json.load( f )

def write_text( file_path , text_lines_list ):
	#with open( file_path , 'a', encoding='utf-8' ) as f:
	with open( file_path , 'w', encoding='utf-8' ) as f:
		f.writelines( text_lines_list )

def read_text( file_path ):
	with open( file_path ) as f:
		return f.read().splitlines()

# JQUERY_UI_CSS_INTEGRITY = "sha256-RPilbUJ5F7X6DdeTO6VFZ5vl5rO5MJnmSk4pwhWfV8A="
# JQUERY_JS_INTEGRITY = "sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4="
# BOOTSTRAP_CSS_INTEGRITY = "sha384-KyZXEAg3QhqLMpG8r+8fhAXLRk2vvoC2f3B09zVXn8CA5QIVfZOJ3BCsw2P0p/We"
# BOOTSTRAP_JS_INTEGRITY = "sha384-U1DAWAznBHeqEIlVSCgzq+c9gqGAJn5c/t99JyeKa9xxaYpSvHU5awsuZVVFIhvj"
# JQUERY_UI_JS_INTEGRITY = "sha256-VazP97ZCwtekAsvgPBSUwPFKdrwD3unUfSGVYrahUqU="
JQUERY_UI_CSS_INTEGRITY = ""
JQUERY_JS_INTEGRITY = ""
BOOTSTRAP_CSS_INTEGRITY = ""
BOOTSTRAP_JS_INTEGRITY = ""
JQUERY_UI_JS_INTEGRITY = ""

def build_drag_and_drop_html( options ):
	return f'''<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>{options["title"]}</title>
	<link rel="stylesheet" href="{options["cdn"]["jquery_ui_css"]["url"]}" integrity="{options["cdn"]["jquery_ui_css"]["integrity"]}" >
	<script src="{options["cdn"]["jquery_js"]["url"]}" integrity="{options["cdn"]["jquery_js"]["integrity"]}"></script>
	<link rel="stylesheet" href="{options["cdn"]["bootstrap_css"]["url"]}" integrity="{options["cdn"]["bootstrap_css"]["integrity"]}">
	<script src="{options["cdn"]["bootstrap_bundle"]["url"]}" integrity="{options["cdn"]["bootstrap_bundle"]["integrity"]}"></script>
	<script src="{options["cdn"]["jquery_ui_js"]["url"]}" integrity="{options["cdn"]["jquery_ui_js"]["integrity"]}" ></script>
</head>
<body>
	<div id="label-container">
		{options["image_map"]}
	</div>
	<div class="container">
		<div class="row justify-content-start">
			<div class="col-2">
				<div id="draggable-label-container"></div>
			</div>
			<div class="col-10">
				<canvas id="interactive-image-canvas"></canvas>
			</div>
		</div>
	</div>
	<script type="text/javascript">
		function load() {{ start_interactive_drag_and_drop(); }}
		window.image_source_url = "{options["image_source_url"]}";
		window.next_challenge_url = "{options["next_challenge_url"]}";
		window.image_scale_percentage = {options["image_scale_percentage"]};
		window.unanswered_color = "{options["unanswered_color"]}";
		window.answered_color = "{options["answered_color"]}";
		window.text_color = "{options["text_color"]}";
		window.text_font = "{options["text_font"]}";
		window.text_x_offset_factor = {options["text_x_offset_factor"]};
		window.text_y_offset_factor = {options["text_y_offset_factor"]};
		window.any_position = {str( options["any_position"] ).lower()};
		window.randomize_order = {str( options["randomize_order"] ).lower()};
		window.auto_advance = {str( options["auto_advance"] ).lower()};
		let interactive_drag_and_drop_script = document.createElement( "script" );
		interactive_drag_and_drop_script.setAttribute( "src" , "{options["cdn"]["interactive_drag_and_drop_js"]}?v=" + ( new Date() ).getTime() );
		interactive_drag_and_drop_script.onload = load;
		document.head.appendChild( interactive_drag_and_drop_script );
	</script>
</body>
</html>'''

def build_typing_html( options ):
	return f'''<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>{options["title"]}</title>
	<link rel="stylesheet" href="{options["cdn"]["jquery_ui_css"]["url"]}" integrity="{options["cdn"]["jquery_ui_css"]["integrity"]}" >
	<script src="{options["cdn"]["jquery_js"]["url"]}" integrity="{options["cdn"]["jquery_js"]["integrity"]}"></script>
	<link rel="stylesheet" href="{options["cdn"]["bootstrap_css"]["url"]}" integrity="{options["cdn"]["bootstrap_css"]["integrity"]}">
	<script src="{options["cdn"]["bootstrap_bundle"]["url"]}" integrity="{options["cdn"]["bootstrap_bundle"]["integrity"]}"></script>
	<script src="{options["cdn"]["jquery_ui_js"]["url"]}" integrity="{options["cdn"]["jquery_ui_js"]["integrity"]}" ></script>
</head>
<body>
	<div id="label-container">
		{options["image_map"]}
	</div>
	<div>
		<center><canvas id="interactive-image-canvas"></canvas></center>
	</div>
	</br>
	<div class="container">
		<div class="row justify-content-center">
			<div class="col-2"></div>
			<div class="col-8">
				<div class="input-group">
					<span class="input-group-text" id="bootstrap-answer-companion">Answer</span>
					<input autofocus id="input-answer" type="text" class="form-control" aria-label="Sizing example input" aria-describedby="bootstrap-answer-companion">
					<button class="btn btn-outline-secondary" type="button" id="hint-button">Hint</button>
				</div>
			</div>
			<div class="col-2"></div>
		</div>
		</br>
		<div class="row justify-content-center">
			<div class="col-2"></div>
			<div class="col-8">
				<p id="hint-area" class="text-center"></p>
			</div>
			<div class="col-2"></div>
		</div>
	</div>
	<script type="text/javascript">
		function load() {{ start_interactive_typing(); }}
		window.image_source_url = "{options["image_source_url"]}";
		window.next_challenge_url = "{options["next_challenge_url"]}";
		window.image_scale_percentage = {options["image_scale_percentage"]};
		window.unanswered_color = "{options["unanswered_color"]}";
		window.answered_color = "{options["answered_color"]}";
		window.text_color = "{options["text_color"]}";
		window.text_font = "{options["text_font"]}";
		window.text_x_offset_factor = {options["text_x_offset_factor"]};
		window.text_y_offset_factor = {options["text_y_offset_factor"]};
		window.any_position = {str( options["any_position"] ).lower()};
		window.randomize_order = {str( options["randomize_order"] ).lower()};
		window.auto_advance = {str( options["auto_advance"] ).lower()};
		let interactive_typing_script = document.createElement( "script" );
		interactive_typing_script.setAttribute( "src" , "{options["cdn"]["interactive_typing_js"]}?v=" + ( new Date() ).getTime() );
		interactive_typing_script.onload = load;
		document.head.appendChild( interactive_typing_script );
	</script>
</body>
</html>'''

def generate( config , append_title=True ):
	if "images" not in config:
		sys.exit( 1 )
	if "any_position" not in config:
		config[ "any_position" ] = False
	if "randomize_order" not in config:
		config[ "randomize_order" ] = True
	if "auto_advance" not in config:
		config[ "auto_advance" ] = True
	pprint( config )

	# input_config_path = Path( sys.argv[1] )
	output_base_dir =  config[ "output_base_dir" ]
	try:
		shutil.rmtree(  config[ "output_base_dir" ] )
	except Exception as e:
		pass
	cached_title = config["title"] # no idea , somehow somebody changes it
	config[ "output_base_dir" ].mkdir( parents=True , exist_ok=True )
	if append_title:
		drag_and_drop_base_dir = config[ "output_base_dir" ].joinpath( "DragAndDrop" , config["title"] )
		typing_base_dir = config[ "output_base_dir" ].joinpath( "Typing" , config["title"] )
	else:
		drag_and_drop_base_dir = config[ "output_base_dir" ].joinpath( "DragAndDrop" )
		typing_base_dir = config[ "output_base_dir" ].joinpath( "Typing" )
	drag_and_drop_base_dir.mkdir( parents=True , exist_ok=True )
	typing_base_dir.mkdir( parents=True , exist_ok=True )
	# print( config[ "output_base_dir" ].absolute() )


	names = [ x[0] for x in config["images"] ]
	next_names = []
	next_indexes = []
	for index , value in enumerate( names ):
		next_names.append(  names[ index ] )
		next_indexes.append( index )
	next_names.append( names[ 0 ] )
	next_names = next_names[ 1: ]
	next_indexes.append( next_indexes[ 0 ] )
	next_indexes = next_indexes[ 1: ]
	# print( names )
	# print( next_names )
	total_images = len( config["images"] )
	for index , question in enumerate( config["images"] ):
		# write_text( file_path , text_lines_list )
		index_prefix = str( index + 1 ).zfill( 3 )
		next_index_prefix = str( next_indexes[ index ] + 1 ).zfill( 3 )
		next_index = 0

		image_source_url = question[ 1 ]
		#image_map = base64.b64decode( question[ 2 ] ).decode( "utf-8" )
		# image_map_raw = base64.b64decode( question[ 2 ] ).decode( "utf-8" ).split( "\n" )
		# image_map = [ image_map_raw[ 0 ] , ...[ f"\t\t\t{x}" for x in image_map_raw[ 1:-2 ] ] , f"\t\t{image_map_raw[-1]}" ]
		# image_map = "\n".join( image_map )

		# Default
		if append_title:
			next_challenge_drag_and_drop_url = f'{config["base_hosted_url"]}/DragAndDrop/{cached_title}/{next_index_prefix}.html'
			next_challenge_typing_url = f'{config["base_hosted_url"]}/Typing/{cached_title}/{next_index_prefix}.html'
		else:
			next_challenge_drag_and_drop_url = f'{config["base_hosted_url"]}{next_index_prefix}.html'
			next_challenge_typing_url = f'{config["base_hosted_url"]}{next_index_prefix}.html'

		# Adhoc , because nested
		# next_challenge_drag_and_drop_url = f'{config["base_hosted_url"]}/DragAndDrop/006-Muscles/{cached_title}/{next_index_prefix}.html'
		# next_challenge_typing_url = f'{config["base_hosted_url"]}/Typing/006-Muscles/{cached_title}/{next_index_prefix}.html'

		# print( next_challenge_drag_and_drop_url )
		options = config
		options[ "title" ] = index_prefix
		options[ "image_map" ] = question[ 2 ]
		options[ "image_source_url" ] = question[ 1 ]
		options[ "next_challenge_url" ] = next_challenge_drag_and_drop_url

		# drag_and_drop_output_path = drag_and_drop_base_dir.joinpath( f"{index_prefix}-{names[index]}.html" )
		drag_and_drop_output_path = drag_and_drop_base_dir.joinpath( f"{index_prefix}.html" )
		drag_and_drop_html = build_drag_and_drop_html( options )
		write_text( str( drag_and_drop_output_path ) , [ drag_and_drop_html ] )

		options[ "next_challenge_url" ] = next_challenge_typing_url
		typing_html = build_typing_html( options )
		# typing_output_path = typing_base_dir.joinpath( f"{index_prefix}-{names[index]}.html" )
		typing_output_path = typing_base_dir.joinpath( f"{index_prefix}.html" )
		write_text( str( typing_output_path ) , [ typing_html ] )
