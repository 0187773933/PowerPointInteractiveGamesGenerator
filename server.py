#!/usr/bin/env python3
import sys
import uuid
import base64
from pathlib import Path
from pprint import pprint
from datetime import timedelta
import tempfile
import zipfile
import shutil
import requests

from sanic import Sanic
from sanic.response import html as sanic_html
from sanic.response import json as sanic_json
from sanic.response import file as sanic_file
from sanic.request import Request

from sanic_jwt_extended import JWT , jwt_required
from sanic_jwt_extended.tokens import Token

import utils
import compute_image_maps
import image_uploader
import interactive_notes_generator

from pptx import Presentation
from copy import deepcopy

DEFAULT_CONFIG = utils.read_json( sys.argv[1] )

def upload_file_to_imgur( file_path ):
	try:
		response = requests.post(
			"https://api.imgur.com/3/upload.json" ,
			headers={ "Authorization": f"Client-ID {DEFAULT_CONFIG[ 'image_upload_server_imgur_version' ][ 'imgur_client_id' ]}" } ,
			data={
				"image": base64.b64encode( open( str( file_path ) , "rb" ).read() ) ,
				"type": "base64" ,
				"name": file_path.stem ,
			}
		)
		response.raise_for_status()
		data = response.json()
		# pprint( data )
		if "data" not in data:
			return False
		if "link" not in data["data"]:
			return False
		return data["data"]["link"]
	except Exception as e:
		print( e )
		return False

app = Sanic( __name__ )

# https://sanic-jwt-extended.seonghyeon.dev/config_options.html
# https://pyjwt.readthedocs.io/en/latest/algorithms.html
with JWT.initialize( app ) as manager:
	manager.config.secret_key = DEFAULT_CONFIG[ "image_upload_server_imgur_version" ][ "sanic_secret_key" ]
	manager.config.public_key = DEFAULT_CONFIG[ "image_upload_server_imgur_version" ][ "sanic_public_key" ]
	manager.config.private_key = DEFAULT_CONFIG[ "image_upload_server_imgur_version" ][ "sanic_private_key" ]
	manager.config.algorithm = "HS512"
	manager.config.jwt_header_key = "token"
	manager.config.jwt_header_prefix = "Bearer"
	manager.config.jwt_cookie = "ppt_interactive_image_upload_server"
	manager.config.access_token_expires = timedelta( weeks=( 52 * 10 ) )

# https://sanic-jwt-extended.seonghyeon.dev/api_docs/jwt.html#class-sanic_jwtextendedjwt
@app.route( "/login" , methods=[ "POST" ] )
async def login( request: Request ):
	username = request.json.get( "username" , "user" )
	access_token = JWT.create_access_token( identity=username )
	return sanic_json( dict( token=access_token ) , status=200 )

# https://sanic-jwt-extended.seonghyeon.dev/usage/basic.html#use-token-object
# https://github.com/NovemberOscar/Sanic-JWT-Extended/blob/0eb9282a4c21f6d9a81c3d3c2a4818353b79b429/sanic_jwt_extended/decorators.py#L11
@app.route( "/protected" , methods=[ "GET" ] )
@jwt_required
async def protected( request: Request , token: Token ):
	print( "accessed protected route" )
	return sanic_json( dict( identity=token.identity , type=token.type , raw_data=token.raw_data , exp=str( token.exp ) ) )

