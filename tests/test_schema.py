
from database.connection import get_engine
from database.schema_detector import (
    detect_schema,
    display_schema
)


if __name__ == "__main__":

    engine = get_engine()

    try:
        schema = detect_schema(engine)

        display_schema(schema)

    finally:
        engine.dispose()
