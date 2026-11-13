
from ai_engine.sql_generator import generate_sql
from sql_engine.executor import execute_sql


if __name__ == "__main__":

    question = "Show the top 10 cities by total revenue."

    print("\nUser Question:")
    print(question)

    sql_query = generate_sql(question)

    print("\nGenerated SQL:")
    print(sql_query)

    try:
        result = execute_sql(sql_query)

        print("\nQuery Results:")

        for row in result["rows"]:
            print(row)

        print("\nRows returned:", result["row_count"])

    except Exception as error:
        print("\nExecution failed:", error)