INPUT_FORM = f'''<!DOCTYPE html>
<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>PowerPoint - Interactive Game Generator</title>
</head>
<body>
	<h1>PowerPoint Interactive Game Generator</h1>
	<ol>
		<li>Create PowerPoint Matching Style Expained <a href="https://github.com/0187773933/PowerPointInteractiveGamesGenerator" target="_blank">Here</a></li>
		<li>Export PowerPoint Slides as JPEG</li>
		<li>Create ZIP Archive Containing the Original PowerPoint and Folder of Exported Slide Images</li>
		<li>Upload ZIP Here</li>
	</ol>
	<form enctype="multipart/form-data" action="/upload-file" method="POST">
		<input type="file" id="powerpoint" name="file"><br><br>
		<span>Textbox Background Color (Hex)</span>&nbsp&nbsp<input type="text" id="background_color" name="background_color" placeholder="0070C0"><br>
		<span>Exported Slide Image Width</span>&nbsp&nbsp<input type="text" id="exported_width" name="exported_width" placeholder="1920"><br>
		<span>Exported Slide Image Height</span>&nbsp&nbsp<input type="text" id="exported_height" name="exported_height" placeholder="1080"><br>
		<span>Exported Slide Image DPI</span>&nbsp&nbsp<input type="text" id="exported_image_dpi" name="exported_image_dpi" placeholder="144"><br>
		<span>Scale Percentage of Image</span>&nbsp&nbsp<input type="text" id="image_scale_percentage" name="image_scale_percentage" placeholder="60"><br>
		<span>Unanswered Color Outline</span>&nbsp&nbsp<input type="text" id="unanswered_color" name="unanswered_color" placeholder="red"><br>
		<span>Answered Color Outline</span>&nbsp&nbsp<input type="text" id="answered_color" name="answered_color" placeholder="#13E337"><br>
		<span>Typing Text Color</span>&nbsp&nbsp<input type="text" id="text_color" name="text_color" placeholder="white"><br>
		<span>Typing Text Font</span>&nbsp&nbsp<input type="text" id="text_font" name="text_font" placeholder="17px Arial"><br>
		<span>Typing Text X-Offset</span>&nbsp&nbsp<input type="text" id="text_x_offset_factor" name="text_x_offset_factor" placeholder="2"><br>
		<span>Typing Text Y-Offset</span>&nbsp&nbsp<input type="text" id="text_y_offset_factor" name="text_y_offset_factor" placeholder="3"><br>
		<span>Base URL of Hosted HTML</span>&nbsp&nbsp<input type="text" size="60" id="base_hosted_url" name="base_hosted_url" placeholder="https://39363.org/NOTES/WSU/2021/Fall/ANT3100/Interactive"><br>
		<span>CDN of Interactive Typing JS</span>&nbsp&nbsp<input type="text" size="60" id="interactive_typing_js" name="interactive_typing_js" placeholder="https://39363.org/CDN/NOTES/interactive_typing.js"><br>
		<span>CDN of Interactive DragAndDrop JS</span>&nbsp&nbsp<input type="text" size="60" id="interactive_drag_and_drop_js" name="interactive_drag_and_drop_js" placeholder="https://39363.org/CDN/NOTES/interactive_drag_and_drop.js"><br>
		<span>CDN of JQuery-UI CSS</span>&nbsp&nbsp<input type="text" size="60" id="jquery_ui_css" name="jquery_ui_css" placeholder="https://39363.org/CDN/jquery-ui.css"><br>
		<span>CDN of JQuery-UI JS</span>&nbsp&nbsp<input type="text" size="60" id="jquery_ui_js" name="jquery_ui_js" placeholder="https://39363.org/CDN/jquery-ui.min.js"><br>
		<span>CDN of JQuery JS</span>&nbsp&nbsp<input type="text" size="60" id="jquery_js" name="jquery_js" placeholder="https://39363.org/CDN/jquery-3.6.0.min.js"><br>
		<span>CDN of Bootstrap CSS</span>&nbsp&nbsp<input type="text" size="60" id="bootstrap_css" name="bootstrap_css" placeholder="https://39363.org/CDN/bootstrap.min.css"><br>
		<span>CDN of Bootstrap Bundle JS</span>&nbsp&nbsp<input type="text" size="60" id="bootstrap_bundle" name="bootstrap_bundle" placeholder="https://39363.org/CDN/bootstrap.bundle.min.js"><br>
		<br>
		<input type="submit">
	</form>
</body>
</html>'''

@app.route( "/" , methods=[ "GET" ] )
# @jwt_required
async def upload( request: Request ):
	return sanic_html( INPUT_FORM )

