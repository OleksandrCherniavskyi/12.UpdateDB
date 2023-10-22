from source import link_1
import requests
from xml.etree import ElementTree as ET

session = requests.Session()
response = session.get(link_1, verify='xml.espir.crt')

if response.status_code == 200:
    with response as response:
        tree = ET.parse(response.text)
        root = tree.getroot()


        for product in root.findall('product')[0:1]:
            print(product.attrib)