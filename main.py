import psycopg2
from source import link_1, link_2
from datetime import datetime
import requests
from xml.etree import ElementTree as ET
import pandas as pd
from sqlalchemy import create_engine

import time

# Record the start time
start_time = time.time()


# Database connection parameters
db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '885531',
    'host': 'localhost',
    'port': '5432',
}
engine = create_engine('postgresql://postgres:885531@localhost:5432')

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
# Now you can execute SQL queries


# Define a function to insert data into the 'products' table
def insert_product(symbol, ean, qty, model, sizechart):
    cursor.execute(create_products_table)
    insert_query = "INSERT INTO products (symbol, ean, qty, model, sizechart) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(insert_query, (symbol, ean, qty, model, sizechart))

def insert_history_product(ean, qty, date):
    cursor.execute(create_history_products_table)
    insert_query = "INSERT INTO history_products (ean, qty, date) VALUES (%s, %s, %s)"
    cursor.execute(insert_query, (ean, qty, date))

session = requests.Session()
response = session.get(link_1, verify='xml.espir.crt')




try:


    if response.status_code == 200:
        # Create an iterable for efficient parsing
        context = ET.iterparse(response.content, events=("start", "end"))

        # Turn it into an iterator
        context = iter(context)

        # Get the root element
        event, root = next(context)

        # Define the chunk size
        chunk_size = 1000

        for event, elem in context:
            if event == "end" and elem.tag == "product":
                symbol = []
                ean = []
                qty = []
                model = []
                sizechart = []
                x_symbol = elem.find('symbol').text
                #ean_element = elem.find('ean')
                #if ean_element is not None and ean_element.text is not None and ean_element.text.strip() != "":
                x_ean = elem.find('ean').text
                ean.append(x_ean)
                x_qty = elem.find('qty').text
                x_model = elem.find('model').text
                x_sizechart = elem.find('sizechart').text

                insert_product(x_symbol, x_ean, x_qty, x_model, x_sizechart)
                current_datetime = datetime.now()
                insert_history_product(x_ean, x_qty, current_datetime)
                #symbol.append(x_symbol)
                #qty.append(x_qty)
                #model.append(model)
                #sizechart.append(x_sizechart)
                #product_dict = {
                #    'symbol': symbol,
                #    'ean': ean,
                #    'qty': qty,
                #    'model': model,
                #    'sizechart': sizechart
                #}
#
                product_df = pd.DataFrame(product_dict, columns=['symbol', 'ean', 'qty', 'model', 'sizechart'])
                product_df = product_df.sort_values(by='ean')
                product_df.to_sql("products", engine, if_exists='append', index=False)

                # Process the extracted data here
                # You may want to store it in lists or perform further actions
                root.clear()
    else:
        print(f"Failed to retrieve the XML file. Status code: {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred while making the request: {e}")


#if response.status_code == 200:
#    xml_content = response.content
#    try:
#        root = ET.fromstring(xml_content)
#    except ET.ParseError as e:
#        print(f"XML ParseError: {e}")
#
#        # Let's try to print the problematic line from the XML
#        lines = xml_content.decode('utf-8').splitlines()  # Decode the content to a string
#        error_line = lines[1]  # Assuming line 2 is where the error occurred
#        print("Problematic Line:")
#        print(error_line)
#    #root = ET.fromstring(xml_content)
#    # Define the chunk size
#    chunk_size = 1000
#    for products_element in root.findall('.//products'):
#        # Find all P elements within PRODUCTS
#        p_elements = products_element.findall('product')
#        symbol = []
#        ean = []
#        qty = []
#        model = []
#        sizechart = []
#        for product in p_elements:
#            x_symbol = product.find('symbol').text
#            ean_element = product.find('ean')
#            if ean_element is not None and ean_element.text is not None and ean_element.text.strip() != "":
#                x_ean = ean_element.text
#            x_qty = product.find('qty').text
#            x_model = product.find('model').text
#            x_sizechart = product.find('sizechart').text
#
#
#            symbol.append(x_symbol)
#            ean.append(x_ean)
#            qty.append(x_qty)
#            model.append(model)
#            sizechart.append(x_sizechart)
#            product_dict = {
#                'symbol': symbol,
#                'ean': ean,
#                'qty': qty,
#                'model': model,
#                'sizechart': sizechart
#            }
#            product_df = pd.DataFrame(product_dict, columns=['symbol', 'ean', 'qty', 'model', 'sizechart'] )
#            product_df.shape
#            #product_df = product_df.sort_values(by='ean')
#            #product_df.to_sql("products", engine, if_exists='append', index=False, chunksize=1000)
#
#            #insert_product(x_symbol, x_ean, x_qty, x_model, x_sizechart)
#            #current_datetime = datetime.now()
#            #insert_history_product(x_ean, x_qty, current_datetime)
#
#        else:
#            print("No 'PRODUCTS' element found in the XML")


session.close()

cursor.close()
connection.close()
print("Database connection closed")



# Record the end time
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

print(f"Elapsed time for database operations: {elapsed_time} seconds")