import certifi
from source import link_1, link_2



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

        for product in p_elements[0:20]:
            symbol = product.find('symbol').text
            ean = product.find('ean').text
            qty = product.find('qty').text
            model = product.find('model').text
            sizechart = product.find('sizechart').text

            print(symbol, ean, qty, model, sizechart)
    else:
        print("No 'PRODUCTS' element found in the XML")


session.close()



#Maximum EAN Length: 13
#Maximum Symbol Length: 13
#Maximum Qty Length: 4
#Maximum Model Length: 16
#Maximum Sizechart Length: 49
#