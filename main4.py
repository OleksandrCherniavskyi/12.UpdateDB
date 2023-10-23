from source import link_2
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime



current_datetime = datetime.now()
session = requests.Session()
response = session.get(link_2, verify='xml.espir.crt', )

soup = BeautifulSoup(response.content,  "lxml")

products = soup.find('products')
e = []
q = []
for product in products:

    x_e = product.find('e').text
    x_q = product.find('q').text
    e.append(x_e)
    q.append(x_q)

history_products_dict = {
   'ean': e,
   'qty': q,
   'date': current_datetime,
}