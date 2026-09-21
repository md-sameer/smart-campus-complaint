from functools import wraps
from flask import session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def hash_password(plain_text_password):
    """Hash a plain-text password using Werkzeug (bcrypt-based)."""
    return generate_password_hash(plain_text_password)


def verify_password(plain_text_password, password_hash):
    """Check a plain-text password against a stored hash."""
    return check_password_hash(password_hash, plain_text_password)


# ---------------------------------------------------------------------------
# Session / role-check decorators
# ---------------------------------------------------------------------------

def student_required(f):
    """Decorator: endpoint accessible only to authenticated students."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "student":
            return jsonify({"success": False, "message": "Authentication required. Please log in as a student."}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator: endpoint accessible only to authenticated admins."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "admin":
            return jsonify({"success": False, "message": "Authentication required. Please log in as admin."}), 401
        return f(*args, **kwargs)
    return decorated


def department_head_required(f):
    """Decorator: endpoint accessible only to authenticated department heads."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "department_head":
            return jsonify({"success": False, "message": "Authentication required. Please log in as a department head."}), 401
        return f(*args, **kwargs)
    return decorated
