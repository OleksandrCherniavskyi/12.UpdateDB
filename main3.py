import pandas as pd
from xml.sax import make_parser, handler
from source import link_1, link_2
import requests
import psycopg2
from xml.etree import ElementTree as ET
from sqlalchemy import create_engine
import time
# Record the start time
start_time = time.time()

engine = create_engine('postgresql://postgres:885531@localhost:5432')
db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '885531',
    'host': 'localhost',
    'port': '5432',
}

create_products_table = """
CREATE TABLE IF NOT EXISTS products (
    ean bigint PRIMARY KEY,
    symbol character varying(13),
    qty integer,
    model character varying(16),
    sizechart character varying(50)
);"""

create_history_products_table = """
CREATE TABLE IF NOT EXISTS history_products (
    ean bigint,
    qty integer,
    date timestamp,
    FOREIGN KEY (ean) REFERENCES products(ean)
);
"""

# Create a connection to the database

connection = psycopg2.connect(**db_params)
connection.autocommit = True
cursor = connection.cursor()




class XMLHandler(handler.ContentHandler):
    def __init__(self):
        self.data = []
        self.row = {}
        self.product_dict = {
            'symbol': [],
            'ean': [],
            'qty': [],
            'model': [],
            'sizechart': []
        }

    def startElement(self, name, attrs):
        self.row = {}

    def characters(self, data):
        self.row[self.current_tag] = data

    def endElement(self, name):
        if name == 'product':
            self.product_dict['symbol'].append(self.row['symbol'])
            self.product_dict['ean'].append(self.row['ean'])
            self.product_dict['qty'].append(self.row['qty'])
            self.product_dict['model'].append(self.row['model'])
            self.product_dict['sizechart'].append(self.row['sizechart'])

        self.row = {}

# Create a single XMLHandler object
xml_handler = XMLHandler()

session = requests.Session()
response = session.get(link_1, verify='xml.espir.crt', stream=True)

if response.status_code == 200:
    xml_content = response.content
    tree = ET.parse(xml_content)
    root = tree.getroot()


    handler = XMLHandler()
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.parse(xml_content)

    product_df = pd.DataFrame(xml_handler.product_dict, columns=['symbol', 'ean', 'qty', 'model', 'sizechart'])
    product_df = product_df.sort_values(by='ean')

    product_df.to_sql("products", engine, if_exists='append', index=False)


# Record the end time
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

print(f"Elapsed time for database operations: {elapsed_time} seconds")
