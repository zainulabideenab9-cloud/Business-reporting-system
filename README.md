# ABRS - Business Reporting System

A Streamlit + MySQL business reporting application for operational tracking, analytics, reporting, and maintenance.

## Features

- Secure login with role-based access (`admin`, `employee`)
- Dashboard with KPI cards and charts
- Employee Portal for customer/project/budget input
- Task logging with productivity leaderboard
- Admin analytics with forecasting
- CSV/PDF/SQL export reporting
- Maintenance view for audit and budget alerts
- Demo data seeding and reset tooling

## Tech Stack

- Python
- Streamlit
- MySQL
- Pandas / NumPy
- Plotly
- scikit-learn
- FPDF

## Project File

- Main app: `app.py`

## Run Locally

1. Open PowerShell in the project folder.
2. Set environment variables:

```powershell
$env:ABRS_MYSQL_HOST="localhost"
$env:ABRS_MYSQL_PORT="3306"
$env:ABRS_MYSQL_USER="root"
$env:ABRS_MYSQL_PASSWORD='your_mysql_password'
$env:ABRS_MYSQL_DATABASE="DB"
```

3. Start the app:

```powershell
streamlit run D:\abrs\abrs\app.py
```

## Default Login

- Admin email: `admin@brs.local`
- Admin password: `admin123`

## Demo Users (if seeded)

- `ayesha@brs.local` / `employee123`
- `hamza@brs.local` / `employee123`
- `sara@brs.local` / `employee123`

## Demo Data

- Demo data is seeded during database initialization when business data is empty.
- Use **Maintenance -> Reset Demo Data** to clear and reseed test records.

## Testing Notes

- Confirm MySQL is running and accessible with the configured credentials.
- If login fails on first run, check DB connectivity errors in the app and terminal.
- Verify all modules:
  - Dashboard
  - Employee Portal
  - Tasks
  - Analytics (admin only)
  - Reports (admin only)
  - Maintenance (admin only)

## Common Troubleshooting

- **Access denied for MySQL user**: verify `ABRS_MYSQL_USER` and `ABRS_MYSQL_PASSWORD`.
- **Unknown database**: create the database first, or update `ABRS_MYSQL_DATABASE`.
- **Port issue**: confirm MySQL is listening on `3306` (or set your custom port).

## Security Reminder

Default credentials are for development/demo only. Change passwords before production use.
