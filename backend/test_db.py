
# Import the libraries needed for our database connection.
from pathlib import Path
import os

import pymysql
from dotenv import load_dotenv

# Locate and load our backend environment variables.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Retrieve database settings.
host = os.getenv("DB_HOST", "localhost")
port = int(os.getenv("DB_PORT", "3306"))
database = os.getenv("DB_NAME")
username = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

# Check that all required settings are available.
if not all([database, username, password]):
    print("ERROR: Database configuration is incomplete.")
    raise SystemExit(1)

try:
    # Attempt to connect Python directly to MySQL.
    connection = pymysql.connect(
        host=host,
        port=port,
        user=username,
        password=password,
        database=database,
        connect_timeout=5
    )

    print("SUCCESS: Python connected to MySQL!")

    # Close the connection after the test.
    connection.close()

except pymysql.MySQLError as error:
    print("MYSQL CONNECTION FAILED")
    print(error)
