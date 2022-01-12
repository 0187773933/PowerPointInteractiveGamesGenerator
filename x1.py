#!/usr/bin/env python3
import base64
import utils

# openssl ecparam -name secp521r1 -genkey -noout -out private.ec.key
if __name__ == "__main__":
	x = utils.base64_encode('''-----BEGIN EC PRIVATE KEY-----
MIHcAgEBBEIAsO7NyYC8+C0qvNlGYalj5Da5OWIWxfoc7zV+EUjI9R/QC2/uQis1
jFtiATJkX6BUT4MoyuQFFdPmtwp2ef9T2zigBwYFK4EEACOhgYkDgYYABACyrReG
LN+BvSV2l+vvG0FeP/zH7jgujmDguRDJIUZ0etyjJpnUzHtF56tiZ3yJSK5BZn4O
Wfz7HSqqW5nx3aPt/wEpox5q9OZXrzKJ0JBR17j9vqmz3+8Qu7T5kVDhOrjwv+zn
blUHGl0LoDq7f7Lpjx3+aAUHMH6QU11LzIFZHFxUdQ==
-----END EC PRIVATE KEY-----''')
	print( x )