
from sqlalchemy import inspect, text


def detect_schema(engine):
    """
    Detect all tables, columns, data types,
    primary keys and foreign keys in MySQL.
    """

    inspector = inspect(engine)

    schema = {}

    tables = inspector.get_table_names()

    for table_name in tables:

        columns = inspector.get_columns(table_name)

        primary_keys = inspector.get_pk_constraint(table_name)

        foreign_keys = inspector.get_foreign_keys(table_name)

        column_details = []

        for column in columns:

            column_details.append({
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"],
                "primary_key": (
                    column["name"] in primary_keys.get(
                        "constrained_columns", []
                    )
                )
            })

        foreign_key_details = []

        for fk in foreign_keys:

            foreign_key_details.append({
                "columns": fk["constrained_columns"],
                "referenced_table": fk["referred_table"],
                "referenced_columns": fk["referred_columns"]
            })

        # Get record count
        quoted_table = (
            engine.dialect.identifier_preparer
            .quote(table_name)
        )

        with engine.connect() as connection:

            row_count = connection.execute(
                text(f"SELECT COUNT(*) FROM {quoted_table}")
            ).scalar_one()

        schema[table_name] = {
            "columns": column_details,
            "foreign_keys": foreign_key_details,
            "row_count": row_count
        }

    return schema


def display_schema(schema):

    for table_name, details in schema.items():

        print(f"\nTABLE: {table_name}")
        print(f"ROWS: {details['row_count']}")

        print("\nCOLUMNS:")

        for column in details["columns"]:

            print(
                f"{column['name']} | "
                f"{column['type']} | "
                f"Nullable: {column['nullable']} | "
                f"Primary Key: {column['primary_key']}"
            )

        print("\nFOREIGN KEYS:")

        for fk in details["foreign_keys"]:

            print(
                f"{fk['columns']} -> "
                f"{fk['referenced_table']}."
                f"{fk['referenced_columns']}"
            )
