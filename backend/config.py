import os

class Config:
    # Flask secret key (used for session management)
    SECRET_KEY = os.environ.get("SECRET_KEY", "smart-campus-secret-key-change-in-production")

    # MySQL Database Configuration
    # ⚠️ CHANGE THESE VALUES to match your local MySQL setup
    MYSQL_HOST = "localhost"
    MYSQL_PORT = 3306
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "your_mysql_password_here"   # <-- CHANGE THIS
    MYSQL_DATABASE = "smart_campus_complaint"
