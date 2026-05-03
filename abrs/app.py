import hashlib
import os
import re
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF
from mysql.connector import Error, connect
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Business Reporting System", layout="wide")


def apply_global_styles():
    st.markdown(
        """
        <style>
        :root {
            --neon-cyan: #00f5ff;
            --neon-pink: #ff2bd6;
            --neon-lime: #8dff00;
            --panel-bg: #0f0b1f;
            --text-main: #e8f9ff;
        }

        [data-testid="stSidebar"],
        [data-testid="stSidebarNav"],
        [data-testid="collapsedControl"] {
            display: none !important;
        }

        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at top right, #24104a 0%, #0b0a1a 55%, #070712 100%);
            color: var(--text-main);
        }

        [data-testid="stHeader"] {
            background: rgba(7, 7, 18, 0.85);
            border-bottom: 1px solid rgba(0, 245, 255, 0.35);
        }

        .stButton > button {
            min-height: 3rem !important;
            font-size: 1.02rem !important;
            font-weight: 600 !important;
            border-radius: 0.7rem !important;
            border: 1px solid rgba(0, 245, 255, 0.6) !important;
            background: linear-gradient(135deg, rgba(0, 245, 255, 0.12), rgba(255, 43, 214, 0.12)) !important;
            color: #eafcff !important;
            box-shadow: 0 0 10px rgba(0, 245, 255, 0.25), 0 0 18px rgba(255, 43, 214, 0.15) !important;
        }

        .stButton > button:hover {
            border-color: rgba(141, 255, 0, 0.8) !important;
            box-shadow: 0 0 12px rgba(141, 255, 0, 0.45), 0 0 20px rgba(0, 245, 255, 0.35) !important;
            transform: translateY(-1px);
        }

        [data-testid="stMetric"],
        [data-testid="stDataFrame"],
        [data-testid="stForm"] {
            background: rgba(18, 18, 38, 0.62);
            border: 1px solid rgba(0, 245, 255, 0.2);
            border-radius: 0.75rem;
        }

        h1, h2, h3 {
            color: #e9e7ff;
            text-shadow: 0 0 8px rgba(0, 245, 255, 0.25);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state():
    defaults = {
        "authenticated": False,
        "user_id": None,
        "user_name": "",
        "user_role": "",
        "theme": "dark",
        "active_page": "Dashboard",
        "flash_message": "",
        "flash_until": 0.0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def db_config():
    return {
        "host": "127.0.0.1", # Matches your sidebar connection
        "port": 3306,
        "user": "root",
        # Use the exact password you used to see the green dot in VS Code
        "password": "12345678zain$", 
        "database": "abrs_mysql_database", # Targeting your new DB in the screenshot
        "autocommit": True,
    }


def get_connection():
    return connect(**db_config())


def hash_password(raw_password):
    return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()


def seed_sample_data(cur):
    cur.execute("SELECT COUNT(*) FROM Customers")
    customers_count = cur.fetchone()[0]
    if customers_count > 0:
        return

    cur.execute(
        """
        INSERT INTO Users (name, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE name = VALUES(name), role = VALUES(role)
        """,
        ("Ayesha Khan", "ayesha@brs.local", hash_password("employee123"), "employee"),
    )
    cur.execute(
        """
        INSERT INTO Users (name, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE name = VALUES(name), role = VALUES(role)
        """,
        ("Hamza Ali", "hamza@brs.local", hash_password("employee123"), "employee"),
    )

    cur.execute("SELECT id FROM Users WHERE email = %s", ("admin@brs.local",))
    admin_row = cur.fetchone()
    admin_id = admin_row[0] if admin_row else 1

    sample_customers = [
        ("Neon Retail Ltd", "+92-300-1112233"),
        ("Skyline Foods", "+92-321-5558844"),
        ("Orbit Health", "+92-333-9988776"),
    ]

    customer_ids = []
    for name, contact in sample_customers:
        cur.execute(
            "INSERT INTO Customers (name, contact_info, created_by) VALUES (%s, %s, %s)",
            (name, contact, admin_id),
        )
        customer_ids.append(cur.lastrowid)

    sample_projects = [
        (customer_ids[0], "Retail Automation", "In-Progress"),
        (customer_ids[1], "Supply Chain Upgrade", "Completed"),
        (customer_ids[2], "Clinical Dashboard", "Pending"),
    ]

    project_ids = []
    for customer_id, ptype, status in sample_projects:
        cur.execute(
            "INSERT INTO Projects (customer_id, type, status) VALUES (%s, %s, %s)",
            (customer_id, ptype, status),
        )
        project_ids.append(cur.lastrowid)

    budget_rows = [
        (customer_ids[0], 120000, 76000, "2026-01-15"),
        (customer_ids[0], 95000, 64000, "2026-02-18"),
        (customer_ids[1], 180000, 140000, "2026-01-10"),
        (customer_ids[1], 110000, 83000, "2026-03-02"),
        (customer_ids[2], 90000, 32000, "2026-02-05"),
        (customer_ids[2], 135000, 41000, "2026-03-12"),
    ]
    for row in budget_rows:
        cur.execute(
            "INSERT INTO Budget (customer_id, amount, cost, date) VALUES (%s, %s, %s, %s)",
            row,
        )

    cur.execute("SELECT id FROM Users WHERE email = %s", ("ayesha@brs.local",))
    employee_one = cur.fetchone()
    emp1_id = employee_one[0] if employee_one else admin_id

    cur.execute("SELECT id FROM Users WHERE email = %s", ("hamza@brs.local",))
    employee_two = cur.fetchone()
    emp2_id = employee_two[0] if employee_two else admin_id

    task_rows = [
        (emp1_id, project_ids[0], 6.5, "Prepared process map and automation workflow draft"),
        (emp2_id, project_ids[1], 7.0, "Validated migration checklist and closed UAT issues"),
        (emp1_id, project_ids[2], 4.0, "Built initial KPI wireframe for analytics module"),
        (emp2_id, project_ids[0], 5.5, "Client workshop and backlog refinement"),
    ]
    for row in task_rows:
        cur.execute(
            "INSERT INTO TaskLogs (employee_id, project_id, hours, description) VALUES (%s, %s, %s, %s)",
            row,
        )

    cur.execute(
        "INSERT INTO ActivityLogs (user_id, action, details) VALUES (%s, %s, %s)",
        (admin_id, "Sample Data Seeded", "Inserted demo records for functional testing"),
    )




def reset_demo_data():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SET FOREIGN_KEY_CHECKS = 0")
                try:
                    for table in ["TaskLogs", "ActivityLogs", "Budget", "Projects", "Customers"]:
                        cur.execute(f"TRUNCATE TABLE {table}")

                    cur.execute(
                        "DELETE FROM Users WHERE email IN (%s, %s)",
                        ("ayesha@brs.local", "hamza@brs.local"),
                    )

                    cur.execute(
                        """
                        UPDATE Users
                        SET name = %s, password_hash = %s, role = 'admin', is_active = 1
                        WHERE email = %s
                        """,
                        ("System Admin", hash_password("admin123"), "admin@brs.local"),
                    )
                    if cur.rowcount == 0:
                        cur.execute(
                            """
                            INSERT INTO Users (name, email, password_hash, role)
                            VALUES (%s, %s, %s, %s)
                            """,
                            ("System Admin", "admin@brs.local", hash_password("admin123"), "admin"),
                        )
                finally:
                    cur.execute("SET FOREIGN_KEY_CHECKS = 1")

                seed_sample_data(cur)
        return True, "Demo data reset and reseeded successfully."
    except Error as exc:
        return False, f"Unable to reset demo data: {exc}"

def init_database():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # 1. Users Table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS Users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(120) NOT NULL,
                        email VARCHAR(150) UNIQUE NOT NULL,
                        password_hash VARCHAR(256) NOT NULL,
                        role ENUM('admin','employee') NOT NULL DEFAULT 'employee',
                        is_active TINYINT(1) NOT NULL DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 2. Customers Table (With Index Included)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS Customers (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(150) NOT NULL,
                        contact_info VARCHAR(255) NOT NULL,
                        created_by INT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (created_by) REFERENCES Users(id),
                        INDEX idx_customers_created_by (created_by)
                    )
                """)

                # 3. Projects Table (With Index Included)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS Projects (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        customer_id INT NOT NULL,
                        type VARCHAR(120) NOT NULL,
                        status ENUM('Pending','In-Progress','Completed') NOT NULL DEFAULT 'Pending',
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (customer_id) REFERENCES Customers(id),
                        INDEX idx_projects_customer_status (customer_id, status)
                    )
                """)

                # 4. Budget Table (With Index Included)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS Budget (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        customer_id INT NOT NULL,
                        amount DECIMAL(15,2) NOT NULL,
                        cost DECIMAL(15,2) NOT NULL DEFAULT 0,
                        date DATE NOT NULL,
                        FOREIGN KEY (customer_id) REFERENCES Customers(id),
                        INDEX idx_budget_customer_date (customer_id, date)
                    )
                """)

                # 5. TaskLogs Table (With Index Included)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS TaskLogs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        employee_id INT NOT NULL,
                        project_id INT NULL,
                        hours DECIMAL(6,2) NOT NULL,
                        description VARCHAR(255) NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (employee_id) REFERENCES Users(id),
                        FOREIGN KEY (project_id) REFERENCES Projects(id),
                        INDEX idx_tasklogs_employee_time (employee_id, timestamp)
                    )
                """)

                # 6. ActivityLogs Table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS ActivityLogs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NULL,
                        action VARCHAR(200) NOT NULL,
                        details VARCHAR(255) NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES Users(id)
                    )
                """)

                # 7. Seed Admin User
                cur.execute("SELECT id FROM Users WHERE email = %s", ("admin@brs.local",))
                if cur.fetchone() is None:
                    cur.execute(
                        """
                        INSERT INTO Users (name, email, password_hash, role)
                        VALUES (%s, %s, %s, %s)
                        """,
                        ("System Admin", "admin@brs.local", hash_password("admin123"), "admin"),
                    )

                seed_sample_data(cur)
    except Error as exc:
        st.error(f"MySQL initialization failed. Database error: {exc}")


