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

config = utils.read_json( sys.argv[1] )

def upload_file_to_imgur( file_path ):
	try:
		response = requests.post(
			"https://api.imgur.com/3/upload.json" ,
			headers={ "Authorization": f"Client-ID {config[ 'image_upload_server_imgur_version' ][ 'imgur_client_id' ]}" } ,
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
	manager.config.secret_key = config[ "image_upload_server_imgur_version" ][ "sanic_secret_key" ]
	manager.config.public_key = config[ "image_upload_server_imgur_version" ][ "sanic_public_key" ]
	manager.config.private_key = config[ "image_upload_server_imgur_version" ][ "sanic_private_key" ]
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


@app.route( "/upload" , methods=[ "GET" ] )
# @jwt_required
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
	<h1>PowerPoint Interactive Game Generator</h1>
	<br>
	<h2>Upload PowerPoint Here</h2>
	<form enctype="multipart/form-data" action="/upload-file" method="POST">
		<input type="file" id="powerpoint" name="file"><br>
		<input type="submit">
	</form>
</body>
</html>''')


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
	input_file = request.files.get( "file" )
	input_file_type = input_file.type
	input_file_name = input_file.name
	input_file_data = input_file.body
	print( input_file_type , input_file_name )
	print( config["image_upload_server_imgur_version"][ "imgur_client_id" ] )

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




