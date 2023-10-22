from source import link_1, link_2

url = link_1

import requests
from xml.etree import ElementTree as ET



session = requests.Session()
response = session.get(link_2, verify='xml.espir.crt')

if response.status_code == 200:
    xml_content = response.content
    root = ET.fromstring(xml_content)
    products_element = root.find('PRODUCTS')

    if products_element is not None:
        # Find all P elements within PRODUCTS
        p_elements = products_element.findall('P')

        for p in p_elements:
            # Access and print the content of the P element
            s = p.find('S').text
            m = p.find('M').text
            e = p.find('E').text
            q = p.find('Q').text
            print(f"S: {s}, M: {m}, E: {e}, Q: {q}")

    else:
        print("No 'PRODUCTS' element found in the XML")

session.close()