# app.py
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config
from models import db
from routes.ferc import ferc_bp
from routes.proforma import proforma_bp
from routes.debt import debt_bp
from routes.gpt import gpt_bp
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app)  # Enable CORS if needed

    # Register blueprints
    app.register_blueprint(ferc_bp)
    app.register_blueprint(proforma_bp)
    app.register_blueprint(debt_bp)
    app.register_blueprint(gpt_bp)

    # Serve the frontend interface
    @app.route('/')
    def index():
        return send_from_directory('templates', 'query_interface.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
