from source import link_2
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import time
import psycopg2
from sqlalchemy import create_engine
import pandas as pd


exiting_product_query = '''
SELECT ean, qty, (ean*(qty - 1000000)) AS my_id
FROM "products"'''

# Database connection parameters
db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '885531',
    'host': 'localhost',
    'port': '5432',
}
engine = create_engine('postgresql://postgres:885531@localhost:5432')

current_datetime = datetime.now()
# Record the start time
start_time = time.time()

# Create a connection to the database

connection = psycopg2.connect(**db_params)
connection.autocommit = True
cursor = connection.cursor()
# Now you can execute SQL queries


session = requests.Session()
response = session.get(link_2, verify='xml.espir.crt', )

soup = BeautifulSoup(response.content,  "lxml")

products = soup.find('products')
e = []
q = []
s = []
m = []
my_id = []
for product in products:

    x_e = product.find('e').text
    if x_e == '':
        continue
    x_e = int(x_e)
    x_q = product.find('q').text
    x_q = int(x_q)
    x_x = (x_e * (x_q - 1000000))
    x_s = product.find('s').text
    x_m = product.find('m').text

    s.append(x_s)
    m.append(x_m)
    e.append(x_e)
    q.append(x_q)
    my_id.append(x_x)

compared_dict = {
   'ean': e,
   'qty': q,
   'my_id': my_id,
    'symbol': s,
    'model': m
}
compared_df = pd.DataFrame(compared_dict, columns=['ean', 'qty', 'my_id', 'symbol', 'model'])

exiting_product = pd.read_sql_query(exiting_product_query, engine)
changed_qty = compared_df[~compared_df["my_id"].isin(exiting_product['my_id'])]

update_df_columns = ['symbol', 'ean', 'qty', 'model']


new_columns = ['ean', 'qty']
new_df = changed_qty[new_columns].copy()
update_df = changed_qty[update_df_columns].copy()
update_df.to_sql("products", engine, if_exists='replace', index=False)
new_df['date'] = current_datetime
print(new_df)
new_df.to_sql("history_products", engine, if_exists='append', index=False)

# Record the end time
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

print(f"Elapsed time for database operations: {elapsed_time} seconds")
