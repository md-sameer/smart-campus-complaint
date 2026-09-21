from database import get_connection


# ---------------------------------------------------------------------------
# Status transition rules
# ---------------------------------------------------------------------------

VALID_DEPT_HEAD_STATUSES = {"In Progress", "Completed", "Not Completed"}


def submit_complaint(register_number, category, title, description):
    """Insert a new complaint for a student. Returns complaint_id on success."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO complaints (register_number, category, title, description, status)
            VALUES (%s, %s, %s, %s, 'Pending')
        """
        cursor.execute(sql, (register_number, category, title, description))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def get_student_complaints(register_number):
    """Return all complaints belonging to a specific student."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT
                c.complaint_id,
                c.category,
                c.title,
                c.description,
                c.status,
                c.date_raised,
                c.resolution_remarks,
                c.completion_date,
                d.department_name AS department
            FROM complaints c
            LEFT JOIN departments d ON c.department_id = d.department_id
            WHERE c.register_number = %s
            ORDER BY c.date_raised DESC
        """
        cursor.execute(sql, (register_number,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_all_complaints(status=None, category=None, search=None):
    """Return all complaints, optionally filtered. Used by Admin."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT
                c.complaint_id,
                c.category,
                c.title,
                c.description,
                c.status,
                c.priority,
                c.date_raised,
                c.resolution_remarks,
                c.completion_date,
                s.student_name,
                s.register_number,
                s.department AS student_department,
                d.department_name AS assigned_department,
                dh.full_name AS assigned_head_name
            FROM complaints c
            JOIN students s ON c.register_number = s.register_number
            LEFT JOIN departments d ON c.department_id = d.department_id
            LEFT JOIN department_heads dh ON c.head_id = dh.head_id
            WHERE 1=1
        """
        params = []

        if status:
            sql += " AND c.status = %s"
            params.append(status)
        if category:
            sql += " AND c.category = %s"
            params.append(category)
        if search:
            sql += " AND (c.title LIKE %s OR s.student_name LIKE %s OR s.register_number LIKE %s)"
            like = f"%{search}%"
            params.extend([like, like, like])

        sql += " ORDER BY c.date_raised DESC"
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_complaint_detail(complaint_id):
    """Return full detail of a single complaint including student info and update history."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Complaint + student + assigned info
        sql = """
            SELECT
                c.*,
                s.student_name,
                s.department AS student_department,
                s.year,
                s.section,
                s.email,
                s.phone_number,
                d.department_name AS assigned_department,
                dh.full_name AS assigned_head_name
            FROM complaints c
            JOIN students s ON c.register_number = s.register_number
            LEFT JOIN departments d ON c.department_id = d.department_id
            LEFT JOIN department_heads dh ON c.head_id = dh.head_id
            WHERE c.complaint_id = %s
        """
        cursor.execute(sql, (complaint_id,))
        complaint = cursor.fetchone()
        if not complaint:
            return None, None

        # Update history
        history_sql = """
            SELECT * FROM complaint_updates
            WHERE complaint_id = %s
            ORDER BY updated_at ASC
        """
        cursor.execute(history_sql, (complaint_id,))
        updates = cursor.fetchall()
        return complaint, updates
    finally:
        cursor.close()
        conn.close()


def assign_complaint(complaint_id, department_id, head_id, admin_id):
    """
    Assign a complaint to a department + department head.
    Sets status to 'Assigned' and logs the change in complaint_updates.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch current status
        cursor.execute("SELECT status FROM complaints WHERE complaint_id = %s", (complaint_id,))
        row = cursor.fetchone()
        if not row:
            return False, "Complaint not found"

        old_status = row["status"]

        # Validate department exists
        cursor.execute("SELECT department_id FROM departments WHERE department_id = %s", (department_id,))
        if not cursor.fetchone():
            return False, "Invalid department"

        # Validate department head belongs to that department
        cursor.execute(
            "SELECT head_id FROM department_heads WHERE head_id = %s AND department_id = %s",
            (head_id, department_id)
        )
        if not cursor.fetchone():
            return False, "Invalid department head for chosen department"

        # Update complaint
        cursor.execute(
            """
            UPDATE complaints
            SET department_id = %s, head_id = %s, status = 'Assigned'
            WHERE complaint_id = %s
            """,
            (department_id, head_id, complaint_id)
        )

        # Log status change
        cursor.execute(
            """
            INSERT INTO complaint_updates
                (complaint_id, old_status, new_status, updated_by_role, updated_by_id, remarks)
            VALUES (%s, %s, 'Assigned', 'admin', %s, 'Complaint assigned to department')
            """,
            (complaint_id, old_status, admin_id)
        )
        conn.commit()
        return True, "Assigned"
    finally:
        cursor.close()
        conn.close()


def get_dept_head_complaints(head_id):
    """Return complaints assigned to a specific department head."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT
                c.complaint_id,
                c.category,
                c.title,
                c.description,
                c.status,
                c.priority,
                c.date_raised,
                c.resolution_remarks,
                s.student_name,
                s.register_number
            FROM complaints c
            JOIN students s ON c.register_number = s.register_number
            WHERE c.head_id = %s
            ORDER BY c.date_raised DESC
        """
        cursor.execute(sql, (head_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def update_complaint_status(complaint_id, head_id, new_status, action_taken, resolution_remarks, completion_date):
    """
    Department head updates a complaint's status + resolution info.
    Only allows transitions: Assigned/In Progress → In Progress / Completed / Not Completed.
    """
    if new_status not in VALID_DEPT_HEAD_STATUSES:
        return False, f"Invalid status. Must be one of: {', '.join(VALID_DEPT_HEAD_STATUSES)}"

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Verify this complaint belongs to the logged-in head
        cursor.execute(
            "SELECT status FROM complaints WHERE complaint_id = %s AND head_id = %s",
            (complaint_id, head_id)
        )
        row = cursor.fetchone()
        if not row:
            return False, "Complaint not found or not assigned to you"

        old_status = row["status"]

        # Update complaint
        cursor.execute(
            """
            UPDATE complaints
            SET status = %s,
                resolution_remarks = %s,
                completion_date = %s
            WHERE complaint_id = %s
            """,
            (new_status, resolution_remarks, completion_date, complaint_id)
        )

        # Log status change
        remarks_log = action_taken or resolution_remarks or ""
        cursor.execute(
            """
            INSERT INTO complaint_updates
                (complaint_id, old_status, new_status, updated_by_role, updated_by_id, remarks)
            VALUES (%s, %s, %s, 'department_head', %s, %s)
            """,
            (complaint_id, old_status, new_status, head_id, remarks_log)
        )
        conn.commit()
        return True, new_status
    finally:
        cursor.close()
        conn.close()
