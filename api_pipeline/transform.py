
def transform_products(products):
    cleaned = []

    for p in products:
        cleaned.append({
            "product_id": p.get("id"),
            "title": p.get("title"),
            "category": p.get("category"),
            "brand": p.get("brand"),
            "price": p.get("price"),
            "discount_percentage": p.get("discountPercentage"),
            "rating": p.get("rating"),
            "stock": p.get("stock"),
            "sku": p.get("sku"),
            "availability_status": p.get("availabilityStatus")
        })

    return cleaned


def transform_users(users):
    cleaned = []

    for u in users:
        address = u.get("address") or {}
        company = u.get("company") or {}

        cleaned.append({
            "user_id": u.get("id"),
            "first_name": u.get("firstName"),
            "last_name": u.get("lastName"),
            "age": u.get("age"),
            "gender": u.get("gender"),
            "email": u.get("email"),
            "phone": u.get("phone"),
            "username": u.get("username"),
            "university": u.get("university"),
            "company_name": company.get("name"),
            "department": company.get("department"),
            "job_title": company.get("title"),
            "city": address.get("city"),
            "state": address.get("state"),
            "country": address.get("country")
        })

    return cleaned


def transform_carts(carts):
    cleaned = []

    for c in carts:
        cleaned.append({
            "cart_id": c.get("id"),
            "user_id": c.get("userId"),
            "total": c.get("total"),
            "discounted_total": c.get("discountedTotal"),
            "total_products": c.get("totalProducts"),
            "total_quantity": c.get("totalQuantity")
        })

    return cleaned


def transform_cart_items(carts):
    cleaned = []

    for cart in carts:
        for product in cart.get("products", []):
            cleaned.append({
                "cart_id": cart.get("id"),
                "product_id": product.get("id"),
                "title": product.get("title"),
                "price": product.get("price"),
                "quantity": product.get("quantity"),
                "total": product.get("total"),
                "discounted_total": product.get("discountedTotal")
            })

    return cleaned


def transform_all(products, users, carts):

    transformed = {
        "products": transform_products(products),
        "users": transform_users(users),
        "carts": transform_carts(carts),
        "cart_items": transform_cart_items(carts)
    }

    print("\n--- TRANSFORMATION SUMMARY ---")

    for table, records in transformed.items():
        print(f"{table}: {len(records)} records")

    return transformed
