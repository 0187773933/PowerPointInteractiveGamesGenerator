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

@app.post( "/test/upload" , stream=True )
async def test_upload( request ):
	try:
		start_time = datetime.datetime.now().astimezone( time_zone )

		with tempfile.TemporaryDirectory() as temp_dir:
			temp_dir_posix = Path( temp_dir )
			input_file_path = temp_dir_posix.joinpath( "input.pptx" )
			print( "Uploading Test File" )
			with open( str( input_file_path ) , "wb" ) as file:
				while True:
					body = await request.stream.read()
					if body is None:
						break
					file.write( body )
			end_time = datetime.datetime.now().astimezone( time_zone )
			duration = relativedelta( end_time , start_time )
			duration_milliseconds = round( duration.microseconds / 1000 )
			print( "The Upload Took %d year %d month %d days %d hours %d minutes %d seconds %d milliseconds" % (
				duration.years , duration.months , duration.days , duration.hours , duration.minutes ,
				duration.seconds , duration_milliseconds
			))
			print( input_file_path )
			print( input_file_path.stat() )
			return sanic_json( dict( size=str( input_file_path.stat() ) ) , status=200 )
	except Exception as e:
		print( e )
		return sanic_json( dict( failed=str( e ) ) , status=200 )

if __name__ == "__main__":
	app.run( host="0.0.0.0" , port="9379" )