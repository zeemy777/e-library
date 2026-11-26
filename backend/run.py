import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
from sqlalchemy import text

from config import Config
from extensions import db

from auth import auth_bp
from library import library_bp
from contact import contact_bp
from admin import admin_bp
from favorites import favorites_bp
from loans import loans_bp
from reviews import reviews_bp


def create_app(config_object=Config):

    app = Flask(__name__)

    # Load configuration.
    app.config.from_object(config_object)

    # Session settings. A Vercel frontend on a different domain needs
    # SameSite=None plus Secure cookies so login sessions survive the
    # cross-origin fetch from the deployed site.
    secure_cookies = os.getenv(
        "SESSION_COOKIE_SECURE", "false"
    ).lower() in {"1", "true", "yes"}

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = os.getenv(
        "SESSION_COOKIE_SAMESITE", "Lax"
    )
    app.config["SESSION_COOKIE_SECURE"] = secure_cookies

    # Allow the local Vite dev server and any explicitly configured Vercel
    # origin. Never use "*" here: credentialed CORS requests require an exact
    # origin, and a wildcard would be rejected by the browser anyway.
    origins = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]

    # Initialize CORS.
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": origins
            }
        },
        supports_credentials=True
    )

    # Initialize database.
    db.init_app(app)

    # Register blueprints.
    app.register_blueprint(auth_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(favorites_bp)
    app.register_blueprint(loans_bp)
    app.register_blueprint(reviews_bp)

    # Backend health check.
    @app.route("/api/health", methods=["GET"])
    def health_check():

        return jsonify({
            "status": "success",
            "message": "E-Library backend is running!"
        })

    # Database health check.
    @app.route("/api/db-health", methods=["GET"])
    def database_health():

        try:
            with db.engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            return jsonify({
                "status": "success",
                "message": "MySQL connection successful!"
            })

        except Exception:

            app.logger.exception(
                "Database connection failed"
            )

            return jsonify({
                "status": "error",
                "message": "Could not connect to MySQL."
            }), 500

    # Serve the production React build so the whole site runs
    # from this one Flask server (no separate Vite dev server).
    frontend_dist = Config.FRONTEND_DIST

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def frontend_files(path):

        # Unknown API routes should stay JSON, not the SPA shell.
        if path.startswith("api/"):
            return jsonify({
                "status": "error",
                "message": "Not found."
            }), 404

        requested = frontend_dist / path

        if path and requested.is_file():
            return send_from_directory(frontend_dist, path)

        return send_from_directory(frontend_dist, "index.html")

    return app


app = create_app()


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )