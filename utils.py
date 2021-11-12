import sys
import json
from pathlib import Path
from natsort import humansorted

def write_json( file_path , python_object ):
	with open( file_path , 'w', encoding='utf-8' ) as f:
		json.dump( python_object , f , ensure_ascii=False , indent=4 )

def read_json( file_path ):
	with open( file_path ) as f:
		return json.load( f )

# https://stackoverflow.com/a/24290026
def enumerate2( xs , start=0 , step=1 ):
	for x in xs:
		yield ( start , x )
		start += step

def get_slide_image_paths( power_point_file ):
	power_point_file_posix = Path( power_point_file )
	ALLOWED_EXTENSIONS = [ ".jpeg" ]
	BaseDirectoryPosixPath = power_point_file_posix.parent.joinpath( power_point_file_posix.stem )
	FilesPosixInBaseDirectory = BaseDirectoryPosixPath.glob( '*' )
	FilesPosixInBaseDirectory = [ x for x in FilesPosixInBaseDirectory if x.is_file() ]
	FilesPosixInBaseDirectory = [ x for x in FilesPosixInBaseDirectory if x.suffix in ALLOWED_EXTENSIONS ]
	# FilesPosixInBaseDirectory = humansorted( FilesPosixInBaseDirectory )
	FilesPosixInBaseDirectory = [ BaseDirectoryPosixPath.joinpath( f"Slide{x}.jpeg" ) for x in range( 1 , len( FilesPosixInBaseDirectory ) + 1 ) ]
	return FilesPosixInBaseDirectory