def run_query(query, params=None, fetch="all"):
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(query, params or ())
                if fetch == "one":
                    return cur.fetchone()
                if fetch == "none":
                    return None
                return cur.fetchall()
    except Error as exc:
        st.error(f"Database error: {exc}")
        return None


def log_activity(action, details=""):
    if not st.session_state.get("authenticated"):
        return
    run_query(
        "INSERT INTO ActivityLogs (user_id, action, details) VALUES (%s, %s, %s)",
        (st.session_state.user_id, action, details[:255]),
        fetch="none",
    )


def authenticate(email, password):
    user = run_query(
        """
        SELECT id, name, role, password_hash
        FROM Users
        WHERE email = %s AND is_active = 1
        """,
        (email,),
        fetch="one",
    )
    if user and user["password_hash"] == hash_password(password):
        return user
    return None


def template_name():
    return "plotly_dark" if st.session_state.theme == "dark" else "plotly_white"


def nav_flash(message):
    st.session_state.flash_message = message
    st.session_state.flash_until = datetime.now().timestamp() + 1.0


def set_page(page_name):
    st.session_state.active_page = page_name
    nav_flash(f"Active view: {page_name}")


def render_title_bar():
    left, right = st.columns([7, 3])
    with left:
        st.title("Business Reporting System")
        st.caption("Secure operational analytics and reporting platform")
    with right:
        t1, t2 = st.columns(2)
        with t1:
            if st.button(
                "Dark Mode",
                use_container_width=True,
                type="primary" if st.session_state.theme == "dark" else "secondary",
            ):
                st.session_state.theme = "dark"
                nav_flash("Dark mode enabled")
                st.rerun()
        with t2:
            if st.button(
                "Light Mode",
                use_container_width=True,
                type="primary" if st.session_state.theme == "light" else "secondary",
            ):
                st.session_state.theme = "light"
                nav_flash("Light mode enabled")
                st.rerun()
    if datetime.now().timestamp() < st.session_state.flash_until:
        st.success(st.session_state.flash_message)


