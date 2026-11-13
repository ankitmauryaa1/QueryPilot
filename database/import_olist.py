
import pandas as pd
from pathlib import Path
from sqlalchemy import text

from database.connection import get_engine


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "processed"


def create_tables(engine):

    print("Creating MySQL tables...")

    statements = [

        # Customers
        """
        CREATE TABLE IF NOT EXISTS  olist_customers (
            customer_id VARCHAR(32) PRIMARY KEY,
            customer_unique_id VARCHAR(32),
            customer_zip_code_prefix INT,
            customer_city VARCHAR(100),
            customer_state CHAR(2)
        )
        """,

        # Products
        """
        CREATE TABLE IF NOT EXISTS  olist_products (
            product_id VARCHAR(32) PRIMARY KEY,
            product_category_name VARCHAR(100),
            product_name_lenght INT,
            product_description_lenght INT,
            product_photos_qty INT,
            product_weight_g INT,
            product_length_cm INT,
            product_height_cm INT,
            product_width_cm INT
        )
        """,

        # Orders
        """
        CREATE TABLE IF NOT EXISTS  olist_orders (
            order_id VARCHAR(32) PRIMARY KEY,
            customer_id VARCHAR(32) NOT NULL,
            order_status VARCHAR(30),
            order_purchase_timestamp DATETIME,
            order_approved_at DATETIME,
            order_delivered_carrier_date DATETIME,
            order_delivered_customer_date DATETIME,
            order_estimated_delivery_date DATETIME,

            CONSTRAINT fk_olist_order_customer
            FOREIGN KEY (customer_id)
            REFERENCES olist_customers(customer_id)
        )
        """,

        # Order items
        """
        CREATE TABLE IF NOT EXISTS  olist_order_items (
            order_id VARCHAR(32) NOT NULL,
            order_item_id INT NOT NULL,
            product_id VARCHAR(32) NOT NULL,
            seller_id VARCHAR(32),
            shipping_limit_date DATETIME,
            price DECIMAL(10,2),
            freight_value DECIMAL(10,2),

            PRIMARY KEY (order_id, order_item_id),

            CONSTRAINT fk_olist_item_order
            FOREIGN KEY (order_id)
            REFERENCES olist_orders(order_id),

            CONSTRAINT fk_olist_item_product
            FOREIGN KEY (product_id)
            REFERENCES olist_products(product_id)
        )
        """,

        # Payments
        """
        CREATE TABLE IF NOT EXISTS  olist_payments (
            order_id VARCHAR(32) NOT NULL,
            payment_sequential INT NOT NULL,
            payment_type VARCHAR(30),
            payment_installments INT,
            payment_value DECIMAL(10,2),

            PRIMARY KEY (order_id, payment_sequential),

            CONSTRAINT fk_olist_payment_order
            FOREIGN KEY (order_id)
            REFERENCES olist_orders(order_id)
        )
        """
    ]

    with engine.begin() as connection:

    

        for statement in statements:
            connection.execute(text(statement))

    print("All five tables created!")


def import_csv(engine, table_name, date_columns=None):

    file_path = DATA_DIR / f"{table_name}.csv"

    print(f"\nImporting {table_name}...")

    df = pd.read_csv(file_path)

    # Convert date columns
    if date_columns:
        for column in date_columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )

    # Replace missing values with SQL NULL-compatible None
    df = df.astype(object).where(pd.notna(df), None)

    df.to_sql(
        name=f"olist_{table_name}",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=1000
    )

    print(f"{table_name}: {len(df):,} rows imported")


def import_all():

    engine = get_engine()

    try:
        create_tables(engine)

        import_csv(engine, "customers")

        import_csv(engine, "products")

        import_csv(
            engine,
            "orders",
            [
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "order_estimated_delivery_date"
            ]
        )

        import_csv(
            engine,
            "order_items",
            ["shipping_limit_date"]
        )

        import_csv(engine, "payments")

        print("\nAll Olist datasets imported successfully!")

    except Exception as error:
        print("\nImport failed:", error)
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    import_all()

