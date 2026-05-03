"""
ABRS - Advanced Business Reporting System
Configuration Module
"""

import os

# ──────────────────────────────────────────────
# Database Configuration
# ──────────────────────────────────────────────
# Set DB_ENGINE to "mysql" for production, "sqlite" for development
DB_ENGINE = os.environ.get("ABRS_DB_ENGINE", "sqlite")

# SQLite config (development)
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "abrs_database.db")

# MySQL config (production)
MYSQL_CONFIG = {
    "host": os.environ.get("ABRS_MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("ABRS_MYSQL_PORT", 3306)),
    "user": os.environ.get("ABRS_MYSQL_USER", "root"),
    "password": os.environ.get("ABRS_MYSQL_PASSWORD", ""),
    "database": os.environ.get("ABRS_MYSQL_DATABASE", "abrs"),
}

# ──────────────────────────────────────────────
# Security Configuration
# ──────────────────────────────────────────────
HASH_ALGORITHM = "sha256"
SESSION_TIMEOUT_MINUTES = 60

# ──────────────────────────────────────────────
# Application Configuration
# ──────────────────────────────────────────────
APP_TITLE = "ABRS - Advanced Business Reporting System"
APP_ICON = ""
PAGE_LAYOUT = "wide"

# ──────────────────────────────────────────────
# Financial Configuration
# ──────────────────────────────────────────────
DEFAULT_TAX_RATE = 0.25  # 25% default tax rate
BUDGET_ALERT_THRESHOLD = 0.80  # Alert at 80% budget usage

# ──────────────────────────────────────────────
# Logging Configuration
# ──────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
ACTIVITY_LOG_FILE = os.path.join(LOG_DIR, "activity.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "errors.log")

# ──────────────────────────────────────────────
# Backup Configuration
# ──────────────────────────────────────────────
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "backups")

# Ensure directories exist
for d in [LOG_DIR, BACKUP_DIR]:
    os.makedirs(d, exist_ok=True)