def render_navigation():
    pages = ["Dashboard", "Employee Portal", "Tasks", "Analytics", "Reports", "Maintenance"]
    cols = st.columns(len(pages) + 1)
    for i, page in enumerate(pages):
        if cols[i].button(
            page,
            use_container_width=True,
            type="primary" if st.session_state.active_page == page else "secondary",
        ):
            set_page(page)
            st.rerun()
    if cols[-1].button("Logout", use_container_width=True):
        log_activity("Logout", "User ended session")
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.user_name = ""
        st.session_state.user_role = ""
        st.session_state.active_page = "Dashboard"
        nav_flash("Session closed")
        st.rerun()


def professional_layout(fig, title_text):
    fig.update_layout(
        template=template_name(),
        title=title_text,
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1.0),
        hovermode="x unified",
    )
    return fig


def dashboard_page():
    st.subheader("Executive Dashboard")
    kpi_query = """
    SELECT
        IFNULL(SUM(b.amount), 0) AS revenue,
        IFNULL(SUM(b.cost), 0) AS costs,
        (SELECT COUNT(*) FROM Customers) AS customers,
        (SELECT COUNT(*) FROM Users WHERE role='employee' AND is_active=1) AS employees
    FROM Budget b
    """
    kpi = run_query(kpi_query, fetch="one") or {"revenue": 0, "costs": 0, "customers": 0, "employees": 0}
    revenue = float(kpi["revenue"] or 0)
    costs = float(kpi["costs"] or 0)
    profit = revenue - costs
    margin = (profit / revenue * 100) if revenue else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"{revenue:,.2f}")
    c2.metric("Total Customers", int(kpi["customers"]))
    c3.metric("Active Employees", int(kpi["employees"]))
    c4.metric("Profit Margin", f"{margin:.2f}%", delta=f"{profit:,.2f}")

    trend = run_query(
        """
        SELECT DATE_FORMAT(date, '%Y-%m') AS month,
               SUM(amount) AS revenue,
               SUM(cost) AS costs
        FROM Budget
        GROUP BY DATE_FORMAT(date, '%Y-%m')
        ORDER BY month
        """
    ) or []
    dist = run_query(
        """
        SELECT c.name AS customer_name, p.type AS project_type, SUM(b.amount) AS revenue
        FROM Budget b
        JOIN Customers c ON c.id = b.customer_id
        LEFT JOIN Projects p ON p.customer_id = c.id
        GROUP BY c.name, p.type
        HAVING SUM(b.amount) > 0
        """
    ) or []

    left, right = st.columns(2)
    with left:
        if trend:
            df_t = pd.DataFrame(trend)
            df_t["revenue"] = pd.to_numeric(df_t["revenue"], errors="coerce").fillna(0)
            df_t["costs"] = pd.to_numeric(df_t["costs"], errors="coerce").fillna(0)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_t["month"], y=df_t["revenue"], mode="lines+markers", name="Revenue", line=dict(width=3)))
            fig.add_trace(go.Scatter(x=df_t["month"], y=df_t["costs"], mode="lines+markers", name="Costs", line=dict(width=2, dash="dash")))
            fig = professional_layout(fig, "Monthly Revenue Trend")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No monthly revenue available.")
    with right:
        if dist:
            df_d = pd.DataFrame(dist).fillna({"project_type": "General"})
            df_d["revenue"] = pd.to_numeric(df_d["revenue"], errors="coerce").fillna(0)
            fig = px.sunburst(df_d, path=["customer_name", "project_type"], values="revenue", color="revenue", color_continuous_scale="Blues")
            fig = professional_layout(fig, "Revenue Distribution")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No revenue distribution available.")


