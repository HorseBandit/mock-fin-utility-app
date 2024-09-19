# db_connection_verify.py

from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy import text
import os
import pyodbc
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load environment variables from the .env file
def load_env_vars():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    # elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")  # Uncomment if used
    db_connection_string = os.getenv("DATABASE_URL")

    if not api_key or not db_connection_string:
        raise ValueError("Missing required environment variables.")

    return api_key, db_connection_string

# Load environment variables
api_key, db_connection_string = load_env_vars()

app.config['SQLALCHEMY_DATABASE_URI'] = db_connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking

# Initialize SQLAlchemy instance
db = SQLAlchemy(app)

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),  # Waits 2, 4, 8, ... seconds
    stop=stop_after_attempt(5),                          # Tries 5 times
    retry=retry_if_exception_type(OperationalError),      # Retries only on OperationalError
    reraise=True                                         # Raises the exception after retries are exhausted
)
def test_db_connection():
    """
    Attempts to connect to the database and retrieve its version.
    Retries on OperationalError with exponential backoff.
    """
    try:
        with app.app_context():  # Ensure the app context is available
            result = db.session.execute(text("SELECT @@version"))
            version_info = result.fetchone()
            print(f"Database version: {version_info[0]}")
            return True
    except OperationalError as e:
        print(f"Attempt failed with error: {e}")
        raise  # Trigger the retry

def main():
    try:
        test_db_connection()
        print("Database connection successful.")
    except OperationalError as e:
        print(f"Error occurred during startup DB connection test after retries: {e}")

if __name__ == "__main__":
    main()
