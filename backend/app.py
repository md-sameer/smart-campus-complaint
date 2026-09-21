from flask import Flask
from config import Config
from routes.auth_routes import auth_bp
from routes.student_routes import student_bp
from routes.admin_routes import admin_bp
from routes.department_routes import dept_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    # Allow frontend (running on a different port) to call our APIs
    try:
        from flask_cors import CORS
        CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5500", "http://localhost:5500", "null"])
    except ImportError:
        print("[WARNING] flask-cors not installed. Install it with: pip install flask-cors")

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(dept_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    print("=" * 50)
    print(" Smart Campus Complaint System — Backend")
    print(" Running at: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)