def is_valid_name(name):
    return bool(re.fullmatch(r"[A-Za-z0-9 .,&()-]{2,150}", name))


def is_valid_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email or ""))


def employee_portal_page():
    st.markdown('<div data-testid="demo-employee-portal">', unsafe_allow_html=True)
    st.subheader("Employee Input Portal")

    with st.form("customer_project_form", clear_on_submit=True):
        st.markdown("Customer and Project Registration")
        c_name = st.text_input("Customer Name")
        c_contact = st.text_input("Contact Information")
        p_type = st.text_input("Project Type")
        p_status = st.selectbox("Project Status", ["Pending", "In-Progress", "Completed"])
        b_amount = st.number_input("Budget Amount", min_value=0.0, step=100.0)
        b_cost = st.number_input("Current Cost", min_value=0.0, step=100.0)
        b_date = st.date_input("Budget Date", value=datetime.today())
        submit_main = st.form_submit_button("Save Customer and Project", type="primary")

    if submit_main:
        if not c_name or not c_contact or not p_type:
            st.error("All fields are required.")
            st.markdown("</div>", unsafe_allow_html=True)
            return
        if not is_valid_name(c_name):
            st.error("Customer name contains invalid characters.")
            st.markdown("</div>", unsafe_allow_html=True)
            return
        if b_cost > b_amount:
            st.warning("Cost is above current budget allocation.")
        dup = run_query("SELECT id, name FROM Customers WHERE name = %s", (c_name,), fetch="one")
        if dup:
            st.info("Existing customer found. New project and budget will be linked.")
            customer_id = dup["id"]
        else:
            run_query(
                "INSERT INTO Customers (name, contact_info, created_by) VALUES (%s, %s, %s)",
                (c_name, c_contact, st.session_state.user_id),
                fetch="none",
            )
            new_row = run_query("SELECT id FROM Customers WHERE name=%s ORDER BY id DESC LIMIT 1", (c_name,), fetch="one")
            customer_id = new_row["id"] if new_row else None
        if customer_id is None:
            st.error("Unable to resolve customer id.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        run_query(
            "INSERT INTO Projects (customer_id, type, status) VALUES (%s, %s, %s)",
            (customer_id, p_type, p_status),
            fetch="none",
        )
        run_query(
            "INSERT INTO Budget (customer_id, amount, cost, date) VALUES (%s, %s, %s, %s)",
            (customer_id, float(b_amount), float(b_cost), b_date),
            fetch="none",
        )
        log_activity("Customer/Project Added", f"Customer: {c_name}, Project: {p_type}")
        st.success("Customer, project, and budget saved successfully.")

    st.markdown("---")
    st.markdown('<div data-testid="demo-employee-form">', unsafe_allow_html=True)
    st.markdown("Employee Registration")
    with st.form("employee_create_form", clear_on_submit=True):
        emp_name = st.text_input("Employee Name")
        emp_email = st.text_input("Employee Email")
        emp_password = st.text_input("Temporary Password", value="employee123", type="password")
        submit_emp = st.form_submit_button("Add Employee", type="primary")

    if submit_emp:
        if not emp_name.strip() or not emp_email.strip() or not emp_password:
            st.error("Employee name, email, and password are required.")
        elif not is_valid_name(emp_name.strip()):
            st.error("Employee name contains invalid characters.")
        elif not is_valid_email(emp_email.strip()):
            st.error("Employee email format is invalid.")
        else:
            existing_emp = run_query("SELECT id FROM Users WHERE email = %s", (emp_email.strip().lower(),), fetch="one")
            if existing_emp:
                st.warning("Employee email already exists.")
            else:
                run_query(
                    """
                    INSERT INTO Users (name, email, password_hash, role, is_active)
                    VALUES (%s, %s, %s, 'employee', 1)
                    """,
                    (emp_name.strip(), emp_email.strip().lower(), hash_password(emp_password)),
                    fetch="none",
                )
                log_activity("Employee Added", f"Employee: {emp_email.strip().lower()}")
                st.success("Employee account added successfully.")

    employees = run_query(
        """
        SELECT id, name, email, is_active, created_at
        FROM Users
        WHERE role='employee'
        ORDER BY id DESC
        LIMIT 25
        """
    ) or []
    if employees:
        st.dataframe(pd.DataFrame(employees), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("Data Quality Controls")
    duplicates = run_query(
        """
        SELECT name, COUNT(*) AS duplicate_count
        FROM Customers
        GROUP BY name
        HAVING COUNT(*) > 1
        ORDER BY duplicate_count DESC
        """
    ) or []
    if duplicates:
        st.warning("Duplicate customer names detected.")
        st.dataframe(pd.DataFrame(duplicates), use_container_width=True)
    else:
        st.success("No duplicate customers detected.")

    st.markdown("</div>", unsafe_allow_html=True)


def tasks_page():
    st.markdown('<div data-testid="demo-tasks-page">', unsafe_allow_html=True)
    st.subheader("Task Logging and Productivity")
    projects = run_query(
        """
        SELECT p.id, c.name AS customer_name, p.type, p.status
        FROM Projects p
        JOIN Customers c ON c.id = p.customer_id
        ORDER BY p.id DESC
        """
    ) or []
    project_options = {f"{p['id']} | {p['customer_name']} | {p['type']}": p["id"] for p in projects}

    with st.form("task_form", clear_on_submit=True):
        project_choice = st.selectbox("Project", list(project_options.keys()) if project_options else ["No projects available"])
        hours = st.number_input("Hours", min_value=0.0, max_value=24.0, step=0.5)
        desc = st.text_area("Work Description")
        submit_task = st.form_submit_button("Log Task", type="primary")

    if submit_task:
        if not desc.strip() or hours <= 0:
            st.error("Description and positive hours are required.")
        elif not projects:
            st.error("Create a project before logging tasks.")
        else:
            project_id = project_options[project_choice]
            run_query(
                "INSERT INTO TaskLogs (employee_id, project_id, hours, description) VALUES (%s, %s, %s, %s)",
                (st.session_state.user_id, project_id, float(hours), desc.strip()),
                fetch="none",
            )
            log_activity("Task Logged", f"Project ID: {project_id}, Hours: {hours}")
            st.success("Task logged successfully.")

    recent_tasks = run_query(
        """
        SELECT t.id, u.name AS employee_name, t.project_id, t.hours, t.description, t.timestamp
        FROM TaskLogs t
        JOIN Users u ON u.id = t.employee_id
        ORDER BY t.timestamp DESC
        LIMIT 20
        """
    ) or []
    if recent_tasks:
        st.markdown("Recent Task Logs")
        st.dataframe(pd.DataFrame(recent_tasks), use_container_width=True)

    leaderboard = run_query(
        """
        SELECT u.name AS employee_name,
               COUNT(t.id) AS tasks_completed,
               IFNULL(SUM(t.hours), 0) AS hours_logged
        FROM Users u
        LEFT JOIN TaskLogs t ON t.employee_id = u.id
        WHERE u.role = 'employee'
        GROUP BY u.id, u.name
        ORDER BY hours_logged DESC, tasks_completed DESC
        """
    ) or []
    if leaderboard:
        df_lb = pd.DataFrame(leaderboard)
        df_lb["incentive_estimate"] = (pd.to_numeric(df_lb["hours_logged"], errors="coerce").fillna(0) * 12.5).round(2)
        st.dataframe(df_lb, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


def analytics_page():
    st.subheader("Admin Analytics and Forecasting")
    if st.session_state.user_role != "admin":
        st.warning("Analytics is restricted to admin users.")
        return

    perf = run_query(
        """
        SELECT u.name AS employee_name,
               COUNT(t.id) AS task_count,
               IFNULL(SUM(t.hours), 0) AS hours_logged,
               IFNULL(SUM(b.amount), 0) AS revenue_contribution
        FROM Users u
        LEFT JOIN TaskLogs t ON t.employee_id = u.id
        LEFT JOIN Projects p ON p.id = t.project_id
        LEFT JOIN Budget b ON b.customer_id = p.customer_id
        WHERE u.role='employee'
        GROUP BY u.id, u.name
        ORDER BY revenue_contribution DESC
        """
    ) or []
    if perf:
        df_perf = pd.DataFrame(perf)
        fig_bar = px.bar(
            df_perf,
            x="employee_name",
            y="revenue_contribution",
            color="hours_logged",
            title="Employee Revenue Contribution",
            barmode="group",
        )
        fig_bar = professional_layout(fig_bar, "Employee Revenue Contribution")
        st.plotly_chart(fig_bar, use_container_width=True)

    revenue_monthly = run_query(
        """
        SELECT DATE_FORMAT(date, '%Y-%m') AS month,
               SUM(amount) AS revenue
        FROM Budget
        GROUP BY DATE_FORMAT(date, '%Y-%m')
        ORDER BY month
        """
    ) or []
    if len(revenue_monthly) >= 3:
        df = pd.DataFrame(revenue_monthly)
        df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)
        df["index"] = np.arange(len(df))
        model = LinearRegression()
        model.fit(df[["index"]], df["revenue"])
        future_steps = 3
        future_idx = np.arange(len(df), len(df) + future_steps)
        forecast_vals = model.predict(future_idx.reshape(-1, 1))
        future_months = [f"Forecast-{i + 1}" for i in range(future_steps)]

        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(x=df["month"], y=df["revenue"], mode="lines+markers", name="Historical"))
        fig_forecast.add_trace(
            go.Scatter(x=future_months, y=forecast_vals, mode="lines+markers", name="Forecast", line=dict(dash="dot", width=3))
        )
        fig_forecast = professional_layout(fig_forecast, "Revenue Forecast")
        st.plotly_chart(fig_forecast, use_container_width=True)
    else:
        st.info("At least three months of revenue data are required for forecasting.")

    churn = run_query(
        """
        SELECT c.name, MAX(b.date) AS last_budget_date
        FROM Customers c
        LEFT JOIN Budget b ON b.customer_id = c.id
        GROUP BY c.id, c.name
        HAVING last_budget_date IS NULL OR last_budget_date < DATE_SUB(CURDATE(), INTERVAL 60 DAY)
        """
    ) or []
    st.markdown("Potential Churn Clients")
    if churn:
        st.dataframe(pd.DataFrame(churn), use_container_width=True)
    else:
        st.success("No inactive customers detected in the churn window.")


