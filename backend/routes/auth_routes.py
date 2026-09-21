from flask import Blueprint, request, jsonify, session
from database import get_connection
from utils.auth import hash_password, verify_password

auth_bp = Blueprint("auth", __name__)


# ---------------------------------------------------------------------------
# POST /api/student/login
# ---------------------------------------------------------------------------
@auth_bp.route("/api/student/login", methods=["POST"])
def student_login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Missing request body"}), 400

    register_number = data.get("register_number", "").strip()
    password = data.get("password", "")

    if not register_number or not password:
        return jsonify({"success": False, "message": "register_number and password are required"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM students WHERE register_number = %s", (register_number,))
        student = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not student or not verify_password(password, student["password_hash"]):
        return jsonify({"success": False, "message": "Invalid register number or password"}), 401

    # Set session
    session.clear()
    session["role"] = "student"
    session["register_number"] = student["register_number"]

    return jsonify({
        "success": True,
        "student": {
            "register_number": student["register_number"],
            "student_name": student["student_name"],
            "department": student["department"],
            "year": student["year"],
            "section": student["section"],
            "email": student["email"],
            "phone_number": student["phone_number"]
        }
    }), 200


# ---------------------------------------------------------------------------
# POST /api/admin/login
# ---------------------------------------------------------------------------
@auth_bp.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Missing request body"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"success": False, "message": "username and password are required"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
        admin = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not admin or not verify_password(password, admin["password_hash"]):
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

    session.clear()
    session["role"] = "admin"
    session["admin_id"] = admin["admin_id"]

    return jsonify({
        "success": True,
        "admin": {
            "admin_id": admin["admin_id"],
            "username": admin["username"],
            "full_name": admin["full_name"]
        }
    }), 200


# ---------------------------------------------------------------------------
# POST /api/department-head/login
# ---------------------------------------------------------------------------
@auth_bp.route("/api/department-head/login", methods=["POST"])
def dept_head_login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Missing request body"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"success": False, "message": "username and password are required"}), 400

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT dh.*, d.department_name
            FROM department_heads dh
            JOIN departments d ON dh.department_id = d.department_id
            WHERE dh.username = %s
            """,
            (username,)
        )
        head = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not head or not verify_password(password, head["password_hash"]):
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

    session.clear()
    session["role"] = "department_head"
    session["head_id"] = head["head_id"]
    session["department_id"] = head["department_id"]

    return jsonify({
        "success": True,
        "head": {
            "head_id": head["head_id"],
            "username": head["username"],
            "full_name": head["full_name"],
            "department": head["department_name"],
            "department_id": head["department_id"]
        }
    }), 200


# ---------------------------------------------------------------------------
# POST /api/logout  (works for all roles)
# ---------------------------------------------------------------------------
@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"}), 200
