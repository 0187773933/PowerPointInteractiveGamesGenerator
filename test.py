#!/usr/bin/env python3


# https://stackoverflow.com/a/49111747
def get_nested_dictionary_value( d , l , default_val=None ):
	if l[ 0 ] not in d:
		print( "1" )
		return default_val
	elif len( l )==1:
		print( "2" )
		return d[ l[ 0 ] ]
	else:
		print( "3" )
		return get_nested_dictionary_value( d[ l[ 0 ] ] , l[ 1: ] )

def set_nested_dictionary_value( d , l , set_value=None ):
	if l[ 0 ] not in d:
		print( "1" )
		return set_value
	elif len( l )==1:
		print( "3" )
		d[ l[ 0 ] ] = set_value
		return d
	else:
		print( "3" )
		return set_nested_dictionary_value( d[ l[ 0 ] ] , l[ 1: ] , set_value )

if __name__ == "__main__":
    x = { "a": [ 3 , 4 , 5 , 6 ] , "b": { "q": "here" } }
    print( x )
    print( get_nested_dictionary_value( x , [ "b" , "q" ] ) )
    set_nested_dictionary_value( x , [ "b" , "q" ] , "there" )
    print( x )