def build_csv_report():
    data = run_query(
        """
        SELECT c.name AS customer,
               p.type AS project_type,
               p.status AS project_status,
               b.amount AS budget_amount,
               b.cost AS budget_cost,
               b.date AS budget_date
        FROM Customers c
        LEFT JOIN Projects p ON p.customer_id = c.id
        LEFT JOIN Budget b ON b.customer_id = c.id
        ORDER BY c.name, b.date
        """
    ) or []
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode("utf-8")


def build_pdf_report():
    kpi = run_query(
        """
        SELECT IFNULL(SUM(amount),0) AS revenue,
               IFNULL(SUM(cost),0) AS costs,
               COUNT(DISTINCT customer_id) AS customers
        FROM Budget
        """,
        fetch="one",
    ) or {"revenue": 0, "costs": 0, "customers": 0}

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Business Reporting System - Monthly Report", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(3)
    pdf.cell(0, 8, f"Total Revenue: {float(kpi['revenue']):,.2f}", ln=True)
    pdf.cell(0, 8, f"Total Costs: {float(kpi['costs']):,.2f}", ln=True)
    pdf.cell(0, 8, f"Total Customers: {int(kpi['customers'])}", ln=True)
    profit = float(kpi["revenue"]) - float(kpi["costs"])
    pdf.cell(0, 8, f"Profit: {profit:,.2f}", ln=True)
    return bytes(pdf.output(dest="S"))


