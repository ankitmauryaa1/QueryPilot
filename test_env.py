from dotenv import load_dotenv
import os

load_dotenv(override=True)

print("Host:", os.getenv("DB_HOST"))
print("User:", os.getenv("DB_USER"))
print("Port:", os.getenv("DB_PORT"))
print("Password loaded:", bool(os.getenv("DB_PASSWORD")))
print("Database:", os.getenv("DB_NAME"))