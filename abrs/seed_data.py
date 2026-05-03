"""
ABRS - Database Seed Script
Populates the database with realistic sample data for testing and demonstration.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import datetime
import random
import sqlite3
from utils.security import SecurityManager
from config import SQLITE_DB_PATH, DB_ENGINE


def seed_database():
    """Populate the database with comprehensive sample data."""
    # Initialize schema first
    from utils.db_engine import get_db
    get_db()  # This initializes the schema
    print("Schema initialized...")

    # Use a single persistent connection for the entire seed operation
    if DB_ENGINE == "sqlite":
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
    else:
        import mysql.connector
        from config import MYSQL_CONFIG
        conn = mysql.connector.connect(**MYSQL_CONFIG)

    cursor = conn.cursor()

    # ──────────────────────────────────────
    # Clear existing data
    # ──────────────────────────────────────
    cursor.execute("PRAGMA foreign_keys = OFF" if DB_ENGINE == "sqlite" else "SET FOREIGN_KEY_CHECKS=0")
    for table in ["DataQualityIssues", "ActivityLogs", "TaskLogs",
                   "Projects", "Budget", "Customers", "Users"]:
        try:
            cursor.execute(f"DELETE FROM {table}")
        except Exception:
            pass
    cursor.execute("PRAGMA foreign_keys = ON" if DB_ENGINE == "sqlite" else "SET FOREIGN_KEY_CHECKS=1")
    conn.commit()
    print("Cleared existing data...")

    # Helper: get last insert ID
    def last_id():
        if DB_ENGINE == "sqlite":
            cursor.execute("SELECT last_insert_rowid()")
        else:
            cursor.execute("SELECT LAST_INSERT_ID()")
        return cursor.fetchone()[0]

    # ──────────────────────────────────────
    # Seed Users
    # ──────────────────────────────────────
    users = [
        {"name": "Admin User", "email": "admin@abrs.com", "password": "Admin123", "role": "admin"},
        {"name": "Alice Chen", "email": "alice@abrs.com", "password": "Emp12345", "role": "employee"},
        {"name": "Bob Smith", "email": "bob@abrs.com", "password": "Emp12345", "role": "employee"},
        {"name": "Carol Wang", "email": "carol@abrs.com", "password": "Emp12345", "role": "employee"},
        {"name": "David Lee", "email": "david@abrs.com", "password": "Emp12345", "role": "employee"},
        {"name": "Eva Martinez", "email": "eva@abrs.com", "password": "Emp12345", "role": "employee"},
    ]

    ph = "?" if DB_ENGINE == "sqlite" else "%s"
    user_ids = []
    for u in users:
        pw_hash = SecurityManager.hash_password(u["password"])
        cursor.execute(
            f"""INSERT INTO Users (name, email, password_hash, role, is_active)
               VALUES ({ph}, {ph}, {ph}, {ph}, 1)""",
            (u["name"], u["email"], pw_hash, u["role"])
        )
        user_ids.append(last_id())
    conn.commit()
    print(f"Seeded {len(users)} users...")

    # ──────────────────────────────────────
    # Seed Customers
    # ──────────────────────────────────────
    customers = [
        {"name": "TechVision Corp", "contact": "contact@techvision.com", "industry": "Technology", "created_by": user_ids[1]},
        {"name": "HealthFirst Medical", "contact": "info@healthfirst.com", "industry": "Healthcare", "created_by": user_ids[1]},
        {"name": "FinancePro Solutions", "contact": "hello@financepro.com", "industry": "Finance", "created_by": user_ids[2]},
        {"name": "RetailMax Group", "contact": "sales@retailmax.com", "industry": "Retail", "created_by": user_ids[2]},
        {"name": "ManufactureX Inc", "contact": "biz@manufacturex.com", "industry": "Manufacturing", "created_by": user_ids[3]},
        {"name": "EduLearn Academy", "contact": "admin@edulearn.edu", "industry": "Education", "created_by": user_ids[3]},
        {"name": "GreenEnergy Labs", "contact": "info@greenenergy.com", "industry": "Technology", "created_by": user_ids[4]},
        {"name": "CloudNet Systems", "contact": "support@cloudnet.io", "industry": "Technology", "created_by": user_ids[4]},
        {"name": "UrbanDev Construction", "contact": "projects@urbandev.com", "industry": "Infrastructure", "created_by": user_ids[5]},
        {"name": "BioPharm Research", "contact": "research@biopharm.com", "industry": "Healthcare", "created_by": user_ids[5]},
        {"name": "DataStream Analytics", "contact": "team@datastream.ai", "industry": "Technology", "created_by": user_ids[1]},
        {"name": "OceanTrade Logistics", "contact": "ops@oceantrade.com", "industry": "Retail", "created_by": user_ids[2]},
    ]

    customer_ids = []
    for c in customers:
        cursor.execute(
            f"""INSERT INTO Customers (name, contact_info, industry, created_by)
               VALUES ({ph}, {ph}, {ph}, {ph})""",
            (c["name"], c["contact"], c["industry"], c["created_by"])
        )
        customer_ids.append(last_id())
    conn.commit()
    print(f"Seeded {len(customers)} customers...")

    # ──────────────────────────────────────
    # Seed Budget
    # ──────────────────────────────────────
    categories = ["Operations", "Marketing", "Development", "Infrastructure", "Services", "General"]
    budget_entries = []
    base_date = datetime.datetime(2024, 7, 1)

    for i, cid in enumerate(customer_ids):
        num_entries = random.randint(2, 4)
        for j in range(num_entries):
            month_offset = random.randint(0, 11)
            entry_date = base_date + datetime.timedelta(days=month_offset * 30 + random.randint(0, 28))
            amount = random.uniform(5000, 80000)
            cost = amount * random.uniform(0.3, 0.85)
            budget_entries.append({
                "customer_id": cid,
                "amount": round(amount, 2),
                "cost": round(cost, 2),
                "category": random.choice(categories),
                "date": entry_date.strftime("%Y-%m-%d %H:%M:%S"),
                "description": f"Q{j+1} budget allocation for {customers[i]['name']}"
            })

    for b in budget_entries:
        cursor.execute(
            f"""INSERT INTO Budget (customer_id, amount, cost, category, date, description)
               VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})""",
            (b["customer_id"], b["amount"], b["cost"], b["category"],
             b["date"], b["description"])
        )
    conn.commit()
    print(f"Seeded {len(budget_entries)} budget entries...")

    # ──────────────────────────────────────
    # Seed Projects
    # ──────────────────────────────────────
    project_types = ["Web Development", "Mobile App", "Data Analytics",
                     "Consulting", "Infrastructure", "Maintenance", "Other"]
    statuses = ["Pending", "In-Progress", "Completed"]

    projects = []
    for i, cid in enumerate(customer_ids):
        num_projects = random.randint(1, 3)
        for j in range(num_projects):
            emp_id = random.choice(user_ids[1:])
            status = random.choice(statuses)
            start = base_date + datetime.timedelta(days=random.randint(0, 300))
            end = None
            if status == "Completed":
                end = start + datetime.timedelta(days=random.randint(30, 120))
            revenue = random.uniform(10000, 150000) if status != "Pending" else 0
            projects.append({
                "customer_id": cid,
                "employee_id": emp_id,
                "type": random.choice(project_types),
                "status": status,
                "start_date": start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": end.strftime("%Y-%m-%d %H:%M:%S") if end else None,
                "revenue": round(revenue, 2),
                "description": f"{project_types[j % len(project_types)]} project for {customers[i]['name']}"
            })

    project_ids = []
    for p in projects:
        cursor.execute(
            f"""INSERT INTO Projects (customer_id, employee_id, type, status, start_date, end_date, revenue, description)
               VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})""",
            (p["customer_id"], p["employee_id"], p["type"], p["status"],
             p["start_date"], p["end_date"], p["revenue"], p["description"])
        )
        project_ids.append(last_id())
    conn.commit()
    print(f"Seeded {len(projects)} projects...")

    # ──────────────────────────────────────
    # Seed TaskLogs
    # ──────────────────────────────────────
    task_descriptions = [
        "Completed frontend module development",
        "Reviewed and tested API endpoints",
        "Deployed staging environment",
        "Client requirements gathering meeting",
        "Database optimization and indexing",
        "Code review and refactoring",
        "Wrote unit tests for payment module",
        "Prepared project documentation",
        "Fixed critical bug in authentication",
        "Designed database schema for new feature",
        "Performance testing and load analysis",
        "Updated project roadmap with stakeholders",
        "Integrated third-party payment gateway",
        "Conducted user acceptance testing",
        "Optimized SQL queries for reporting",
    ]

    task_count = 0
    for emp_id in user_ids[1:]:
        num_tasks = random.randint(5, 15)
        for _ in range(num_tasks):
            proj_id = random.choice(project_ids) if project_ids else None
            hours = round(random.uniform(0.5, 8.0), 2)
            desc = random.choice(task_descriptions)
            task_date = datetime.datetime.now() - datetime.timedelta(
                days=random.randint(0, 60),
                hours=random.randint(0, 8)
            )
            cursor.execute(
                f"""INSERT INTO TaskLogs (employee_id, project_id, hours, description, timestamp)
                   VALUES ({ph}, {ph}, {ph}, {ph}, {ph})""",
                (emp_id, proj_id, hours, desc, task_date.strftime("%Y-%m-%d %H:%M:%S"))
            )
            task_count += 1
    conn.commit()
    print(f"Seeded {task_count} task logs...")

    # ──────────────────────────────────────
    # Seed Activity Logs
    # ──────────────────────────────────────
    actions = ["Login", "Add Customer", "Add Project", "Update Project Status",
               "Log Task", "Export Report", "View Analytics", "Budget Alert"]

    for _ in range(30):
        uid = random.choice(user_ids)
        action = random.choice(actions)
        log_time = datetime.datetime.now() - datetime.timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 12)
        )
        cursor.execute(
            f"""INSERT INTO ActivityLogs (user_id, action, timestamp)
               VALUES ({ph}, {ph}, {ph})""",
            (uid, action, log_time.strftime("%Y-%m-%d %H:%M:%S"))
        )
    conn.commit()
    print("Seeded activity logs...")

    # ──────────────────────────────────────
    # Update admin last login
    # ──────────────────────────────────────
    cursor.execute(
        f"UPDATE Users SET last_login = {ph} WHERE role = 'admin'",
        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)
    )
    conn.commit()

    conn.close()

    print("\nDatabase seeded successfully!")
    print(f"   Users: {len(users)}")
    print(f"   Customers: {len(customers)}")
    print(f"   Budget Entries: {len(budget_entries)}")
    print(f"   Projects: {len(projects)}")
    print(f"   Task Logs: {task_count}")
    print("\n   Default Login Credentials:")
    print("   Admin:    admin@abrs.com / Admin123")
    print("   Employee: alice@abrs.com / Emp12345")


if __name__ == "__main__":
    seed_database()