def database_backup_sql():
    table_rows = run_query("SHOW TABLES")
    if not table_rows:
        return ""
    table_names = [list(row.values())[0] for row in table_rows]
    lines = ["-- Business Reporting System SQL Backup", f"-- Generated at {datetime.now()}"]
    for table in table_names:
        create_stmt = run_query(f"SHOW CREATE TABLE {table}", fetch="one")
        if create_stmt:
            lines.append(f"\nDROP TABLE IF EXISTS `{table}`;")
            lines.append(f"{create_stmt['Create Table']};")
        rows = run_query(f"SELECT * FROM {table}") or []
        for row in rows:
            values = []
            for value in row.values():
                if value is None:
                    values.append("NULL")
                elif isinstance(value, (int, float)):
                    values.append(str(value))
                else:
                    safe = str(value).replace("'", "''")
                    values.append(f"'{safe}'")
            lines.append(f"INSERT INTO `{table}` VALUES ({', '.join(values)});")
    return "\n".join(lines)


def reports_page():
    st.subheader("Reporting and Export")
    if st.session_state.user_role != "admin":
        st.warning("Reports are restricted to admin users.")
        return
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "Download Monthly CSV",
            data=build_csv_report(),
            file_name=f"monthly_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "Download Monthly PDF",
            data=build_pdf_report(),
            file_name=f"monthly_report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    with col3:
        backup_text = database_backup_sql()
        st.download_button(
            "Download SQL Backup",
            data=backup_text.encode("utf-8"),
            file_name=f"abrs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
            mime="application/sql",
            use_container_width=True,
        )
    log_activity("Report Access", "Reports page viewed")


