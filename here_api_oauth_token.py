# GET TOKEN (HERE REST API's)

import time #To generate the OAuth timestamp
import urllib.parse #To URLencode the parameter string
import hmac #To implement HMAC algorithm
import hashlib #To generate SHA256 digest
from base64 import b64encode #To encode binary data into Base64
import binascii #To convert data into ASCII
import requests #To make HTTP requests

grant_type = 'client_credentials'
oauth_consumer_key = 'Q1kYHo33I5p8JBVxGatlnQ' #From credentials.properties file
oauth_nonce = str(int(time.time()*1000))
oauth_signature_method = 'HMAC-SHA256'
oauth_timestamp = str(int(time.time()))
oauth_version = '1.0'

def create_parameter_string(grant_type, oauth_consumer_key,oauth_nonce,oauth_signature_method,oauth_timestamp,oauth_version):
    parameter_string = ''
    parameter_string = parameter_string + 'grant_type=' + grant_type
    parameter_string = parameter_string + '&oauth_consumer_key=' + oauth_consumer_key
    parameter_string = parameter_string + '&oauth_nonce=' + oauth_nonce
    parameter_string = parameter_string + '&oauth_signature_method=' + oauth_signature_method
    parameter_string = parameter_string + '&oauth_timestamp=' + oauth_timestamp
    parameter_string = parameter_string + '&oauth_version=' + oauth_version
    return parameter_string

parameter_string = create_parameter_string(grant_type, oauth_consumer_key,oauth_nonce,oauth_signature_method,oauth_timestamp,oauth_version)
encoded_parameter_string = urllib.parse.quote(parameter_string, safe='')

url = 'https://account.api.here.com/oauth2/token'
encoded_base_string = 'POST' + '&' + urllib.parse.quote(url, safe='')
encoded_base_string = encoded_base_string + '&' + encoded_parameter_string

access_key_secret = 'M3dXIGLygXrRjDjGraMB3_uJ_g7Fv9XD8HOtVOTRyG2gxHeBRNBKPSn3keyIekgyImxuLdycUJAeXSmE16Ufbw' #From credentials.properties file
signing_key = access_key_secret + '&'

def create_signature(secret_key, signature_base_string):
    encoded_string = signature_base_string.encode()
    encoded_key = secret_key.encode()
    temp = hmac.new(encoded_key, encoded_string, hashlib.sha256).hexdigest()
    byte_array = b64encode(binascii.unhexlify(temp))
    return byte_array.decode()

oauth_signature = create_signature(signing_key, encoded_base_string)
encoded_oauth_signature = urllib.parse.quote(oauth_signature, safe='')

body = {'grant_type' : '{}'.format(grant_type)}

headers = {
            'Content-Type' : 'application/x-www-form-urlencoded',
            'Authorization' : 'OAuth oauth_consumer_key="{0}",oauth_nonce="{1}",oauth_signature="{2}",oauth_signature_method="HMAC-SHA256",oauth_timestamp="{3}",oauth_version="1.0"'.format(oauth_consumer_key,oauth_nonce,encoded_oauth_signature,oauth_timestamp)
          }
    
response = requests.post(url, data=body, headers=headers)

def get_token():
    token = response.text
    return token






