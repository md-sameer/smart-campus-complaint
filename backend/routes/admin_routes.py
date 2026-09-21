from flask import Blueprint, jsonify, request, session
from database import get_connection
from utils.auth import admin_required
from services.complaint_service import get_all_complaints, get_complaint_detail, assign_complaint

admin_bp = Blueprint("admin", __name__)


# ---------------------------------------------------------------------------
# GET /api/admin/complaints  — list all complaints (with optional filters)
# ---------------------------------------------------------------------------
@admin_bp.route("/api/admin/complaints", methods=["GET"])
@admin_required
def list_complaints():
    status = request.args.get("status")
    category = request.args.get("category")
    search = request.args.get("search")

    complaints = get_all_complaints(status=status, category=category, search=search)

    # Serialise datetime fields
    for c in complaints:
        if c.get("date_raised"):
            c["date_raised"] = str(c["date_raised"])
        if c.get("completion_date"):
            c["completion_date"] = str(c["completion_date"])

    return jsonify({"complaints": complaints}), 200


# ---------------------------------------------------------------------------
# GET /api/admin/complaints/<id>  — full detail of one complaint
# ---------------------------------------------------------------------------
@admin_bp.route("/api/admin/complaints/<int:complaint_id>", methods=["GET"])
@admin_required
def complaint_detail(complaint_id):
    complaint, updates = get_complaint_detail(complaint_id)
    if not complaint:
        return jsonify({"success": False, "message": "Complaint not found"}), 404

    # Serialise datetimes
    for key in ("date_raised", "completion_date"):
        if complaint.get(key):
            complaint[key] = str(complaint[key])

    for u in updates:
        if u.get("updated_at"):
            u["updated_at"] = str(u["updated_at"])

    return jsonify({
        "complaint": complaint,
        "updates": updates
    }), 200


# ---------------------------------------------------------------------------
# PUT /api/admin/complaints/<id>/assign  — assign to department + head
# ---------------------------------------------------------------------------
@admin_bp.route("/api/admin/complaints/<int:complaint_id>/assign", methods=["PUT"])
@admin_required
def assign(complaint_id):
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Missing request body"}), 400

    department_id = data.get("department_id")
    head_id = data.get("head_id")

    if department_id is None or head_id is None:
        return jsonify({"success": False, "message": "department_id and head_id are required"}), 400

    admin_id = session["admin_id"]
    ok, message = assign_complaint(complaint_id, department_id, head_id, admin_id)

    if not ok:
        status_code = 404 if "not found" in message.lower() else 400
        return jsonify({"success": False, "message": message}), status_code

    return jsonify({"success": True, "status": "Assigned"}), 200


# ---------------------------------------------------------------------------
# GET /api/admin/departments  — list departments + their heads (for dropdowns)
# ---------------------------------------------------------------------------
@admin_bp.route("/api/admin/departments", methods=["GET"])
@admin_required
def list_departments():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT department_id, department_name FROM departments ORDER BY department_name")
        departments = cursor.fetchall()

        cursor.execute(
            "SELECT head_id, full_name, username, department_id FROM department_heads ORDER BY full_name"
        )
        heads = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return jsonify({"departments": departments, "department_heads": heads}), 200


# ---------------------------------------------------------------------------
# GET /api/admin/stats  — overview counts by status (for dashboard cards)
# ---------------------------------------------------------------------------
@admin_bp.route("/api/admin/stats", methods=["GET"])
@admin_required
def stats():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM complaints
            GROUP BY status
            """
        )
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    counts = {row["status"]: row["count"] for row in rows}
    return jsonify({
        "total": sum(counts.values()),
        "pending": counts.get("Pending", 0),
        "assigned": counts.get("Assigned", 0),
        "in_progress": counts.get("In Progress", 0),
        "completed": counts.get("Completed", 0),
        "not_completed": counts.get("Not Completed", 0)
    }), 200
