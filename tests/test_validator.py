
from sql_engine.validator import validate_sql


test_queries = [

    "SELECT * FROM olist_customers",

    """
    SELECT customer_city, COUNT(*)
    FROM olist_customers
    GROUP BY customer_city
    """,

    "DELETE FROM olist_customers",

    "DROP TABLE olist_customers",

    "UPDATE olist_customers SET customer_city = 'Delhi'",

    "SELECT * FROM olist_customers; DROP TABLE olist_customers",

    """
    WITH city_orders AS (
        SELECT customer_id
        FROM olist_orders
    )
    SELECT * FROM city_orders
    """
]


for query in test_queries:

    is_valid, message = validate_sql(query)

    print("\nQuery:", query.strip())
    print("Valid:", is_valid)
    print("Message:", message)
