
from sqlalchemy import text

from database.connection import get_engine
from sql_engine.validator import validate_sql

from ai_engine.sql_generator import regenerate_sql


def execute_sql(query, question=None, max_retries=2):

    engine = get_engine()

    try:

        for attempt in range(max_retries + 1):

            # Validate every generated or corrected query
            is_valid, message = validate_sql(query)

            if not is_valid:
                raise ValueError(
                    f"SQL validation failed: {message}"
                )

            try:

                with engine.connect() as connection:

                    connection.execute(
                        text(
                            "SET SESSION MAX_EXECUTION_TIME = 10000"
                        )
                    )

                    result = connection.execute(text(query))

                    columns = list(result.keys())

                    rows = result.fetchmany(100)

                    return {
                        "columns": columns,
                        "rows": rows,
                        "row_count": len(rows),
                        "executed_sql": query,
                        "attempts": attempt + 1
                    }

            except Exception as error:

                if attempt >= max_retries or not question:
                    raise

                print(
                    f"SQL failed. Attempting correction "
                    f"{attempt + 1}/{max_retries}..."
                )

                query = regenerate_sql(
                    question,
                    query,
                    str(error)
                )

        raise RuntimeError("SQL correction attempts exhausted.")

    finally:
        engine.dispose()
