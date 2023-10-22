import certifi
import requests
from source import link_1, link_2


try:
  print('Checking connection to Site...')
  test = requests.get(link_2)
  print('Connection to Github OK.')
except requests.exceptions.SSLError as err:
  print('SSL Error. Adding custom certs to Certifi store...')
  cafile = certifi.where()
  with open('certicate.pem', 'rb') as infile:
    customca = infile.read()
  with open(cafile, 'ab') as outfile:
    outfile.write(customca)
    print('That might have worked.')