
from ai_engine.sql_generator import generate_sql


if __name__ == "__main__":

    question = (
        "Show the top 10 cities by total revenue."
    )

    sql_query = generate_sql(question)

    print("\nUser Question:")
    print(question)

    print("\nGenerated SQL:")
    print(sql_query)