def get_updated_config( request ):
	config = DEFAULT_CONFIG

	background_color = request.form.get( "background_color" )
	if len( background_color ) > 0:
		config[ "parser" ][ "our_background_textbox_hex" ] = background_color
	exported_width = request.form.get( "exported_width" )
	if len( exported_width ) > 0:
		config[ "parser" ][ "exported_width" ] = int( exported_width )
	exported_height = request.form.get( "exported_height" )
	if len( exported_height ) > 0:
		config[ "parser" ][ "exported_height" ] = int( background_color )
	exported_image_dpi = request.form.get( "exported_image_dpi" )
	if len( exported_image_dpi ) > 0:
		config[ "parser" ][ "exported_image_dpi" ] = int( exported_image_dpi )

	image_scale_percentage = request.form.get( "image_scale_percentage" )
	if len( image_scale_percentage ) > 0:
		config[ "html" ][ "image_scale_percentage" ] = int( image_scale_percentage )
	unanswered_color = request.form.get( "unanswered_color" )
	if len( unanswered_color ) > 0:
		config[ "html" ][ "unanswered_color" ] = unanswered_color
	answered_color = request.form.get( "answered_color" )
	if len( answered_color ) > 0:
		config[ "html" ][ "answered_color" ] = answered_color
	text_color = request.form.get( "text_color" )
	if len( text_color ) > 0:
		config[ "html" ][ "text_color" ] = text_color
	text_font = request.form.get( "text_font" )
	if len( text_font ) > 0:
		config[ "html" ][ "text_font" ] = text_font
	text_x_offset_factor = request.form.get( "text_x_offset_factor" )
	if len( text_x_offset_factor ) > 0:
		config[ "html" ][ "text_x_offset_factor" ] = int( text_x_offset_factor )
	text_y_offset_factor = request.form.get( "text_y_offset_factor" )
	if len( text_y_offset_factor ) > 0:
		config[ "html" ][ "text_y_offset_factor" ] = int( text_y_offset_factor )

	base_hosted_url = request.form.get( "base_hosted_url" )
	if len( base_hosted_url ) > 0:
		config[ "html" ][ "base_hosted_url" ] = base_hosted_url

	interactive_typing_js = request.form.get( "interactive_typing_js" )
	if len( interactive_typing_js ) > 0:
		config[ "html" ][ "cdn" ][ "interactive_typing_js" ] = interactive_typing_js

	interactive_drag_and_drop_js = request.form.get( "interactive_drag_and_drop_js" )
	if len( interactive_drag_and_drop_js ) > 0:
		config[ "html" ][ "cdn" ][ "interactive_drag_and_drop_js" ][ "url" ] = interactive_drag_and_drop_js

	jquery_ui_css = request.form.get( "jquery_ui_css" )
	if len( jquery_ui_css ) > 0:
		config[ "html" ][ "cdn" ][ "jquery_ui_css" ][ "url" ] = jquery_ui_css

	jquery_ui_js = request.form.get( "jquery_ui_js" )
	if len( jquery_ui_js ) > 0:
		config[ "html" ][ "cdn" ][ "jquery_ui_js" ][ "url" ] = jquery_ui_js

	jquery_js = request.form.get( "jquery_js" )
	if len( jquery_js ) > 0:
		config[ "html" ][ "cdn" ][ "jquery_js" ][ "url" ] = jquery_js

	bootstrap_css = request.form.get( "bootstrap_css" )
	if len( bootstrap_css ) > 0:
		config[ "html" ][ "cdn" ][ "bootstrap_css" ][ "url" ] = bootstrap_css

	bootstrap_bundle = request.form.get( "bootstrap_bundle" )
	if len( bootstrap_bundle ) > 0:
		config[ "html" ][ "cdn" ][ "bootstrap_bundle" ][ "url" ] = bootstrap_bundle

	return config



