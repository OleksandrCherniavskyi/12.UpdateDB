import psycopg2
from source import link_1, link_2
from datetime import datetime
import requests
from xml.etree import ElementTree as ET
import pandas as pd
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
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

soup = BeautifulSoup(response.content, "lxml")

products = soup.find('products')

symbol = []
ean = []
qty = []
model = []  # Fixed the issue here by initializing the model list
sizechart = []

for product in products:
    x_symbol = product.find('symbol').text
    x_ean = product.find('ean').text
    x_qty = product.find('qty').text
    x_model = product.find('model').text
    x_sizechart = product.find('sizechart').text
    symbol.append(x_symbol)
    qty.append(x_qty)
    model.append(x_model)  # Fixed the issue here by appending x_model
    sizechart.append(x_sizechart)
    ean.append(x_ean)

product_dict = {
   'symbol': symbol,
   'ean': ean,
   'qty': qty,
   'model': model,
   'sizechart': sizechart
}
current_datetime = datetime.now()


history_products_dict = {
   'ean': ean,
   'qty': qty,
   'date': current_datetime,

}

product_df = pd.DataFrame(product_dict, columns=['symbol', 'ean', 'qty', 'model', 'sizechart'])
product_df = product_df.sort_values(by='ean')
product_df.to_sql("products", engine, if_exists='append', index=False)

history_products_df = pd.DataFrame(history_products_dict, columns=['ean', 'qty', 'date'])
history_products_df.to_sql("history_products", engine, if_exists='append', index=False)


session.close()

cursor.close()
connection.close()
print("Database connection closed")





# Record the end time
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

print(f"Elapsed time for database operations: {elapsed_time} seconds")

#Elapsed time for database operations: 16.939167261123657 seconds