def maintenance_page():
    st.subheader("System Maintenance and Audit")
    health = "Healthy"
    try:
        run_query("SELECT 1", fetch="one")
    except Exception:
        health = "Unavailable"
    st.metric("MySQL Connectivity", health)

    st.markdown("Demo Data Tools")
    st.caption("Use this to clear existing business records and load fresh sample data.")
    if st.button("Reset Demo Data", type="primary", use_container_width=True):
        ok, message = reset_demo_data()
        if ok:
            log_activity("Demo Data Reset", "Maintenance reseeded sample dataset")
            st.success(message)
            st.rerun()
        else:
            st.error(message)

    if st.session_state.user_role != "admin":
        st.warning("Maintenance is restricted to admin users.")
        return
    logs = run_query(
        """
        SELECT a.timestamp, u.name AS user_name, a.action, a.details
        FROM ActivityLogs a
        LEFT JOIN Users u ON u.id = a.user_id
        ORDER BY a.timestamp DESC
        LIMIT 100
        """
    ) or []
    st.dataframe(pd.DataFrame(logs), use_container_width=True)

    window_days = st.number_input("Budget alert window days", min_value=1, max_value=365, value=30)
    alerts = run_query(
        """
        SELECT c.name AS customer_name,
               SUM(b.amount) AS total_budget,
               SUM(b.cost) AS total_cost
        FROM Customers c
        JOIN Budget b ON b.customer_id = c.id
        WHERE b.date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        GROUP BY c.id, c.name
        HAVING total_budget > 0 AND (SUM(b.cost) / SUM(b.amount)) >= 0.8
        ORDER BY (SUM(b.cost) / SUM(b.amount)) DESC
        """,
        (int(window_days),),
    ) or []
    if alerts:
        df_alerts = pd.DataFrame(alerts)
        df_alerts["usage_pct"] = (df_alerts["total_cost"] / df_alerts["total_budget"] * 100).round(2)
        st.warning("Budget usage threshold exceeded for one or more customers.")
        st.dataframe(df_alerts, use_container_width=True)
    else:
        st.success("No budget threshold breaches in selected window.")


