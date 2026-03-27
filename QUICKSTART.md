# Quick Start Guide

## 5-Minute Setup

### Step 1: Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows - Download from postgresql.org
```

### Step 2: Create Database
```bash
sudo -u postgres psql
CREATE DATABASE feedback_db;
\q
```

### Step 3: Install Python Dependencies
```bash
pip install psycopg2-binary python-dotenv
```

### Step 4: Configure Environment
```bash
# Create .env file
echo "DB_HOST=localhost
DB_NAME=feedback_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432" > .env
```

### Step 5: Initialize Database
```bash
python init_db.py
```

### Step 6: Replace Files
```bash
# Backup originals
cp app.py app_backup.py
cp owner_dashboard.py owner_dashboard_backup.py

# Use updated versions
cp app_updated.py app.py
cp owner_dashboard_updated.py owner_dashboard.py
```

### Step 7: Run Application
```bash
# Customer dashboard
streamlit run app.py

# Owner dashboard (in new terminal)
streamlit run owner_dashboard.py
```

## Default Login Credentials

**Customer Access:**
- Username: `customer1`
- Password: `customer123`

**Owner Access:**
- Username: `owner1`
- Password: `owner123`

## Testing Checklist

- [ ] Customer can login to app.py
- [ ] Customer can submit feedback
- [ ] Customer can submit ideas
- [ ] Customer can vote on ideas
- [ ] Owner can login to owner_dashboard.py
- [ ] Owner can view feedback analytics
- [ ] Owner can view statistical analysis
- [ ] Customer cannot access owner dashboard
- [ ] Owner cannot access customer features

## Rollback (If Needed)

```bash
# Restore original files
cp app_backup.py app.py
cp owner_dashboard_backup.py owner_dashboard.py

# Continue using CSV files
```

## Common Issues

**"Connection refused"**
- Start PostgreSQL: `sudo systemctl start postgresql`

**"Authentication failed"**
- Check .env credentials match PostgreSQL user

**"Module not found"**
- Ensure database.py and auth.py are in project root

**"Table does not exist"**
- Run: `python init_db.py`
