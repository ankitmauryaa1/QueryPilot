
import requests

BASE_URL = "https://dummyjson.com"


def fetch_data(endpoint):
    """
    Fetch all records from a DummyJSON endpoint.
    """
    url = f"{BASE_URL}/{endpoint}"

    try:
        response = requests.get(
            url,
            params={"limit": 0},
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        print(f"Successfully fetched {endpoint}")

        return data

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Failed to fetch {endpoint}: {error}"
        ) from error


def fetch_products():
    data = fetch_data("products")
    return data.get("products", [])


def fetch_users():
    data = fetch_data("users")
    return data.get("users", [])


def fetch_carts():
    data = fetch_data("carts")
    return data.get("carts", [])


if __name__ == "__main__":

    products = fetch_products()
    users = fetch_users()
    carts = fetch_carts()

    print("\n--- API FETCH SUMMARY ---")
    print("Products:", len(products))
    print("Users:", len(users))
    print("Carts:", len(carts))

    if products:
        print("\nFirst product:")
        print(products[0])
