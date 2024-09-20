from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from models import db
from routes.ferc import ferc_bp
from routes.proforma import proforma_bp
from routes.debt import debt_bp
from routes.gpt import gpt_bp
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from sqlalchemy.exc import OperationalError

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with retry
    initialize_database(app)
    migrate = Migrate(app, db)

    CORS(app)  # Enable CORS if needed

    # Register blueprints with URL prefixes
    app.register_blueprint(ferc_bp, url_prefix='/api/ferc')
    app.register_blueprint(proforma_bp, url_prefix='/api/proforma')
    app.register_blueprint(debt_bp, url_prefix='/api/debt')
    app.register_blueprint(gpt_bp, url_prefix='/api/query')  # Set the prefix for GPT-related queries

    # Serve the frontend interface
    @app.route('/')
    def index():
        return send_from_directory('templates', 'query_interface.html')

    return app

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(OperationalError),
    reraise=True
)
def initialize_database(app):
    """
    Initializes the database with retry logic to handle delayed startups.
    """
    try:
        db.init_app(app)
        with app.app_context():
            db.create_all()
            print("Database tables created successfully.")
    except OperationalError as e:
        print(f"Attempt to initialize database failed: {e}")
        raise  # Trigger the retry

if __name__ == '__main__':
    try:
        app = create_app()
        app.run(debug=True)
    except OperationalError as e:
        print(f"Failed to start the Flask app due to database connection issues: {e}")
