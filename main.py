import certifi
from source import link_1, link_2

url = link_1

import requests
from xml.etree import ElementTree as ET



session = requests.Session()
response = session.get(link_1, verify='xml.espir.crt')

if response.status_code == 200:
    xml_content = response.content
    root = ET.fromstring(xml_content)
    products_element = root.find('products')

    if products_element is not None:
        # Find all P elements within PRODUCTS
        p_elements = products_element.findall('product')

        for product in p_elements:
            # Access and print the content of the P element
            symbol = product.find('symbol').text
            ean = product.find('ean').text
            qty = product.find('qty').text
            model = product.find('model').text
            sizechart = product.find('sizechart').text
            print(f"Symbol: {symbol}, ean: {ean}, qty: {qty}, model: {model}, sizechart: {sizechart}")

    else:
        print("No 'PRODUCTS' element found in the XML")

session.close()
