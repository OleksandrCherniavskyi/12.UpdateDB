import schedule
from source import link_1, link_2
from datetime import datetime
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from bs4 import BeautifulSoup
import time
from query import create_products_table, create_history_products_table, exiting_product_query
import warnings


db_name = 'database'
db_user = 'username'
db_pass = 'secret'
db_host = 'db'
db_port = '5432'

# Create the connection string
connection_string = f'postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

# Create the database engine
engine = create_engine(connection_string)

#engine = create_engine('postgresql+psycopg2://postgres:885531@localhost:5432')

# Now you can execute SQL queries
def create_db():
    # Create a connection to the database
    session = requests.Session()
    print('Connection to DB')
    connection = engine.connect()
    #connection.autocommit = True

    # Record the start time
    start_time = time.time()
    # create table
    connection.execute(create_products_table)
    print('Create table products if not exists')

    connection.execute(create_history_products_table)
    print('Create table history_products if not exists')

    # Check if the table is not empty
    result = connection.execute(text("SELECT COUNT(*) FROM products;"))
    row_count = result.fetchone()[0]
    print(f'Rows in products table:', row_count)
    # If the table is not empty, call the update_table function
    if row_count > 0:
        print("Check to update data")
        updatebd2()
    else:
        print('Parsing XML')
        response = session.get(link_1, verify='xml.espir.crt')
        warnings.filterwarnings("ignore", category=UserWarning, module="bs4")
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

        product_df = pd.DataFrame(product_dict, columns=['ean', 'symbol', 'qty', 'model', 'sizechart'])
        product_df = product_df.sort_values(by='ean')
        product_df.to_sql("products", connection, if_exists='append', index=False)
        #connection.commit()
        print("Add data to products table")
        # Check if the table is not empty
        result = connection.execute(text("SELECT COUNT(*) FROM products;"))
        row_count = result.fetchone()[0]
        print(f'Rows in products table:', row_count)
        history_products_df = pd.DataFrame(history_products_dict, columns=['ean', 'qty', 'date'])
        history_products_df.to_sql("history_products", connection, if_exists='append', index=False)
        #connection.commit()
        # Record the end time
        end_time = time.time()

        # Calculate the elapsed time
        elapsed_time = end_time - start_time

        print(f"DB created in  {elapsed_time} seconds")
        session.close()

        connection.close()
        print("Database connection closed")


def update_db():
    # Record the start time
    start_time = time.time()

    # Create a connection to the database
    session = requests.Session()
    connection = engine.connect()
    print('Connection to DB')

    response = session.get(link_2, verify='xml.espir.crt', )
    warnings.filterwarnings("ignore", category=UserWarning, module="bs4")
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

    exiting = connection.execute(exiting_product_query)
    exiting_product = pd.DataFrame(exiting.fetchall(), columns=['ean', 'qty', 'my_id'])
    changed = compared_df["my_id"].isin(exiting_product['my_id'])
    changed_qty = compared_df[~changed]

    connection.close()
    print("Database connection closed")

    # Record the end time
    end_time = time.time()
    # Calculate the elapsed time
    elapsed_time = end_time - start_time
    print(f"Compared data in: {elapsed_time} seconds")
    return changed_qty


def updatebd2():
    compared = update_db()
    if compared.empty:
        print("No new data. Stopping the function.")
        return
    # Record the start time
    start_time = time.time()

    # Create a connection to the database
    connection = engine.connect()
    print('Connection to DB')

    new_columns = ['ean', 'qty']
    new_df = compared[new_columns].copy()
    current_datetime = datetime.now()
    new_df['date'] = current_datetime
    new_df.to_sql("history_products", connection, if_exists='append', index=False)
    #connection.commit()
    print('Update table history product')

    for index, row in compared.iterrows():
        ean = row['ean']
        qty = row['qty']
        symbol = row['symbol']
        model = row['model']

        update_query = text(f"INSERT INTO products (ean, qty, symbol, model) VALUES ({ean}, {qty}, '{symbol}', '{model}') ON CONFLICT (ean) DO UPDATE SET qty = {qty}")

        connection.execute(update_query)
    #connection.commit()

    print('Update table Product')
    connection.close()
    print("Database connection closed")

    # Record the end time
    end_time = time.time()
    # Calculate the elapsed time
    elapsed_time = end_time - start_time
    print(f"Update database in: {elapsed_time} seconds")

create_db()

schedule.every(1).minutes.do(create_db)

# Run an infinite loop to execute the scheduled tasks
while True:
    schedule.run_pending()
    time.sleep(1)
