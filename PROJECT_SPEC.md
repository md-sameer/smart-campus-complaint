# PROJECT_SPEC.md — Smart Campus Complaint System

**Version:** 1.0
**Team Size:** 3 members
**Duration:** 3 days
**Status:** Active Development

This document is the single source of truth for the Smart Campus Complaint System project. Every team member and every AI coding agent working on this repository MUST read this file before writing or modifying any code.

---

## 1. Project Overview

Smart Campus Complaint System is a web application that lets students raise complaints about campus facilities and services, track their resolution, and lets campus administration route and resolve those complaints through a structured workflow involving an Admin and department-specific Sub-Admins (Department Heads).

The system is built as a simple 3-tier web application:

- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Backend:** Python, Flask, REST APIs
- **Database:** MySQL (managed via MySQL Workbench)

There are **three separate portals**, each with its own login and dashboard:

1. Student Portal
2. Admin Portal
3. Department Head / Sub-Admin Portal

---

## 2. Problem Statement

Campus complaint handling today is informal — students report issues verbally or through scattered channels (WhatsApp, in-person, email), with no tracking, no accountability, and no visibility into resolution status. This causes:

- Lost or ignored complaints
- No accountability for departments
- Students unable to check status
- No historical record for repeated issues

## 3. Objectives

- Give students a single place to raise and track complaints.
- Give admin a centralized view to triage and assign complaints to the right department.
- Give department heads a focused queue of only their assigned work.
- Maintain a clear audit trail of status changes and resolution remarks.
- Keep the system simple enough to be built and demoed by a 3-person student team in 3 days.

---

## 4. User Roles

| Role | Description | Authentication |
|---|---|---|
| Student | Raises complaints, views own complaint status | Register Number + Password |
| Admin | Reviews all complaints, assigns department + department head | Admin Username/ID + Password |
| Department Head (Sub-Admin) | Works only their department's assigned complaints | Department Head ID + Password |

---

## 5. Portal Descriptions

### 5.1 Student Portal

- Login with **Register Number + Password only** (no manual detail entry).
- On successful login, the system fetches the student's stored profile from MySQL and displays it:
  - Register Number, Student Name, Department, Year, Section, Email, Phone Number.
- Features:
  1. Login
  2. View profile
  3. Raise a complaint (category, title, description)
  4. View list of previously submitted complaints
  5. View status of each complaint
  6. View assigned department (if assigned)
  7. View admin/department-head remarks/resolution