@app.route( "/local" , methods=[ "GET" ] )
async def upload( request: Request ):
	return sanic_html( f'''<!DOCTYPE html>
<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>PowerPoint - Interactive Game Generator</title>
</head>
<body>
	<h1>PowerPoint Interactive Local Game Generator - Stage 1</h1>
	<h3>Instructions for Stage 1 </h3>
	<ol>
		<li>Create a PowerPoint with TextBoxes that have all been filled with the same predetermined hex color</li>
		<li>Upload that .pptx file here</li>
		<li>Download Generated .pttx file that contain slides with the text removed</li>
		<li><a href="/local/stage/2">Go to Stage 2</a></li>
	</ol>
	<form enctype="multipart/form-data" action="/local/stage/1" method="POST">
		<input type="file" id="powerpoint" name="file"><br><br>
		<span>Textbox Background Color (Hex)</span>&nbsp&nbsp<input type="text" id="background_color" name="background_color" placeholder="0070C0"><br>
		<span>Exported Slide Image Width</span>&nbsp&nbsp<input type="text" id="exported_width" name="exported_width" placeholder="1920"><br>
		<span>Exported Slide Image Height</span>&nbsp&nbsp<input type="text" id="exported_height" name="exported_height" placeholder="1080"><br>
		<span>Exported Slide Image DPI</span>&nbsp&nbsp<input type="text" id="exported_image_dpi" name="exported_image_dpi" placeholder="144"><br>
		<span>Scale Percentage of Image</span>&nbsp&nbsp<input type="text" id="image_scale_percentage" name="image_scale_percentage" placeholder="60"><br>
		<span>Unanswered Color Outline</span>&nbsp&nbsp<input type="text" id="unanswered_color" name="unanswered_color" placeholder="red"><br>
		<span>Answered Color Outline</span>&nbsp&nbsp<input type="text" id="answered_color" name="answered_color" placeholder="#13E337"><br>
		<span>Typing Text Color</span>&nbsp&nbsp<input type="text" id="text_color" name="text_color" placeholder="white"><br>
		<span>Typing Text Font</span>&nbsp&nbsp<input type="text" id="text_font" name="text_font" placeholder="17px Arial"><br>
		<span>Typing Text X-Offset</span>&nbsp&nbsp<input type="text" id="text_x_offset_factor" name="text_x_offset_factor" placeholder="2"><br>
		<span>Typing Text Y-Offset</span>&nbsp&nbsp<input type="text" id="text_y_offset_factor" name="text_y_offset_factor" placeholder="3"><br>
		<span>Base URL of Hosted HTML</span>&nbsp&nbsp<input type="text" size="60" id="base_hosted_url" name="base_hosted_url" placeholder="https://39363.org/NOTES/WSU/2021/Fall/ANT3100/Interactive"><br>
		<span>CDN of Interactive Typing JS</span>&nbsp&nbsp<input type="text" size="60" id="interactive_typing_js" name="interactive_typing_js" placeholder="https://39363.org/CDN/NOTES/interactive_typing.js"><br>
		<span>CDN of Interactive DragAndDrop JS</span>&nbsp&nbsp<input type="text" size="60" id="interactive_drag_and_drop_js" name="interactive_drag_and_drop_js" placeholder="https://39363.org/CDN/NOTES/interactive_drag_and_drop.js"><br>
		<span>CDN of JQuery-UI CSS</span>&nbsp&nbsp<input type="text" size="60" id="jquery_ui_css" name="jquery_ui_css" placeholder="https://39363.org/CDN/jquery-ui.css"><br>
		<span>CDN of JQuery-UI JS</span>&nbsp&nbsp<input type="text" size="60" id="jquery_ui_js" name="jquery_ui_js" placeholder="https://39363.org/CDN/jquery-ui.min.js"><br>
		<span>CDN of JQuery JS</span>&nbsp&nbsp<input type="text" size="60" id="jquery_js" name="jquery_js" placeholder="https://39363.org/CDN/jquery-3.6.0.min.js"><br>
		<span>CDN of Bootstrap CSS</span>&nbsp&nbsp<input type="text" size="60" id="bootstrap_css" name="bootstrap_css" placeholder="https://39363.org/CDN/bootstrap.min.css"><br>
		<span>CDN of Bootstrap Bundle JS</span>&nbsp&nbsp<input type="text" size="60" id="bootstrap_bundle" name="bootstrap_bundle" placeholder="https://39363.org/CDN/bootstrap.bundle.min.js"><br>
		<br>
		<input type="submit">
	</form>
</body>
</html>''')

