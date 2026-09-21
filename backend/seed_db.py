"""
Run this script ONCE to insert properly hashed seed data into MySQL.
Usage:
    1. Open backend/config.py and set your MYSQL_PASSWORD
    2. Run: python seed_db.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from werkzeug.security import generate_password_hash
from database import get_connection


def seed():
    conn = get_connection()
    cursor = conn.cursor()

    # ── Departments ──────────────────────────────────────────────
    departments = [
        "Electrical", "IT/Network", "Hostel", "Transport",
        "Maintenance", "Canteen", "Security", "General Administration"
    ]
    for dept in departments:
        cursor.execute(
            "INSERT IGNORE INTO departments (department_name) VALUES (%s)", (dept,)
        )
    print("[OK] Departments inserted")

    # -- Admin --
    cursor.execute(
        "INSERT IGNORE INTO admins (username, password_hash, full_name) VALUES (%s, %s, %s)",
        ("admin", generate_password_hash("admin123"), "Campus Administrator")
    )
    print("[OK] Admin inserted  ->  username: admin  |  password: admin123")

    # -- Department Heads --
    heads = [
        ("elec_head",   "head123", "Mr. Rajan (Electrical)",        1),
        ("it_head",     "head123", "Mr. Kumar (IT/Network)",         2),
        ("hostel_head", "head123", "Ms. Priya (Hostel)",             3),
        ("trans_head",  "head123", "Mr. Suresh (Transport)",         4),
        ("maint_head",  "head123", "Mr. Babu (Maintenance)",         5),
        ("canteen_head","head123", "Ms. Devi (Canteen)",             6),
        ("sec_head",    "head123", "Mr. Murugan (Security)",         7),
        ("gen_head",    "head123", "Ms. Lakshmi (General Admin)",    8),
    ]
    for username, pwd, full_name, dept_id in heads:
        cursor.execute(
            "INSERT IGNORE INTO department_heads (username, password_hash, full_name, department_id) VALUES (%s, %s, %s, %s)",
            (username, generate_password_hash(pwd), full_name, dept_id)
        )
    print("[OK] Department heads inserted  ->  all passwords: head123")

    # -- Sample Students --
    students = [
        ("21CS001", "student123", "Arun Kumar",   "Computer Science", 3, "A", "arun@college.edu",    "9876543210"),
        ("21CS002", "student123", "Priya Devi",   "Computer Science", 3, "A", "priya@college.edu",   "9876543211"),
        ("21EC001", "student123", "Karthik Raja", "Electronics",      2, "B", "karthik@college.edu", "9876543212"),
    ]
    for reg, pwd, name, dept, year, sec, email, phone in students:
        cursor.execute(
            """INSERT IGNORE INTO students
               (register_number, password_hash, student_name, department, year, section, email, phone_number)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (reg, generate_password_hash(pwd), name, dept, year, sec, email, phone)
        )
    print("[OK] Students inserted  ->  all passwords: student123")

    conn.commit()
    cursor.close()
    conn.close()

    print("\nDatabase seeded successfully!")
    print("\n--- Demo Credentials ---")
    print("  Admin      -> username: admin       | password: admin123")
    print("  Dept Heads -> username: elec_head   | password: head123")
    print("             -> username: it_head     | password: head123")
    print("  Students   -> reg: 21CS001          | password: student123")
    print("             -> reg: 21CS002          | password: student123")
    print("------------------------")


if __name__ == "__main__":
    seed()