def login_screen():
    st.title("Business Reporting System")
    st.caption("Login with your account to continue")
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", type="primary")
    if submit:
        if not email or not password:
            st.error("Email and password are required.")
            return
        user = authenticate(email.strip(), password)
        if not user:
            st.error("Invalid credentials.")
            return
        st.session_state.authenticated = True
        st.session_state.user_id = user["id"]
        st.session_state.user_name = user["name"]
        st.session_state.user_role = user["role"]
        log_activity("Login", "User authenticated")
        nav_flash("Login successful")
        st.rerun()
    st.info("Default admin login: admin@brs.local / admin123")


def render_authorized_app():
    render_title_bar()
    st.caption(f"Logged in as {st.session_state.user_name} ({st.session_state.user_role})")
    render_navigation()
    st.markdown("---")

    restricted_pages = {"Analytics", "Reports", "Maintenance"}
    if st.session_state.active_page in restricted_pages and st.session_state.user_role != "admin":
        st.session_state.active_page = "Dashboard"
        st.warning("Access limited by role permissions.")

    page = st.session_state.active_page
    if page == "Dashboard":
        dashboard_page()
    elif page == "Employee Portal":
        employee_portal_page()
    elif page == "Tasks":
        tasks_page()
    elif page == "Analytics":
        analytics_page()
    elif page == "Reports":
        reports_page()
    elif page == "Maintenance":
        maintenance_page()
    else:
        dashboard_page()


init_state()
init_database()
apply_global_styles()

if not st.session_state.authenticated:
    login_screen()
else:
    render_authorized_app()




