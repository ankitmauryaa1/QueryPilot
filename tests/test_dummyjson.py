from api_pipeline.dummyjson_client import (
    fetch_products,
    fetch_users,
    fetch_carts
)

products = fetch_products()
users = fetch_users()
carts = fetch_carts()

print("\nAPI TEST RESULTS")
print("----------------")
print("Products:", len(products))
print("Users:", len(users))
print("Carts:", len(carts))

assert len(products) > 0
assert len(users) > 0
assert len(carts) > 0

print("\nAll API tests passed!")