# https://stackoverflow.com/questions/4212861/what-is-a-correct-mime-type-for-docx-pptx-etc
@app.route( "/local/stage/1" , methods=[ "POST" ] )
async def generate_local_stage_one( request: Request ):
	try:

		config = get_updated_config( request )

		input_file = request.files.get( "file" )
		input_file_type = input_file.type
		input_file_name = input_file.name
		input_file_data = input_file.body
		if input_file_name.endswith( ".pptx" ) == False:
			return sanic_json( dict( failed="no .pttx file sent" ) , status=200 )
		input_file_name_stem = input_file_name.split( ".pptx" )[ 0 ]
		print( input_file_type , input_file_name )

		with tempfile.TemporaryDirectory() as temp_dir:

			temp_dir_posix = Path( temp_dir )
			input_file_path = temp_dir_posix.joinpath( input_file_name )
			output_powerpoint_path = temp_dir_posix.joinpath( f"{input_file_name_stem}-Blank.pptx" )

			# 1.) Read Sent Bytes into .pptx file inside temp directory
			with open( str( input_file_path ) , "wb"  ) as file:
				file.write( input_file_data )
			print( input_file_path )
			print( input_file_path.stat() )

			# 2.) Create Copy of PowerPoint With All text removed from boxes with correct fill color
			p = Presentation( input_file_path )
			p_clone = deepcopy( p )
			for slide_index , slide in enumerate( p_clone.slides ):
				for shape_index , shape in enumerate( slide.shapes ):
					if utils.validate_text_box( shape , config[ "parser" ][ "our_background_textbox_hex" ] ):
						print( f"{slide_index} === {shape_index} === valid text box" )
						shape.text_frame.text = ""
			p_clone.save( str( output_powerpoint_path ) )
			print( output_powerpoint_path )
			print( output_powerpoint_path.stat() )
			return await sanic_file(
				str( output_powerpoint_path ) ,
				mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation" ,
				filename=output_powerpoint_path.name
			)
	except Exception as e:
		print( e )
		return sanic_json( dict( failed=str( e ) ) , status=200 )


@app.route( "/local/stage/2" , methods=[ "GET" ] )
async def upload( request: Request ):
	return sanic_html( f'''<!DOCTYPE html>
<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>PowerPoint - Interactive Game Generator</title>
</head>
<body>
	<h1>PowerPoint Interactive Local Game Generator - Stage 2</h1>
	<h3>Instructions for Stage 2 </h3>
	<ol>
		<li>Open the -Blank.pptx that you should of just downloaded in PowerPoint</li>
		<li>File --> Export --> File Format: JPEG , Save Every Slide , Width: 1920 , Height: 1080</li>
		<li>Create .zip archive of the orginal .pptx you uploaded in Stage 1 and the folder of jpegs it just generated</li>
		<li>Upload that .zip file here</a></li>
	</ol>
	<form enctype="multipart/form-data" action="/local/stage/2" method="POST">
		<input type="file" id="powerpoint" name="file"><br><br>
		<span>Textbox Background Color (Hex)</span>&nbsp&nbsp<input type="text" id="background_color" name="background_color" placeholder="0070C0"><br>
		<span>Exported Slide Image Width</span>&nbsp&nbsp<input type="text" id="exported_width" name="exported_width" placeholder="1920"><br>
		<span>Exported Slide Image Height</span>&nbsp&nbsp<input type="text" id="exported_height" name="exported_height" placeholder="1080"><br>
		<span>Exported Slide Image DPI</span>&nbsp&nbsp<input type="text" id="exported_image_dpi" name="exported_image_dpi" placeholder="144"><br>
		<span>Scale Percentage of Image</span>&nbsp&nbsp<input type="text" id="image_scale_percentage" name="image_scale_percentage" placeholder="60"><br>
		<span>Unanswered Color Outline</span>&nbsp&nbsp<input type="text" id="unanswered_color" name="unanswered_color" placeholder="red"><br>
		<span>Answered Color Outline</span>&nbsp&nbsp<input type="text" id="answered_color" name="answered_color" placeholder="#13E337"><br>
		<span>Typing Text Color</span>&nbsp&nbsp<input type="text" id="text_color" name="text_color" placeholder="white"><br>
		<span>Typing Text Font</span>&nbsp&nbsp<input type="text" id="text_font" name="text_font" placeholder="17px Arial"><br>
		<span>Typing Text X-Offset</span>&nbsp&nbsp<input type="text" id="text_x_offset_factor" name="text_x_offset_factor" placeholder="2"><br>
		<span>Typing Text Y-Offset</span>&nbsp&nbsp<input type="text" id="text_y_offset_factor" name="text_y_offset_factor" placeholder="3"><br>
		<span>Base URL of Hosted HTML</span>&nbsp&nbsp<input type="text" size="60" id="base_hosted_url" name="base_hosted_url" placeholder="https://39363.org/NOTES/WSU/2021/Fall/ANT3100/Interactive"><br>
		<span>CDN of Interactive Typing JS</span>&nbsp&nbsp<input type="text" size="60" id="interactive_typing_js" name="interactive_typing_js" placeholder="https://39363.org/CDN/NOTES/interactive_typing.js"><br>
		<span>CDN of Interactive DragAndDrop JS</span>&nbsp&nbsp<input type="text" size="60" id="interactive_drag_and_drop_js" name="interactive_drag_and_drop_js" placeholder="https://39363.org/CDN/NOTES/interactive_drag_and_drop.js"><br>
		<span>CDN of JQuery-UI CSS</span>&nbsp&nbsp<input type="text" size="60" id="jquery_ui_css" name="jquery_ui_css" placeholder="https://39363.org/CDN/jquery-ui.css"><br>
		<span>CDN of JQuery-UI JS</span>&nbsp&nbsp<input type="text" size="60" id="jquery_ui_js" name="jquery_ui_js" placeholder="https://39363.org/CDN/jquery-ui.min.js"><br>
		<span>CDN of JQuery JS</span>&nbsp&nbsp<input type="text" size="60" id="jquery_js" name="jquery_js" placeholder="https://39363.org/CDN/jquery-3.6.0.min.js"><br>
		<span>CDN of Bootstrap CSS</span>&nbsp&nbsp<input type="text" size="60" id="bootstrap_css" name="bootstrap_css" placeholder="https://39363.org/CDN/bootstrap.min.css"><br>
		<span>CDN of Bootstrap Bundle JS</span>&nbsp&nbsp<input type="text" size="60" id="bootstrap_bundle" name="bootstrap_bundle" placeholder="https://39363.org/CDN/bootstrap.bundle.min.js"><br>
		<br>
		<input type="submit">
	</form>
</body>
</html>''')

