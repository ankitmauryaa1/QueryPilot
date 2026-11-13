
import sqlglot
from sqlglot import exp


FORBIDDEN_EXPRESSIONS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Alter,
    exp.Create,
    exp.TruncateTable,
    exp.Merge,
    exp.Command,
)


def validate_sql(query):

    if not query or not query.strip():
        return False, "SQL query is empty."

    try:
        # Parse all statements
        statements = sqlglot.parse(
            query,
            read="mysql"
        )

        # Reject multiple statements
        if len(statements) != 1 or statements[0] is None:
            return False, "Only one SQL statement is allowed."

        parsed = statements[0]

        # Allow SELECT and read-only CTE queries
        if not isinstance(parsed, exp.Select):
            return False, "Only SELECT queries are allowed."

        # Inspect every expression in the query
        for node in parsed.walk():

            if isinstance(node, FORBIDDEN_EXPRESSIONS):
                return False, (
                    f"Forbidden SQL operation: "
                    f"{type(node).__name__}"
                )

            # Reject SELECT ... INTO
            if isinstance(node, exp.Into):
                return False, "SELECT INTO is not allowed."

            # Reject locking reads
            if isinstance(node, exp.Lock):
                return False, "Locking queries are not allowed."

        return True, "SQL query passed validation."

    except Exception as error:

        return False, f"Invalid SQL syntax: {error}"
