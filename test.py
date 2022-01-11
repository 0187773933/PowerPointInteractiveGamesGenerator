#!/usr/bin/env python3
import sys
import uuid
import time
import base64
from pathlib import Path
from pprint import pprint
import tempfile
import zipfile
import shutil
import requests
from binascii import b2a_hex

from sanic import Sanic
from sanic.response import html as sanic_html
from sanic.response import json as sanic_json
from sanic.response import file as sanic_file
from sanic.response import file_stream as sanic_file_stream
from sanic.response import stream as sanic_stream
from sanic.request import Request

import pytz
import datetime
from dateutil.relativedelta import relativedelta
time_zone = pytz.timezone( "US/Eastern" )
app = Sanic( __name__ )
import magic
# https://pypi.org/project/python-magic/
# sudo apt-get install libmagic1
# brew install libmagic
# pip install python-magic-bin
mime = magic.Magic( mime=True )


@app.route( "/" , methods=[ "GET" ] )
async def local( request: Request ):
	return sanic_html( f'''<!DOCTYPE html>
<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>Test Uploader</title>
</head>
<body>
	<h1>Test Uploader</h1>
	<form enctype="multipart/form-data" action="/test/upload" method="POST">
		<input type="file" id="powerpoint" name="file"><br><br>
		<input type="submit">
	</form>
</body>
</html>''')

# def determine_image_type( self , stream_first_4_bytes ):
# 	file_type = None
# 	bytes_as_hex = b2a_hex( stream_first_4_bytes ).decode()
# 	if bytes_as_hex.startswith( 'ffd8' ):
# 		file_type = '.jpeg'
# 	elif bytes_as_hex == '89504e47':
# 		file_type = '.png'
# 	elif bytes_as_hex == '47494638':
# 		file_type = '.gif'
# 	elif bytes_as_hex.startswith('424d'):
# 		file_type = '.bmp'
# 	return file_type

@app.post( "/test/upload" , stream=True )
async def test_upload( request ):
	try:

		# 1.) Injest octet-stream
		start_time = datetime.datetime.now().astimezone( time_zone )
		with tempfile.TemporaryDirectory() as temp_dir:
			temp_dir_posix = Path( temp_dir )
			input_file_path = temp_dir_posix.joinpath( "input" )
			print( "Uploading Test File" )
			first_128 = bytes()
			with open( str( input_file_path ) , "wb" ) as file:
				while True:
					body = await request.stream.read()
					if body is None:
						break
					if len( first_128 ) < 129:
						first_128 += body
					file.write( body )
			end_time = datetime.datetime.now().astimezone( time_zone )
			duration = relativedelta( end_time , start_time )
			duration_milliseconds = round( duration.microseconds / 1000 )
			print( "The Upload Took %d year %d month %d days %d hours %d minutes %d seconds %d milliseconds" % (
				duration.years , duration.months , duration.days , duration.hours , duration.minutes ,
				duration.seconds , duration_milliseconds
			))

			# 2.) Discover File Type
			print( input_file_path )
			file_name = False
			file_extension = False
			file_content_type = False
			try:
				test = first_128[ 0 : 500 ].decode( "utf-8" , "ignore" )
				file_name = test.split( "filename=" )[ 1 ].split( "\n" )[ 0 ][ 1:-2 ]
				file_extension = file_name.split( "." )[ -1 ]
				file_content_type = test.split( "Content-Type: " )[ 1 ].split( "\n" )[ 0 ]
			except Exception as file_type_decode_exception:
				print( file_type_decode_exception )
			print( file_name , file_extension , file_content_type )
			# https://python-forum.io/thread-11941-post-54130.html#pid54130
			# if file_extension != False:
			# 	print( "????" )
			# 	input_file_path.rename( temp_dir_posix.joinpath( file_name ) )
			# 	print( input_file_path )
			print( input_file_path.stat() )

			return sanic_json( dict( size=str( input_file_path.stat() ) ) , status=200 )
	except Exception as e:
		print( e )
		return sanic_json( dict( failed=str( e ) ) , status=200 )

if __name__ == "__main__":
	app.run( host="0.0.0.0" , port="9379" )