@app.route( "/local/stage/2" , methods=[ "POST" ] )
async def generate_local_stage_two( request: Request ):
	try:
		config = get_updated_config( request )
		input_file = request.files.get( "file" )
		input_file_type = input_file.type
		input_file_name = input_file.name
		input_file_data = input_file.body
		if input_file_name.endswith( ".zip" ) == False:
			return sanic_json( dict( failed="no .zip file sent" ) , status=200 )
		input_file_name_stem = input_file_name.split( ".zip" )[ 0 ]
		print( input_file_type , input_file_name )

		with tempfile.TemporaryDirectory() as temp_dir:

			temp_dir_posix = Path( temp_dir )
			input_zip_file_path = temp_dir_posix.joinpath( input_file_name )
			output_powerpoint_path = temp_dir_posix.joinpath( f"{input_file_name_stem}-Blank.pptx" )

			# 1.) Read Sent Bytes into .zip file inside temp directory
			with open( str( input_zip_file_path ) , "wb"  ) as file:
				file.write( input_file_data )
			print( input_zip_file_path )
			print( input_zip_file_path.stat() )

			# 2.) Extract the Zip
			with zipfile.ZipFile( str( input_zip_file_path ) , "r" ) as zip_ref:
				zip_ref.extractall( str( temp_dir_posix ) )

			# 3.) Sort Files and Folders Contained in Zip
			files_and_folders = temp_dir_posix.glob( '*' )
			uploaded_powerpoint_path = False
			image_paths = []
			for x in temp_dir_posix.iterdir():
				if x.is_file():
					if x.suffix == ".pptx":
						uploaded_powerpoint_path = x
				elif x.is_dir():
					if x.stem == "__MACOSX":
						continue
					jpegs = x.glob( "*" )
					jpegs = [ i for i in jpegs if i.is_file() ]
					for index , i in enumerate( jpegs ):
						if i.suffix == ".jpg":
							image_paths.append( x.joinpath( f"Slide{index+1}.jpg" ) )
						elif i.suffix == ".jpeg":
							image_paths.append( x.joinpath( f"Slide{index+1}.jpeg" ) )
			print( uploaded_powerpoint_path )
			print( image_paths )


			# 4.) Create Placeholder Output Directories
			generated_output_base_path = temp_dir_posix.joinpath( f"{input_file_name_stem} - Interactive" )
			generated_output_base_path.mkdir( parents=True , exist_ok=True )
			output_images_path = generated_output_base_path.joinpath( "images" )
			output_images_path.mkdir( parents=True , exist_ok=True )
			output_html_path = generated_output_base_path.joinpath( "html" )
			output_html_path.mkdir( parents=True , exist_ok=True )
			print( output_images_path )
			for index , image_path in enumerate( image_paths ):
				shutil.copyfile( image_path , output_images_path.joinpath( image_path.name ) )
			output_js_path = generated_output_base_path.joinpath( "js" )
			shutil.copytree( "./js" , output_js_path )
			output_js_path.mkdir( parents=True , exist_ok=True )
			output_css_path = generated_output_base_path.joinpath( "css" )
			shutil.copytree( "./css" , output_css_path )
			output_css_path.mkdir( parents=True , exist_ok=True )

			image_maps_in_slides = compute_image_maps.compute( str( uploaded_powerpoint_path ) , config[ "parser" ] )
			print( len( image_maps_in_slides ) )

			if len( image_paths ) != len( image_maps_in_slides ):
				print( "Lengths of Slide Images and Slide Image Maps Don't Match" )
				# print( "This could mean some slides don't have any thing but" )
				sys.exit( 1 )

			print( "here 2" )
			image_objects = []
			for slide_index , image_maps_in_slide in enumerate( image_maps_in_slides ):
				print( f"\nSlide === {slide_index+1}" )
				image_objects.append([
					f"Slide" ,
					f"../../images/{image_paths[ slide_index ].name}" ,
					image_maps_in_slide
				])
			print( "here 3" )
			pprint( image_objects )



			# 3.) Generate Interactive Games
			config[ "html" ][ "base_hosted_url" ] = "./"
			config[ "html" ][ "cdn" ][ "jquery_ui_css"][ "url" ] = f"../../css/jquery-ui.css"
			config[ "html" ][ "cdn" ][ "jquery_ui_js"][ "url" ] = f"../../js/jquery-ui.min.js"
			config[ "html" ][ "cdn" ][ "jquery_js"][ "url" ] = f"../../js/jquery-3.6.0.min.js"
			config[ "html" ][ "cdn" ][ "bootstrap_css"][ "url" ] = f"../../css/bootstrap.min.css"
			config[ "html" ][ "cdn" ][ "bootstrap_bundle"][ "url" ] = f"../../js/bootstrap.bundle.min.js"
			config[ "html" ][ "cdn" ][ "interactive_typing_js" ] = f"../../js/interactive_typing.js"
			config[ "html" ][ "cdn" ][ "interactive_drag_and_drop_js" ] = f"../../js/interactive_drag_and_drop.js"
			html_options = config[ "html" ]
			html_options[ "title" ] = uploaded_powerpoint_path.stem.replace( " " , "-" )
			html_options[ "images" ] = image_objects
			html_options[ "output_base_dir" ] = output_html_path
			interactive_notes_generator.generate( html_options , False )

			# 4.) Zip Everything and Return
			shutil.make_archive( temp_dir_posix.joinpath( f"{generated_output_base_path.stem}" ) , "zip" , str( generated_output_base_path ) )
			output_zip_path = temp_dir_posix.joinpath( f"{generated_output_base_path.stem}.zip" )
			return await sanic_file(
				str( output_zip_path ) ,
				mime_type="application/zip" ,
				filename=f"{generated_output_base_path.stem}.zip"
			)
			# return sanic_json( dict( ok="ok" ) , status=200 )
	except Exception as e:
		print( e )
		return sanic_json( dict( failed=str( e ) ) , status=200 )

