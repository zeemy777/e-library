
# Import tools for handling environment variables and file paths.
import os
from pathlib import Path

# Load environment variables from our backend/.env file.
from dotenv import load_dotenv

# SQLAlchemy URL builder safely handles special characters
# in database passwords.
from sqlalchemy import URL


# Locate and load the backend environment file.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    # Flask security key for sessions and authentication.
    # The name must match the .env entry exactly on every platform.
    SECRET_KEY = os.getenv("APP_SECRET_KEY")

    # Folder where uploaded book files are stored.
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")

    # Production React build served by Flask (project_root/frontend/dist).
    FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"

    # Configure the MySQL database connection.
    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "e_library")
    )

    # Disable unnecessary modification tracking.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
