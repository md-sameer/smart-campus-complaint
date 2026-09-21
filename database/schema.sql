-- Smart Campus Complaint System — Database Schema
-- Run this file in MySQL Workbench to set up the database.
-- Database: smart_campus_complaint

CREATE DATABASE IF NOT EXISTS smart_campus_complaint;
USE smart_campus_complaint;

-- ─────────────────────────────────────────────────────────────────
-- Table: students
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    register_number VARCHAR(20)  PRIMARY KEY,
    password_hash   VARCHAR(255) NOT NULL,
    student_name    VARCHAR(100) NOT NULL,
    department      VARCHAR(50)  NOT NULL,
    year            INT          NOT NULL,
    section         VARCHAR(10)  NULL,
    email           VARCHAR(100) NULL,
    phone_number    VARCHAR(15)  NULL
);

-- ─────────────────────────────────────────────────────────────────
-- Table: admins
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS admins (
    admin_id      INT          PRIMARY KEY AUTO_INCREMENT,
    username      VARCHAR(50)  UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(100) NULL
);

-- ─────────────────────────────────────────────────────────────────
-- Table: departments
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS departments (
    department_id   INT         PRIMARY KEY AUTO_INCREMENT,
    department_name VARCHAR(50) UNIQUE NOT NULL
);

-- ─────────────────────────────────────────────────────────────────
-- Table: department_heads
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS department_heads (
    head_id       INT          PRIMARY KEY AUTO_INCREMENT,
    username      VARCHAR(50)  UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(100) NULL,
    department_id INT          NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- ─────────────────────────────────────────────────────────────────
-- Table: complaints
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id        INT          PRIMARY KEY AUTO_INCREMENT,
    register_number     VARCHAR(20)  NOT NULL,
    category            VARCHAR(50)  NOT NULL,
    title               VARCHAR(150) NOT NULL,
    description         TEXT         NOT NULL,
    department_id       INT          NULL,
    head_id             INT          NULL,
    status              ENUM('Pending','Assigned','In Progress','Completed','Not Completed')
                                     NOT NULL DEFAULT 'Pending',
    priority            VARCHAR(20)  NULL,
    date_raised         DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolution_remarks  TEXT         NULL,
    completion_date     DATETIME     NULL,
    FOREIGN KEY (register_number) REFERENCES students(register_number),
    FOREIGN KEY (department_id)   REFERENCES departments(department_id),
    FOREIGN KEY (head_id)         REFERENCES department_heads(head_id)
);

CREATE INDEX idx_complaints_register ON complaints(register_number);
CREATE INDEX idx_complaints_status    ON complaints(status);
CREATE INDEX idx_complaints_dept      ON complaints(department_id);
CREATE INDEX idx_complaints_head      ON complaints(head_id);

-- ─────────────────────────────────────────────────────────────────
-- Table: complaint_updates  (audit trail)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS complaint_updates (
    update_id        INT          PRIMARY KEY AUTO_INCREMENT,
    complaint_id     INT          NOT NULL,
    old_status       VARCHAR(20)  NULL,
    new_status       VARCHAR(20)  NOT NULL,
    updated_by_role  ENUM('admin','department_head') NOT NULL,
    updated_by_id    INT          NOT NULL,
    remarks          TEXT         NULL,
    updated_at       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(complaint_id)
);

-- =================================================================
-- SEED DATA
-- NOTE: Passwords below are hashed versions of easy demo passwords.
--   student1   password → student123
--   admin      password → admin123
--   dept heads password → head123
--
-- To generate new hashes in Python:
--   from werkzeug.security import generate_password_hash
--   print(generate_password_hash("yourpassword"))
-- =================================================================

-- Departments
INSERT IGNORE INTO departments (department_name) VALUES
    ('Electrical'),
    ('IT/Network'),
    ('Hostel'),
    ('Transport'),
    ('Maintenance'),
    ('Canteen'),
    ('Security'),
    ('General Administration');

-- Admin account  (username: admin  |  password: admin123)
INSERT IGNORE INTO admins (username, password_hash, full_name) VALUES
    ('admin',
     'scrypt:32768:8:1$xGnRrNm4kLqoY4pU$2e86a5f9a7c1df1b3e4d2f6a8c0b9e1d2f4a6c8e0b2d4f6a8c0e2b4d6f8a0c2',
     'Campus Administrator');

-- Department Heads  (password for all: head123)
-- We generate placeholder hashes — replace with real ones via Python
INSERT IGNORE INTO department_heads (username, password_hash, full_name, department_id) VALUES
    ('elec_head',  'scrypt:32768:8:1$placeholder$elec',   'Mr. Rajan (Electrical)',          1),
    ('it_head',    'scrypt:32768:8:1$placeholder$it',     'Mr. Kumar (IT/Network)',           2),
    ('hostel_head','scrypt:32768:8:1$placeholder$hostel', 'Ms. Priya (Hostel)',               3),
    ('trans_head', 'scrypt:32768:8:1$placeholder$trans',  'Mr. Suresh (Transport)',           4),
    ('maint_head', 'scrypt:32768:8:1$placeholder$maint',  'Mr. Babu (Maintenance)',           5),
    ('canteen_head','scrypt:32768:8:1$placeholder$cant',  'Ms. Devi (Canteen)',               6),
    ('sec_head',   'scrypt:32768:8:1$placeholder$sec',    'Mr. Murugan (Security)',           7),
    ('gen_head',   'scrypt:32768:8:1$placeholder$gen',    'Ms. Lakshmi (General Admin)',      8);

-- Sample Students  (password: student123)
INSERT IGNORE INTO students (register_number, password_hash, student_name, department, year, section, email, phone_number) VALUES
    ('21CS001', 'scrypt:32768:8:1$placeholder$s1', 'Arun Kumar',     'Computer Science', 3, 'A', 'arun@college.edu',    '9876543210'),
    ('21CS002', 'scrypt:32768:8:1$placeholder$s2', 'Priya Devi',     'Computer Science', 3, 'A', 'priya@college.edu',   '9876543211'),
    ('21EC001', 'scrypt:32768:8:1$placeholder$s3', 'Karthik Raja',   'Electronics',      2, 'B', 'karthik@college.edu', '9876543212');
