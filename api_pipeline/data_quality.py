
def check_data_quality(transformed):

    report = {
        "status": "PASSED",
        "errors": [],
        "warnings": [],
        "record_counts": {}
    }

    # 1. Check record counts
    for table, records in transformed.items():
        report["record_counts"][table] = len(records)

        if not records:
            report["warnings"].append(
                f"{table} contains no records."
            )

    # 2. Check duplicate product IDs
    products = transformed["products"]
    product_ids = [
        p["product_id"] for p in products
    ]

    if len(product_ids) != len(set(product_ids)):
        report["errors"].append(
            "Duplicate product IDs detected."
        )

    # 3. Check duplicate user IDs
    users = transformed["users"]
    user_ids = [u["user_id"] for u in users]

    if len(user_ids) != len(set(user_ids)):
        report["errors"].append(
            "Duplicate user IDs detected."
        )

    # 4. Check duplicate cart IDs
    carts = transformed["carts"]
    cart_ids = [c["cart_id"] for c in carts]

    if len(cart_ids) != len(set(cart_ids)):
        report["errors"].append(
            "Duplicate cart IDs detected."
        )

    # 5. Check required IDs
    for product in products:
        if product["product_id"] is None:
            report["errors"].append(
                "Product with missing ID detected."
            )
            break

    for user in users:
        if user["user_id"] is None:
            report["errors"].append(
                "User with missing ID detected."
            )
            break

    # 6. Check cart relationships
    user_id_set = set(user_ids)

    for cart in carts:
        if cart["user_id"] not in user_id_set:
            report["errors"].append(
                f"Cart {cart['cart_id']} references "
                "a user that does not exist."
            )
            break

    # 7. Check cart item relationships
    cart_id_set = set(cart_ids)
    product_id_set = set(product_ids)

    for item in transformed["cart_items"]:

        if item["cart_id"] not in cart_id_set:
            report["errors"].append(
                "Cart item references a missing cart."
            )
            break

        if item["product_id"] not in product_id_set:
            report["errors"].append(
                "Cart item references a missing product."
            )
            break

    # 8. Check numeric product values
    for product in products:

        if product["price"] is not None and product["price"] < 0:
            report["errors"].append(
                f"Invalid negative price for product "
                f"{product['product_id']}."
            )
            break

        if product["stock"] is not None and product["stock"] < 0:
            report["errors"].append(
                f"Invalid negative stock for product "
                f"{product['product_id']}."
            )
            break

    if report["errors"]:
        report["status"] = "FAILED"

    print("\n--- DATA QUALITY REPORT ---")
    print("Status:", report["status"])

    for table, count in report["record_counts"].items():
        print(f"{table}: {count} records")

    for error in report["errors"]:
        print("ERROR:", error)

    for warning in report["warnings"]:
        print("WARNING:", warning)

    return report
