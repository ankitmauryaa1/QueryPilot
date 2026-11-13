from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from config.settings import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME
)


def get_engine():

    connection_url = URL.create(
        drivername="mysql+mysqlconnector",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )

    engine = create_engine(
        connection_url,
        pool_pre_ping=True
    )

    return engine


def test_connection():

    engine = get_engine()

    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT VERSION(), DATABASE()")
            )

            version, database = result.fetchone()

            print("MySQL connected successfully!")
            print("MySQL Version:", version)
            print("Database:", database)

            return True

    except Exception as error:

        print("Database connection failed!")
        print("Error:", error)

        return False

    finally:
        engine.dispose()