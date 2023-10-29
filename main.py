import psycopg2
import schedule
from source import link_1, link_2
from datetime import datetime
import requests
import pandas as pd
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
import time
from query import create_products_table, create_history_products_table, exiting_product_query





# Database connection parameters
db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '885531',
    'host': 'localhost',
    'port': '5432',
}
engine = create_engine('postgresql://postgres:885531@localhost:5432')



# Now you can execute SQL queries
def create_db():
    # Create a connection to the database
    session = requests.Session()
    connection = psycopg2.connect(**db_params)
    connection.autocommit = True
    cursor = connection.cursor()
    # Record the start time
    start_time = time.time()
    # create table
    cursor.execute(create_products_table)
    cursor.execute(create_history_products_table)

    # Check if the table is not empty
    cursor.execute("SELECT COUNT(*) FROM products;")

    row_count = cursor.fetchone()[0]
    # If the table is not empty, call the update_table function
    if row_count > 0:
        update_db()
    else:
        # parsing

        response = session.get(link_1, verify='xml.espir.crt')

        soup = BeautifulSoup(response.content, "lxml")
        products = soup.find('products')
        symbol = []
        ean = []
        qty = []
        model = []
        sizechart = []

        for product in products:
            x_symbol = product.find('symbol').text
            x_ean = product.find('ean').text
            if x_ean == '':
                continue
            x_qty = product.find('qty').text
            x_model = product.find('model').text
            x_sizechart = product.find('sizechart').text
            symbol.append(x_symbol)
            qty.append(x_qty)
            model.append(x_model)
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
        # Record the end time
        end_time = time.time()

        # Calculate the elapsed time
        elapsed_time = end_time - start_time

        print(f"Elapsed time for To create DB: {elapsed_time} seconds")
        session.close()

        cursor.close()
        connection.close()
        print("Database connection closed")
        update_db()


def update_db():
    # Record the start time
    start_time = time.time()

    # Create a connection to the database
    session = requests.Session()
    connection = psycopg2.connect(**db_params)
    connection.autocommit = True
    cursor = connection.cursor()

    response = session.get(link_2, verify='xml.espir.crt', )

    soup = BeautifulSoup(response.content, features="lxml")
    products = soup.find('products')
    e = []
    q = []
    s = []
    m = []
    my_id = []
    for product in products:
        x_e = product.find('e')

        if x_e is None:
            continue
        x_e = product.find('e').text

        if x_e == '':
            continue
        x_e = int(x_e)

        try:
            x_q = product.find('q').text
            x_q = int(x_q)
        except AttributeError:
            x_q = None
        x_x = (x_e*(x_q+1000))
        x_x = int(x_x)

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
    pd.set_option('display.max_rows', 10)
    #print(f'New:', compared_df)
    # Specify the chunk size
    chunk_size = 5000

    # Create an empty list to store the DataFrames
    combined_data = []

    # Read data in chunks and append to the combined list
    for chunk in pd.read_sql_query(exiting_product_query, engine, chunksize=chunk_size):
        combined_data.append(chunk)

    # Combine all chunks into one DataFrame using pd.concat
    exiting_product = pd.concat(combined_data, ignore_index=True)
    #exiting_product = pd.read_sql_query(exiting_product_query, engine)

    print(f'EXITING:', exiting_product)
    changed = compared_df["my_id"].isin(exiting_product['my_id'])
    changed_qty = compared_df[~changed]

    print(changed_qty)
    update_df_columns = ['symbol', 'ean', 'qty', 'model']
    update_df = changed_qty[update_df_columns].copy()
    update_df.to_sql("products", engine, if_exists='replace', index=False)

    new_columns = ['ean', 'qty']
    new_df = changed_qty[new_columns].copy()

    current_datetime = datetime.now()
    new_df['date'] = current_datetime

    new_df.to_sql("history_products", engine, if_exists='append', index=False)

    session.close()

    cursor.close()
    connection.close()
    print("Database connection closed")

    # Record the end time
    end_time = time.time()
    # Calculate the elapsed time
    elapsed_time = end_time - start_time
    print(f"Elapsed time to update DB: {elapsed_time} seconds")

create_db()



schedule.every(1).minutes.do(update_db)

# Run an infinite loop to execute the scheduled tasks
while True:
    schedule.run_pending()
    time.sleep(1)





