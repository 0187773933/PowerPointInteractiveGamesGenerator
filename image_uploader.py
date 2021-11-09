#!/usr/bin/env python3
import sys
import requests
import json
import uuid
import base64
from pprint import pprint
from pathlib import Path

def read_json( file_path ):
	with open( file_path ) as f:
		return json.load( f )

def write_text( file_path , text_lines_list ):
	#with open( file_path , 'a', encoding='utf-8' ) as f:
	with open( file_path , 'w', encoding='utf-8' ) as f:
		f.writelines( text_lines_list )

def upload_file_to_imgur( imgur_client_id , file_path ):
	response = requests.post(
		"https://api.imgur.com/3/upload.json" ,
		headers={ "Authorization": f"Client-ID {imgur_client_id}" } ,
		data={
			"image": base64.b64encode( open( file_path , "rb" ).read() ) ,
			"type": "base64" ,
			"name": Path( file_path ).stem ,
		}
	)
	response.raise_for_status()
	data = response.json()
	# pprint( data )
	if "data" not in data:
		return
	if "link" not in data["data"]:
		return
	print( data["data"]["link"] )

def upload_url_to_imgur( imgur_client_id , image_url ):
	imgur_client_id = read_json( Path.home().joinpath( ".config" , "personal" , "imgur_uploader.json" ) )[ "client_id" ]
	response = requests.post(
		"https://api.imgur.com/3/upload.json" ,
		headers={ "Authorization": f"Client-ID {imgur_client_id}" } ,
		data={
			"image": image_url ,
			"type": "URL" ,
			"name": uuid.uuid4().hex[:10] ,
		}
	)
	response.raise_for_status()
	data = response.json()
	# pprint( data )
	if "data" not in data:
		return
	if "link" not in data["data"]:
		return
	print( data["data"]["link"] )

def upload( input_path , config ):
	global Personal
	with open( input_path , "rb" ) as upload_file:
		file_list = { "file": upload_file }
		headers = { 'key': config["key"] }
		response = requests.post( config[ "endpoint_url" ] , headers=headers , files=file_list )
		response.raise_for_status()
		print( response.text )
		return response.text