- **Complaint categories:** Classroom, Laboratory, Hostel, Canteen, Transport, Wi-Fi/Network, Electrical, Water, Cleanliness, Security, Other.
- A student can only ever see **their own** complaints (enforced at the API layer using the logged-in student's register number).

### 5.2 Admin Portal

- Fully separate login from students (Admin Username/ID + Password).
- Dashboard capabilities:
  1. Overview (counts by status)
  2. View all complaints
  3. Search complaints
  4. Filter complaints (by status/category/department)
  5. View full complaint detail
  6. View student details tied to a complaint
  7. Assign complaint to a department
  8. Assign complaint to a specific Department Head
  9. Monitor/change complaint status
  10. View completion remarks
  11. View full complaint history

- **Departments:** Electrical, IT/Network, Hostel, Transport, Maintenance, Canteen, Security, General Administration.
- When a department is chosen, admin selects the appropriate Department Head for that department.

### 5.3 Department Head / Sub-Admin Portal

- Each Department Head belongs to exactly **one** department (e.g., Electrical Department Head, IT Department Head).
- Login is separate from Student and Admin.
- After login, a Department Head sees **only** complaints assigned to their department/account.
- Dashboard shows, per complaint: Complaint ID, Student Name, Register Number, Category, Description, Date Raised, Current Status, Priority (if present).
- Department Head can:
  - Update status: `Assigned → In Progress → Completed / Not Completed`
  - Enter Action Taken
  - Enter Resolution Remarks
  - Enter Completion Date
- Department Heads must never see complaints outside their own department.

---

## 6. Complaint Workflow (Business Process)

```
Student logs in
   ↓
Student raises complaint            → status: Pending
   ↓
Complaint stored in MySQL
   ↓
Admin reviews complaint
   ↓
Admin assigns department + Department Head   → status: Assigned
   ↓
Department Head sees assigned task
   ↓
Department Head starts work         → status: In Progress
   ↓
Department Head completes work      → status: Completed / Not Completed
   ↓
Department Head adds resolution remarks
   ↓
Student sees updated status and remarks
```

---

## 7. Functional Requirements

- FR1: Students authenticate with Register Number + Password only; no manual profile entry.
- FR2: System retrieves and displays stored student profile after login.
- FR3: Students can submit a complaint with category, title, and description.
- FR4: Students can view only their own complaint list and statuses.
- FR5: Admin can view, search, and filter all complaints.
- FR6: Admin can assign a complaint to a department and a specific Department Head.
- FR7: Department Head can view only complaints assigned to them.
- FR8: Department Head can update status and add resolution remarks.
- FR9: All status transitions are recorded (for the complaint history view).
- FR10: Passwords are never stored or transmitted in plain text.

## 8. Non-Functional Requirements

- NFR1: Simplicity — no frameworks beyond the approved stack (no React, Node.js, Docker, microservices, Redis, Kubernetes, n8n).
- NFR2: Beginner-friendly, readable code; no unnecessary abstraction layers.
- NFR3: REST API responses in consistent JSON format.
- NFR4: Passwords hashed using Werkzeug's `generate_password_hash` / `check_password_hash`.
- NFR5: Basic input validation on all forms and API endpoints.
- NFR6: The system must be demoable end-to-end within a single session (no long-running background jobs).
- NFR7: Codebase must be organized so 3 people (or 3 AI agents) can work in parallel without file conflicts.

---

## 9. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python, Flask, REST APIs |
| Database | MySQL |
| DB Tooling | MySQL Workbench |
| Version Control | Git, GitHub |
| IDE | VS Code |
| Password Security | Werkzeug password hashing (Flask built-in) |

---

## 10. System Architecture

```
┌─────────────────┐        REST/JSON         ┌──────────────────┐        SQL        ┌──────────────┐
│   Frontend       │  ───────────────────►   │   Flask Backend   │  ─────────────►  │    MySQL      │
│ (HTML/CSS/JS)    │  ◄───────────────────   │   (REST API)      │  ◄─────────────  │   Database    │
│                   │                          │                   │                    │               │
│ - student pages  │                          │ - auth_routes     │                    │ students      │
│ - admin pages     │                          │ - student_routes  │                    │ admins        │
│ - dept-head pages │                          │ - admin_routes    │                    │ department_   │
└─────────────────┘                          │ - department_     │                    │   heads       │
                                                │   routes           │                    │ departments   │
                                                └──────────────────┘                    │ complaints    │
                                                                                          │ complaint_    │
                                                                                          │   updates     │
                                                                                          └──────────────┘
```

Three independent frontend flows call the same Flask REST API, which is the only component that talks to MySQL. No portal talks to the database directly.

---

## 11. Project Folder Structure

```
smart-campus-complaint/
├── PROJECT_SPEC.md
├── README.md
├── frontend/
│   ├── index.html
│   ├── student-login.html
│   ├── student-dashboard.html
│   ├── submit-complaint.html
│   ├── my-complaints.html
│   ├── admin-login.html
│   ├── admin-dashboard.html
│   ├── department-login.html
│   ├── department-dashboard.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── student.js
│   │   ├── admin.js
│   │   ├── department.js
│   │   └── api.js
│   └── assets/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── requirements.txt
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── student_routes.py
│   │   ├── admin_routes.py
│   │   └── department_routes.py
│   ├── services/
│   │   └── complaint_service.py
│   └── utils/
│       └── auth.py
└── database/
    └── schema.sql
```

---

## 12. MySQL Database Schema

**Database name:** `smart_campus_complaint`

### 12.1 `students`
| Column | Type | Constraints |
|---|---|---|
| register_number | VARCHAR(20) | PRIMARY KEY |
| password_hash | VARCHAR(255) | NOT NULL |
| student_name | VARCHAR(100) | NOT NULL |
| department | VARCHAR(50) | NOT NULL |
| year | INT | NOT NULL |
| section | VARCHAR(10) | NULL |
| email | VARCHAR(100) | NULL |
| phone_number | VARCHAR(15) | NULL |

### 12.2 `admins`
| Column | Type | Constraints |
|---|---|---|
| admin_id | INT | PRIMARY KEY, AUTO_INCREMENT |
| username | VARCHAR(50) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| full_name | VARCHAR(100) | NULL |

### 12.3 `departments`
| Column | Type | Constraints |
|---|---|---|
| department_id | INT | PRIMARY KEY, AUTO_INCREMENT |
| department_name | VARCHAR(50) | UNIQUE, NOT NULL |

Seed values: Electrical, IT/Network, Hostel, Transport, Maintenance, Canteen, Security, General Administration.

### 12.4 `department_heads`
| Column | Type | Constraints |
|---|---|---|
| head_id | INT | PRIMARY KEY, AUTO_INCREMENT |
| username | VARCHAR(50) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| full_name | VARCHAR(100) | NULL |
| department_id | INT | FOREIGN KEY → departments(department_id), NOT NULL |

### 12.5 `complaints`
| Column | Type | Constraints |
|---|---|---|
| complaint_id | INT | PRIMARY KEY, AUTO_INCREMENT |
| register_number | VARCHAR(20) | FOREIGN KEY → students(register_number), NOT NULL |
| category | VARCHAR(50) | NOT NULL |
| title | VARCHAR(150) | NOT NULL |
| description | TEXT | NOT NULL |
| department_id | INT | FOREIGN KEY → departments(department_id), NULL (until assigned) |
| head_id | INT | FOREIGN KEY → department_heads(head_id), NULL (until assigned) |
| status | ENUM('Pending','Assigned','In Progress','Completed','Not Completed') | NOT NULL, DEFAULT 'Pending' |
| priority | VARCHAR(20) | NULL |
| date_raised | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP |
| resolution_remarks | TEXT | NULL |
| completion_date | DATETIME | NULL |

**Indexes:** `register_number`, `status`, `department_id`, `head_id`.

### 12.6 `complaint_updates`
| Column | Type | Constraints |
|---|---|---|
| update_id | INT | PRIMARY KEY, AUTO_INCREMENT |
| complaint_id | INT | FOREIGN KEY → complaints(complaint_id), NOT NULL |
| old_status | VARCHAR(20) | NULL |
| new_status | VARCHAR(20) | NOT NULL |
| updated_by_role | ENUM('admin','department_head') | NOT NULL |
| updated_by_id | INT | NOT NULL |
| remarks | TEXT | NULL |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP |

### 12.7 Entity Relationships

- One `student` → many `complaints` (1:N)
- One `department` → many `department_heads` (1:N)
- One `department` → many `complaints` (1:N)
- One `department_head` → many `complaints` (1:N)
- One `complaint` → many `complaint_updates` (1:N, audit trail)

Seeding requirements: `students`, `department_heads`, and at least one `admins` row must be pre-populated for demo/development.

---

## 13. API Contract

All responses are JSON. All protected endpoints require the caller to be authenticated (session token or simple token returned at login — team may implement with Flask session cookies for simplicity).

### 13.1 Authentication

**POST `/api/student/login`**
- Purpose: Authenticate a student
- Request body: `{ "register_number": "string", "password": "string" }`
- Response: `{ "success": true, "student": { ...profile fields } }`
- Errors: `401 Invalid credentials`, `400 Missing fields`
- Auth required: No

**POST `/api/admin/login`**
- Purpose: Authenticate an admin
- Request body: `{ "username": "string", "password": "string" }`
- Response: `{ "success": true, "admin": { "admin_id": int, "username": "string" } }`
- Errors: `401 Invalid credentials`, `400 Missing fields`
- Auth required: No

**POST `/api/department-head/login`**
- Purpose: Authenticate a department head
- Request body: `{ "username": "string", "password": "string" }`
- Response: `{ "success": true, "head": { "head_id": int, "department": "string" } }`
- Errors: `401 Invalid credentials`, `400 Missing fields`
- Auth required: No

### 13.2 Student

**GET `/api/student/profile`**
- Purpose: Fetch logged-in student's profile
- Response: `{ "register_number", "student_name", "department", "year", "section", "email", "phone_number" }`
- Errors: `401 Not authenticated`
- Auth required: Yes (student)

**POST `/api/complaints`**
- Purpose: Submit a new complaint
- Request body: `{ "category": "string", "title": "string", "description": "string" }`
- Response: `{ "success": true, "complaint_id": int, "status": "Pending" }`
- Errors: `400 Missing fields`, `401 Not authenticated`
- Auth required: Yes (student)

**GET `/api/student/complaints`**
- Purpose: List the logged-in student's own complaints
- Response: `{ "complaints": [ { "complaint_id", "category", "title", "status", "department", "resolution_remarks", "date_raised" } ] }`
- Errors: `401 Not authenticated`
- Auth required: Yes (student)

### 13.3 Admin

**GET `/api/admin/complaints`**
- Purpose: List all complaints (supports `?status=`, `?category=`, `?search=` query params)
- Response: `{ "complaints": [ { full complaint + student summary } ] }`
- Errors: `401 Not authenticated`
- Auth required: Yes (admin)

**GET `/api/admin/complaints/<id>`**
- Purpose: Full detail of one complaint, including student details and update history
- Response: `{ "complaint": {...}, "student": {...}, "updates": [...] }`
- Errors: `404 Not found`, `401 Not authenticated`
- Auth required: Yes (admin)

**PUT `/api/admin/complaints/<id>/assign`**
- Purpose: Assign complaint to a department and department head
- Request body: `{ "department_id": int, "head_id": int }`
- Response: `{ "success": true, "status": "Assigned" }`
- Errors: `400 Invalid department/head`, `404 Not found`, `401 Not authenticated`
- Auth required: Yes (admin)

### 13.4 Department Head

**GET `/api/department-head/complaints`**
- Purpose: List complaints assigned to the logged-in department head
- Response: `{ "complaints": [ { "complaint_id", "student_name", "register_number", "category", "description", "date_raised", "status", "priority" } ] }`
- Errors: `401 Not authenticated`
- Auth required: Yes (department head)

**GET `/api/department-head/complaints/<id>`**
- Purpose: Full detail of one assigned complaint
- Response: `{ "complaint": {...}, "student": {...} }`
- Errors: `403 Not your department's complaint`, `404 Not found`, `401 Not authenticated`
- Auth required: Yes (department head)

**PUT `/api/department-head/complaints/<id>/status`**
- Purpose: Update status and enter resolution info
- Request body: `{ "status": "In Progress | Completed | Not Completed", "action_taken": "string", "resolution_remarks": "string", "completion_date": "YYYY-MM-DD" (optional) }`
- Response: `{ "success": true, "status": "Completed" }`
- Errors: `400 Invalid status`, `403 Not your department's complaint`, `404 Not found`, `401 Not authenticated`
- Auth required: Yes (department head)

> Member 1 and Member 2 must implement these endpoints exactly as documented. Any deviation must be updated here first, then communicated to the team.

---

## 14. Authentication Flow

1. Each portal's login page collects credentials and POSTs to its respective `/api/<role>/login` endpoint.
2. Backend looks up the user by ID/username, verifies password using Werkzeug's `check_password_hash`.
3. On success, backend establishes a Flask session (or returns a simple token) identifying the role and ID.
4. All subsequent portal-specific requests are checked against that session — a student's session cannot access admin or department-head routes, and vice versa.
5. Department Head routes additionally filter every query by the logged-in head's `department_id`/`head_id`.
6. Passwords are never stored, logged, or sent in plaintext beyond the initial HTTPS POST body; only bcrypt/Werkzeug hashes are persisted.

---

## 15. Frontend Requirements

- Plain HTML/CSS/JS only — no build tools, no frameworks.
- `js/api.js` centralizes all `fetch()` calls to the Flask backend so student.js, admin.js, and department.js don't duplicate request logic.
- Consistent design system (shared `css/style.css`) across all three portals, with distinct color accents per portal so users can visually tell them apart.
- Student portal: friendly, simple forms and a clear complaint list/status view.
- Admin portal: dense table-based views with search/filter controls.
- Department Head portal: focused task list with a status-update form per complaint.

## 16. Backend Requirements

- Flask app factory in `app.py`; configuration (DB credentials, secret key) in `config.py`.
- `database.py` handles the MySQL connection (e.g., via `mysql-connector-python` or `PyMySQL`).
- Routes split by role into their own blueprint files under `routes/`.
- Business logic (e.g., status-transition rules, assignment logic) lives in `services/complaint_service.py`, not directly in route handlers.
- `utils/auth.py` holds password hashing/verification helpers and session/role-check decorators.
- Every write endpoint validates required fields and returns clear 400 errors on bad input.

---

## 17. Member Responsibilities

**Member 1 — Frontend Developer**
- Student, Admin, and Department Head portal UI (HTML/CSS/JS).
- Forms, tables, dashboard cards, JS API calls, rendering API responses.
- Must NOT modify backend logic without coordinating with Member 3.

**Member 2 — Backend + MySQL Developer**
- Flask app, REST APIs, MySQL schema and queries.
- Backend authentication, complaint workflow logic, validation, error handling.
- Must document any API changes here in PROJECT_SPEC.md before/along with implementation.

**Member 3 — Team Lead + Integration**
- Owns the GitHub repository and this PROJECT_SPEC.md.
- Coordinates the API contract between Members 1 and 2.
- Handles integration, testing, bug tracking, merge coordination, final deployment, and demo prep.
- Should understand the full system end-to-end even without writing every module.

---

## 18. Git / GitHub Workflow

**Repository:** `smart-campus-complaint` (single shared repo)

**Branches:**
- `main` — stable, always demo-ready
- `frontend` — Member 1's working branch
- `backend` — Member 2's working branch
- `integration` — Member 3's working branch, where frontend + backend are merged and tested before going to `main`

**Rules:**
- No ZIP-file sharing — all work goes through Git.
- Before starting work: `git pull`
- After meaningful work: `git add .` → `git commit -m "..."` → `git push`
- Merge into `main` via Pull Request or controlled merge, reviewed/coordinated by Member 3.
- Never force-push over another member's branch.

---

## 19. AI Agent Rules

Every AI coding agent (and human contributor) working on this repository MUST:

1. Read this PROJECT_SPEC.md before modifying any code.
2. Inspect the existing repository before creating new files.
3. Respect the existing folder structure (Section 11).
4. Work only within their assigned module (Section 17).
5. Never rename API endpoints without updating Section 13 first.
6. Never change database table/column names without team coordination.
7. Never overwrite another member's work.
8. Never create duplicate implementations of the same feature.
9. Keep code beginner-friendly — this is a student project, not a production system.
10. Explain important changes in commit messages or PR descriptions.
11. Test changes locally before committing.
12. Do not introduce technologies outside Section 9 (no React, Node.js, Docker, microservices, Redis, Kubernetes, n8n, etc.).
13. If a requirement is unclear, treat this document as the source of truth.
14. If an API or database change is genuinely necessary, document it here first, then implement it.

---

## 20. 3-Day Development Plan

**Day 1**
- GitHub repo setup, branch creation
- Project folder structure
- Finalize PROJECT_SPEC.md
- MySQL schema creation + seed data
- Student frontend pages (login, dashboard, submit complaint, my complaints)
- Flask app skeleton + backend foundation
- Authentication foundation (all three roles)

**Day 2**
- Student complaint submission + viewing wired to backend
- Admin dashboard UI + backend (list/search/filter/assign)
- Department Head dashboard UI + backend (assigned complaints, status update)

**Day 3**
- Full frontend/backend integration across all three portals
- End-to-end workflow testing (Section 14/22)
- Authentication testing per role
- Database integrity testing
- Bug fixing
- UI polishing
- Deployment
- Demo rehearsal

---

## 21. Testing Checklist

- [ ] Student can log in with valid Register Number + Password
- [ ] Invalid student credentials are rejected with a clear error
- [ ] Student profile auto-populates correctly after login
- [ ] Student can submit a complaint with all required fields
- [ ] Complaint appears with status `Pending` immediately after submission
- [ ] Student sees only their own complaints, never another student's
- [ ] Admin can log in and view all complaints
- [ ] Admin search and filter return correct results
- [ ] Admin can assign a complaint to a department + department head
- [ ] Complaint status updates to `Assigned` after admin assignment
- [ ] Department Head can log in and sees only their department's complaints
- [ ] Department Head cannot access another department's complaints (403 enforced)
- [ ] Department Head can update status through `In Progress → Completed/Not Completed`
- [ ] Resolution remarks and completion date save correctly
- [ ] Student sees the updated status and remarks after resolution
- [ ] Complaint history (`complaint_updates`) reflects every status change
- [ ] Passwords are hashed in the database, never stored in plaintext
- [ ] All API error responses return meaningful status codes and messages

---

## 22. Final Demo Workflow (MVP Definition)

1. Student logs in using Register Number + Password.
2. Student's profile details auto-populate.
3. Student raises a new complaint.
4. Complaint is saved in MySQL with status `Pending`.
5. Admin logs in.
6. Admin sees the new complaint in the dashboard.
7. Admin assigns the complaint to a department.
8. Admin assigns a specific Department Head.
9. Department Head logs in.
10. Department Head sees the assigned complaint.
11. Department Head changes status to `In Progress`.
12. Department Head completes the task, sets status to `Completed`.
13. Department Head enters resolution remarks.
14. Student logs back in / refreshes dashboard.
15. Student sees the updated status and resolution remarks.

This exact end-to-end flow is the definition of a successful MVP for this project.

---

## 23. Future Enhancement Ideas

*(Not part of the 3-day MVP — for reference only.)*

- Email/SMS notifications on status change
- File/photo attachment for complaints
- Complaint priority auto-suggestion based on category
- Analytics dashboard (average resolution time, complaints per department)
- Student satisfaction rating after resolution
- Multi-language support
- Mobile-responsive PWA version
- Admin ability to reassign a complaint if the wrong department was picked

---

*End of PROJECT_SPEC.md*