from flask import Blueprint, jsonify, request, session
from database import get_connection
from utils.auth import student_required
from services.complaint_service import submit_complaint, get_student_complaints

student_bp = Blueprint("student", __name__)


# ---------------------------------------------------------------------------
# GET /api/student/profile
# ---------------------------------------------------------------------------
@student_bp.route("/api/student/profile", methods=["GET"])
@student_required
def get_profile():
    register_number = session["register_number"]
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT register_number, student_name, department, year, section, email, phone_number FROM students WHERE register_number = %s",
            (register_number,)
        )
        student = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not student:
        return jsonify({"success": False, "message": "Student not found"}), 404

    return jsonify(student), 200


# ---------------------------------------------------------------------------
# POST /api/complaints  — submit a new complaint
# ---------------------------------------------------------------------------
@student_bp.route("/api/complaints", methods=["POST"])
@student_required
def create_complaint():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Missing request body"}), 400

    category = data.get("category", "").strip()
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()

    if not category or not title or not description:
        return jsonify({"success": False, "message": "category, title, and description are required"}), 400

    register_number = session["register_number"]
    complaint_id = submit_complaint(register_number, category, title, description)

    return jsonify({
        "success": True,
        "complaint_id": complaint_id,
        "status": "Pending"
    }), 201


# ---------------------------------------------------------------------------
# GET /api/student/complaints  — list own complaints
# ---------------------------------------------------------------------------
@student_bp.route("/api/student/complaints", methods=["GET"])
@student_required
def list_my_complaints():
    register_number = session["register_number"]
    complaints = get_student_complaints(register_number)

    # Convert datetime objects to strings for JSON serialisation
    for c in complaints:
        if c.get("date_raised"):
            c["date_raised"] = str(c["date_raised"])
        if c.get("completion_date"):
            c["completion_date"] = str(c["completion_date"])

    return jsonify({"complaints": complaints}), 200
