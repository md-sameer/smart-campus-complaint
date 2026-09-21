from flask import Blueprint, jsonify, request, session
from utils.auth import department_head_required
from services.complaint_service import (
    get_dept_head_complaints,
    get_complaint_detail,
    update_complaint_status
)

dept_bp = Blueprint("department", __name__)


# ---------------------------------------------------------------------------
# GET /api/department-head/complaints  — list assigned complaints
# ---------------------------------------------------------------------------
@dept_bp.route("/api/department-head/complaints", methods=["GET"])
@department_head_required
def list_complaints():
    head_id = session["head_id"]
    complaints = get_dept_head_complaints(head_id)

    for c in complaints:
        if c.get("date_raised"):
            c["date_raised"] = str(c["date_raised"])

    return jsonify({"complaints": complaints}), 200


# ---------------------------------------------------------------------------
# GET /api/department-head/complaints/<id>  — full detail of one complaint
# ---------------------------------------------------------------------------
@dept_bp.route("/api/department-head/complaints/<int:complaint_id>", methods=["GET"])
@department_head_required
def complaint_detail(complaint_id):
    head_id = session["head_id"]
    complaint, updates = get_complaint_detail(complaint_id)

    if not complaint:
        return jsonify({"success": False, "message": "Complaint not found"}), 404

    # Enforce that this complaint belongs to the logged-in head
    if complaint.get("head_id") != head_id:
        return jsonify({"success": False, "message": "Access denied: this complaint is not assigned to you"}), 403

    for key in ("date_raised", "completion_date"):
        if complaint.get(key):
            complaint[key] = str(complaint[key])

    for u in updates:
        if u.get("updated_at"):
            u["updated_at"] = str(u["updated_at"])

    return jsonify({"complaint": complaint, "updates": updates}), 200


# ---------------------------------------------------------------------------
# PUT /api/department-head/complaints/<id>/status  — update status + remarks
# ---------------------------------------------------------------------------
@dept_bp.route("/api/department-head/complaints/<int:complaint_id>/status", methods=["PUT"])
@department_head_required
def update_status(complaint_id):
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Missing request body"}), 400

    new_status = data.get("status", "").strip()
    action_taken = data.get("action_taken", "").strip()
    resolution_remarks = data.get("resolution_remarks", "").strip()
    completion_date = data.get("completion_date")  # optional, YYYY-MM-DD string or None

    if not new_status:
        return jsonify({"success": False, "message": "status is required"}), 400

    head_id = session["head_id"]
    ok, message = update_complaint_status(
        complaint_id, head_id, new_status, action_taken, resolution_remarks, completion_date
    )

    if not ok:
        status_code = 403 if "not assigned" in message.lower() else 400
        return jsonify({"success": False, "message": message}), status_code

    return jsonify({"success": True, "status": message}), 200
