
from api_pipeline.dummyjson_client import (
    fetch_products,
    fetch_users,
    fetch_carts
)

from api_pipeline.transform import transform_all


products = fetch_products()
users = fetch_users()
carts = fetch_carts()

result = transform_all(products, users, carts)

print("\n--- TESTING TRANSFORMED DATA ---")

for table, records in result.items():
    assert isinstance(records, list)

    if records:
        print(f"\n{table} - First record:")
        print(records[0])

print("\nTransformation test passed!")
