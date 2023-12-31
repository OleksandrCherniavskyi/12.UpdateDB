from sqlalchemy import create_engine, text


exiting_product_query = text('''
SELECT ean, qty, (ean*(qty + 1000)) AS my_id
FROM "products"
--LIMIT 10000''')

create_products_table = text('''
    CREATE TABLE IF NOT EXISTS products (
        ean bigint PRIMARY KEY,
        symbol character varying(13),
        qty integer,
        model character varying(16),
        sizechart character varying(50)
    );
''')

create_history_products_table = text("""
CREATE TABLE IF NOT EXISTS history_products (
    id serial PRIMARY KEY,
    ean bigint,
    qty integer,
    date timestamp
);""")

#update_query = f"INSERT INTO products (ean, qty, symbol, model ) VALUES ({ean}, {qty},{symbol},{model}) ON CONFLICT (ean) DO UPDATE SET qty = {qty}"