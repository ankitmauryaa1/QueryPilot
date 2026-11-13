
from api_pipeline.dummyjson_client import (
    fetch_products,
    fetch_users,
    fetch_carts
)

from api_pipeline.transform import transform_all
from api_pipeline.load_mysql import load_data


print("STEP 1: Fetching API data...")

products = fetch_products()
users = fetch_users()
carts = fetch_carts()


print("STEP 2: Transforming data...")

transformed = transform_all(
    products,
    users,
    carts
)


print("STEP 3: Loading into MySQL...")

load_data(transformed)


print("\nComplete API pipeline executed successfully!")
