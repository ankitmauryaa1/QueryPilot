
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw/olist")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def prepare_dataset():

    print("Loading Olist datasets...")

    customers = pd.read_csv(
        RAW_DIR / "olist_customers_dataset.csv"
    )

    products = pd.read_csv(
        RAW_DIR / "olist_products_dataset.csv"
    )

    orders = pd.read_csv(
        RAW_DIR / "olist_orders_dataset.csv"
    )

    order_items = pd.read_csv(
        RAW_DIR / "olist_order_items_dataset.csv"
    )

    payments = pd.read_csv(
        RAW_DIR / "olist_order_payments_dataset.csv"
    )

    print("All datasets loaded successfully!")

    # Select up to 10,000 real orders
    selected_orders = orders.head(10000).copy()

    # Get selected order IDs
    order_ids = selected_orders["order_id"]

    # Keep related order items
    selected_items = order_items[
        order_items["order_id"].isin(order_ids)
    ].copy()

    # Keep customers belonging to selected orders
    customer_ids = selected_orders[
        "customer_id"
    ].unique()

    selected_customers = customers[
        customers["customer_id"].isin(customer_ids)
    ].copy()

    # Keep products belonging to selected order items
    product_ids = selected_items[
        "product_id"
    ].unique()

    selected_products = products[
        products["product_id"].isin(product_ids)
    ].copy()

    # Keep corresponding payments
    selected_payments = payments[
        payments["order_id"].isin(order_ids)
    ].copy()

    datasets = {
        "customers": selected_customers,
        "products": selected_products,
        "orders": selected_orders,
        "order_items": selected_items,
        "payments": selected_payments
    }

    print("\nSaving processed datasets...")

    for table_name, df in datasets.items():

        output_path = PROCESSED_DIR / f"{table_name}.csv"

        df.to_csv(output_path, index=False)

        print(
            f"{table_name}: {len(df):,} rows saved"
        )

    print("\nDataset preparation completed!")


if __name__ == "__main__":
    prepare_dataset()
