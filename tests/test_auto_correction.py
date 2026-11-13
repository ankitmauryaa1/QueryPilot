
from sql_engine.executor import execute_sql


if __name__ == "__main__":

    question = (
        "Show the top 5 cities by total revenue."
    )

    # Intentionally incorrect column name
    bad_sql = """
    SELECT
        c.customer_city,
        SUM(p.wrong_column) AS revenue
    FROM olist_customers c
    JOIN olist_orders o
        ON c.customer_id = o.customer_id
    JOIN olist_payments p
        ON o.order_id = p.order_id
    GROUP BY c.customer_city
    ORDER BY revenue DESC
    LIMIT 5
    """

    try:

        result = execute_sql(
            bad_sql,
            question=question,
            max_retries=2
        )

        print("\nCorrected SQL:")
        print(result["executed_sql"])

        print("\nResults:")

        for row in result["rows"]:
            print(row)

        print("\nCorrection attempts:", result["attempts"])

    except Exception as error:

        print("\nAuto-correction failed:", error)
