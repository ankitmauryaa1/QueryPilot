
from sqlalchemy import text
from database.connection import get_engine
from datetime import date


def create_tables(connection):

    queries = [

        """
        CREATE TABLE IF NOT EXISTS api_products (
            product_id INT PRIMARY KEY,
            title VARCHAR(255),
            category VARCHAR(100),
            brand VARCHAR(150),
            price DECIMAL(12,2),
            discount_percentage DECIMAL(8,2),
            rating DECIMAL(5,2),
            stock INT,
            sku VARCHAR(100),
            availability_status VARCHAR(100)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS api_users (
            user_id INT PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            age INT,
            gender VARCHAR(30),
            email VARCHAR(255),
            phone VARCHAR(100),
            username VARCHAR(100),
            university VARCHAR(255),
            company_name VARCHAR(255),
            department VARCHAR(150),
            job_title VARCHAR(150),
            city VARCHAR(100),
            state VARCHAR(100),
            country VARCHAR(100)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS api_carts (
            cart_id INT PRIMARY KEY,
            user_id INT,
            total DECIMAL(12,2),
            discounted_total DECIMAL(12,2),
            total_products INT,
            total_quantity INT,
            FOREIGN KEY (user_id)
                REFERENCES api_users(user_id)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS api_cart_items (
            cart_id INT,
            product_id INT,
            title VARCHAR(255),
            price DECIMAL(12,2),
            quantity INT,
            total DECIMAL(12,2),
            discounted_total DECIMAL(12,2),
            PRIMARY KEY (cart_id, product_id),
            FOREIGN KEY (cart_id)
                REFERENCES api_carts(cart_id),
            FOREIGN KEY (product_id)
                REFERENCES api_products(product_id)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS api_product_snapshots (
            product_id INT,
            snapshot_date DATE,
            price DECIMAL(12,2),
            stock INT,
            rating DECIMAL(5,2),
            PRIMARY KEY (product_id, snapshot_date)
        )
        """
    ]

    for query in queries:
        connection.execute(text(query))


def upsert_records(connection, table, records, columns):

    if not records:
        return 0

    column_names = ", ".join(columns)

    placeholders = ", ".join(
        f":{column}" for column in columns
    )

    update_columns = [
        column for column in columns
        if column not in ("product_id", "user_id", "cart_id")
    ]

    # For composite-key tables, update all non-key columns.
    if table == "api_cart_items":
        update_columns = [
            column for column in columns
            if column not in ("cart_id", "product_id")
        ]

    if table == "api_product_snapshots":
        update_columns = [
            column for column in columns
            if column not in ("product_id", "snapshot_date")
        ]

    updates = ", ".join(
        f"{column} = VALUES({column})"
        for column in update_columns
    )

    query = f"""
        INSERT INTO {table} ({column_names})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {updates}
    """

    connection.execute(text(query), records)

    return len(records)


def load_data(transformed):

    engine = get_engine()

    try:
        with engine.begin() as connection:

            create_tables(connection)

            # Load parent tables first to satisfy foreign keys.
            product_count = upsert_records(
                connection,
                "api_products",
                transformed["products"],
                [
                    "product_id", "title", "category", "brand",
                    "price", "discount_percentage", "rating",
                    "stock", "sku", "availability_status"
                ]
            )

            user_count = upsert_records(
                connection,
                "api_users",
                transformed["users"],
                [
                    "user_id", "first_name", "last_name", "age",
                    "gender", "email", "phone", "username",
                    "university", "company_name", "department",
                    "job_title", "city", "state", "country"
                ]
            )

            cart_count = upsert_records(
                connection,
                "api_carts",
                transformed["carts"],
                [
                    "cart_id", "user_id", "total",
                    "discounted_total", "total_products",
                    "total_quantity"
                ]
            )

            item_count = upsert_records(
                connection,
                "api_cart_items",
                transformed["cart_items"],
                [
                    "cart_id", "product_id", "title", "price",
                    "quantity", "total", "discounted_total"
                ]
            )

            # Store one price/stock snapshot per product per day.
            today = date.today()

            snapshots = [
                {
                    "product_id": p["product_id"],
                    "snapshot_date": today,
                    "price": p["price"],
                    "stock": p["stock"],
                    "rating": p["rating"]
                }
                for p in transformed["products"]
            ]

            snapshot_count = upsert_records(
                connection,
                "api_product_snapshots",
                snapshots,
                [
                    "product_id", "snapshot_date",
                    "price", "stock", "rating"
                ]
            )

        print("\n--- MYSQL LOAD SUMMARY ---")
        print("Products:", product_count)
        print("Users:", user_count)
        print("Carts:", cart_count)
        print("Cart Items:", item_count)
        print("Price Snapshots:", snapshot_count)

        print("\nMySQL loading completed successfully!")

        return True

    except Exception as error:
        print("MySQL loading failed:", error)
        raise

    finally:
        engine.dispose()