# https://sanicframework.org/en/guide/basics/response.html#methods
# https://github.com/dawelter2/test_sanic_tornado/blob/master/Sanic/server.py
# https://stackoverflow.com/a/55539152
# https://lost-contact.mit.edu/afs/kth.se/system/common/src/postscript/ghostscript/5.50/src/Devices.htm

# sudo apt-get install unoconv libreoffice ghostscript -y
# soffice --headless --convert-to pdf Quiz\ 5.pptx
# gs -sDEVICE=jpeg -o Slide%02d.jpeg -r144 Quiz\ 5.pdf

# you can't make this up : https://stackoverflow.com/a/64291204
# convert -density 144 "/mnt/blockstorage/PUBLIC/TMP2/PPTXtoJPEGTest/Quiz 5.pdf" -resize 1920x1080 Slide%d.jpeg

# we are loosing resolution somehow no matter what.
# so you have to use powerpoint to export to jpegs, and then zip everything.
# i'm sorry
@app.route( "/upload-file" , methods=[ "POST" ] )
# @jwt_required
# async def upload_file( request: Request , token: Token ):
async def upload_file( request: Request ):

	config = get_updated_config( request )
	pprint( config )

	input_file = request.files.get( "file" )
	input_file_type = input_file.type
	input_file_name = input_file.name
	input_file_data = input_file.body
	# return sanic_json( { "result": "temp" } )
	# print( input_file_type , input_file_name )
	# print( config["image_upload_server_imgur_version"][ "imgur_client_id" ] )

	with tempfile.TemporaryDirectory() as temp_dir:
		temp_dir_posix = Path( temp_dir )

		with tempfile.NamedTemporaryFile( suffix=".zip" , prefix=str( temp_dir_posix ) ) as tf:
			temp_file_path = temp_dir_posix.joinpath( tf.name )
			with open( str( temp_file_path ) , "wb"  ) as file:
				file.write( input_file_data )
			print( temp_file_path )
			print( temp_file_path.stat() )

			with zipfile.ZipFile( str( temp_file_path ) , "r" ) as zip_ref:
				zip_ref.extractall( str( temp_dir_posix ) )

			files_and_folders = temp_dir_posix.glob( '*' )
			uploaded_powerpoint_path = False
			image_paths = []
			for x in temp_dir_posix.iterdir():
				if x.is_file():
					if x.suffix == ".pptx":
						uploaded_powerpoint_path = x
				elif x.is_dir():
					if x.stem == "__MACOSX":
						continue
					jpegs = x.glob( "*" )
					jpegs = [ x for x in jpegs if x.is_file() ]
					jpegs = [ x for x in jpegs if x.suffix == ".jpeg" ]
					for i in range( 1 , len( jpegs ) + 1 ):
						image_paths.append( x.joinpath( f"Slide{i}.jpeg" ) )
			print( uploaded_powerpoint_path )
			print( image_paths )

			# 1.) Compute HTML Image Map Locations
			image_maps_in_slides = compute_image_maps.compute( str( uploaded_powerpoint_path ) , config[ "parser" ] )

			# 2.) Interact with Every Blank Slide ( should be every-other-one )
			image_objects = []
			for slide_index , image_maps_in_slide in utils.enumerate2( image_maps_in_slides , 1 , 2 ):
				if slide_index > ( len( image_maps_in_slides ) * 2 ):
					continue
				print( f"\nSlide === {slide_index+1}" )

				# 1.) Upload to Image Hosting Location
				# uploaded_url = image_uploader.upload( str( slide_image_paths[ slide_index ].absolute() ) , config[ "image_upload_server" ] )
				uploaded_url = upload_file_to_imgur( image_paths[ slide_index ] )
				print( uploaded_url )
				image_objects.append([
					f"Slide" ,
					uploaded_url ,
					image_maps_in_slide
				])

			# # 3.) Generate Interactive Games
			html_output_base_dir = temp_dir_posix.joinpath( f"{uploaded_powerpoint_path.stem} - Interactive" )
			html_options = config[ "html" ]
			html_options[ "title" ] = uploaded_powerpoint_path.stem.replace( " " , "-" )
			html_options[ "images" ] = image_objects
			html_options[ "output_base_dir" ] = html_output_base_dir
			interactive_notes_generator.generate( html_options )
			shutil.make_archive( temp_dir_posix.joinpath( f"{uploaded_powerpoint_path.stem} - Interactive" ) , "zip" , str( html_output_base_dir ) )
			output_zip_path = temp_dir_posix.joinpath( f"{uploaded_powerpoint_path.stem} - Interactive.zip" )
			return await sanic_file(
				str( output_zip_path ) ,
				mime_type="application/zip" ,
				filename="interactive.zip"
			)

if __name__ == "__main__":
	app.run( host="0.0.0.0" , port="9379" )




