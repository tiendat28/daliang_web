-- ============================================================
-- DATABASE SCHEMA – INTERNAL ADMIN SYSTEM
-- Dialect: PostgreSQL
-- Naming convention: snake_case, plural table names, singular columns
-- ============================================================

-- ------------------------------------------------------------
-- 1. DEPARTMENTS
-- ------------------------------------------------------------
CREATE TABLE departments (
    id               SERIAL PRIMARY KEY,
    department_code  VARCHAR(20)  NOT NULL UNIQUE,       -- e.g. DEPT-ENG, DEPT-HR, DEPT-FIN
    department_name  VARCHAR(150) NOT NULL,               -- e.g. Engineering, HR & Admin, Accounting
    description      TEXT,
    color            VARCHAR(7),                          -- hex color used for department tag in UI
    head_employee_id INTEGER,                             -- FK -> employees.id, constraint added after employees table exists
    status           VARCHAR(20) NOT NULL DEFAULT 'active'
                      CHECK (status IN ('active', 'inactive')),
    created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 2. POSITIONS
-- ------------------------------------------------------------
CREATE TABLE positions (
    id            SERIAL PRIMARY KEY,
    position_name VARCHAR(150) NOT NULL,   -- e.g. Department Head, Chief Accountant, Operations Engineer
    level         SMALLINT DEFAULT 1       -- seniority level, 1 = lowest
);

-- ------------------------------------------------------------
-- 3. EMPLOYEES
-- ------------------------------------------------------------
CREATE TABLE employees (
    id               SERIAL PRIMARY KEY,
    employee_code    VARCHAR(20)  NOT NULL UNIQUE,        -- e.g. EMP-0231
    full_name        VARCHAR(150) NOT NULL,
    date_of_birth    DATE,
    gender           VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    phone            VARCHAR(20),
    email            VARCHAR(150) UNIQUE,
    address          TEXT,
    avatar_url       VARCHAR(255),

    department_id    INTEGER NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
    position_id      INTEGER REFERENCES positions(id) ON DELETE SET NULL,

    hire_date        DATE NOT NULL,
    termination_date DATE,                                -- NULL while still employed
    status           VARCHAR(20) NOT NULL DEFAULT 'active'
                      CHECK (status IN ('active', 'probation', 'on_leave', 'terminated')),

    created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_employees_department ON employees(department_id);
CREATE INDEX idx_employees_status ON employees(status);

-- Add the deferred foreign key on departments (department head)
ALTER TABLE departments
    ADD CONSTRAINT fk_departments_head_employee
    FOREIGN KEY (head_employee_id) REFERENCES employees(id) ON DELETE SET NULL;

-- ------------------------------------------------------------
-- 4. ROLES & USER ACCOUNTS (system login)
-- ------------------------------------------------------------
CREATE TABLE roles (
    id         SERIAL PRIMARY KEY,
    role_name  VARCHAR(100) NOT NULL UNIQUE,   -- e.g. Admin, Department Head, Staff
    permissions JSONB                          -- e.g. {"documents.approve": true}
);

CREATE TABLE users (
    id             SERIAL PRIMARY KEY,
    employee_id    INTEGER UNIQUE REFERENCES employees(id) ON DELETE CASCADE,
    username       VARCHAR(50) NOT NULL UNIQUE,
    password_hash  VARCHAR(255) NOT NULL,
    role_id        INTEGER NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    status         VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'locked')),
    last_login_at  TIMESTAMP,
    created_at     TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 5. DOCUMENT TYPES (per department)
-- ------------------------------------------------------------
CREATE TABLE document_types (
    id             SERIAL PRIMARY KEY,
    type_name      VARCHAR(150) NOT NULL,   -- e.g. Technical Drawing, Labor Contract, Financial Report
    department_id  INTEGER REFERENCES departments(id) ON DELETE CASCADE  -- NULL = shared across departments
);

-- ------------------------------------------------------------
-- 6. DOCUMENTS
-- ------------------------------------------------------------
CREATE TABLE documents (
    id                SERIAL PRIMARY KEY,
    title             VARCHAR(255) NOT NULL,
    department_id     INTEGER NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
    document_type_id  INTEGER REFERENCES document_types(id) ON DELETE SET NULL,

    file_path         VARCHAR(500) NOT NULL,
    file_format       VARCHAR(10),                        -- PDF, DOCX, XLSX, DWG...
    file_size_kb      INTEGER,
    version           INTEGER NOT NULL DEFAULT 1,

    uploaded_by       INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
    approved_by       INTEGER REFERENCES employees(id) ON DELETE SET NULL,
    approved_at       TIMESTAMP,

    status            VARCHAR(20) NOT NULL DEFAULT 'pending'
                       CHECK (status IN ('pending', 'approved', 'rejected', 'expired')),
    expiry_date       DATE,
    notes             TEXT,

    created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_documents_department ON documents(department_id);
CREATE INDEX idx_documents_status ON documents(status);

-- ------------------------------------------------------------
-- 7. DOCUMENT HISTORY (audit trail)
-- ------------------------------------------------------------
CREATE TABLE document_history (
    id             SERIAL PRIMARY KEY,
    document_id    INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    action         VARCHAR(20) NOT NULL
                    CHECK (action IN ('uploaded', 'updated', 'approved', 'rejected', 'deleted')),
    performed_by   INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
    notes          TEXT,
    performed_at   TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 8. PARTNERS (suppliers / customers – for invoices)
-- ------------------------------------------------------------
CREATE TABLE partners (
    id              SERIAL PRIMARY KEY,
    partner_code    VARCHAR(20) NOT NULL UNIQUE,
    partner_name    VARCHAR(255) NOT NULL,
    type            VARCHAR(20) NOT NULL CHECK (type IN ('supplier', 'customer', 'both')),
    tax_code        VARCHAR(20),
    address         TEXT,
    phone           VARCHAR(20),
    email           VARCHAR(150),
    contact_person  VARCHAR(150)
);

-- ------------------------------------------------------------
-- 9. INVOICES (purchase & sale)
-- ------------------------------------------------------------
CREATE TABLE invoices (
    id             SERIAL PRIMARY KEY,
    invoice_number VARCHAR(30) NOT NULL UNIQUE,           -- e.g. INV-2026-0847
    type           VARCHAR(10) NOT NULL CHECK (type IN ('purchase', 'sale')),

    partner_id     INTEGER NOT NULL REFERENCES partners(id) ON DELETE RESTRICT,
    created_by     INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,

    issue_date     DATE NOT NULL,
    due_date       DATE,
    total_amount   NUMERIC(16,2) NOT NULL DEFAULT 0,
    vat_amount     NUMERIC(16,2) DEFAULT 0,

    status         VARCHAR(20) NOT NULL DEFAULT 'unpaid'
                    CHECK (status IN ('unpaid', 'paid', 'overdue', 'cancelled')),
    notes          TEXT,

    created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_invoices_type ON invoices(type);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_partner ON invoices(partner_id);

-- ------------------------------------------------------------
-- 10. INVOICE ITEMS
-- ------------------------------------------------------------
CREATE TABLE invoice_items (
    id           SERIAL PRIMARY KEY,
    invoice_id   INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    item_name    VARCHAR(255) NOT NULL,
    unit         VARCHAR(20),
    quantity     NUMERIC(12,2) NOT NULL DEFAULT 1,
    unit_price   NUMERIC(16,2) NOT NULL DEFAULT 0,
    amount       NUMERIC(16,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- ------------------------------------------------------------
-- 11. PAYMENTS (an invoice can be paid in multiple installments)
-- ------------------------------------------------------------
CREATE TABLE payments (
    id             SERIAL PRIMARY KEY,
    invoice_id     INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    amount         NUMERIC(16,2) NOT NULL,
    payment_date   DATE NOT NULL,
    method         VARCHAR(20) CHECK (method IN ('cash', 'bank_transfer', 'card')),
    confirmed_by   INTEGER REFERENCES employees(id) ON DELETE SET NULL,
    notes          TEXT
);

-- ============================================================
-- KEY RELATIONSHIPS
-- departments  1-n  employees
-- departments  1-1  employees (head_employee_id)
-- employees    1-1  users            (login account, optional)
-- departments  1-n  documents
-- employees    1-n  documents        (uploaded_by / approved_by)
-- documents    1-n  document_history
-- partners     1-n  invoices
-- invoices     1-n  invoice_items
-- invoices     1-n  payments
-- ============================================================
