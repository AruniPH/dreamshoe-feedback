# PostgreSQL Migration & Authentication Setup

## Prerequisites

1. Install PostgreSQL on your system
2. Create a database named `feedback_db`

## Installation Steps

### 1. Install Required Packages

```bash
pip install psycopg2-binary python-dotenv
```

### 2. Configure Database Connection

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:

```
DB_HOST=localhost
DB_NAME=feedback_db
DB_USER=postgres
DB_PASSWORD=your_actual_password
DB_PORT=5432
```

### 3. Initialize Database

Run the initialization script to create tables and default users:

```bash
python init_db.py
```

This creates:
- Database tables (users, feedback, ideas)
- Default customer account: `customer1` / `customer123`
- Default owner account: `owner1` / `owner123`

### 4. Replace Old Files

Replace your existing files with the updated versions:

```bash
# Backup originals
mv app.py app_old.py
mv owner_dashboard.py owner_dashboard_old.py

# Use new versions
mv app_updated.py app.py
mv owner_dashboard_updated.py owner_dashboard.py
```

### 5. Update Collective Intelligence Page

If using the pages folder:

```bash
mv pages/1_Collective_Intelligence.py pages/1_Collective_Intelligence_old.py
mv pages/1_Collective_Intelligence_updated.py pages/1_Collective_Intelligence.py
```

## Running the Application

### Customer Dashboard
```bash
streamlit run app.py
```
Login with: `customer1` / `customer123`

### Owner Dashboard
```bash
streamlit run owner_dashboard.py
```
Login with: `owner1` / `owner123`

## Access Control

- **Customers** can:
  - Submit feedback via chatbot
  - Submit and vote on ideas
  
- **Owners** can:
  - View all feedback analytics
  - View statistical analysis
  - Access idea pool data

## Security Notes

1. Change default passwords immediately in production
2. Never commit `.env` file to version control
3. Use environment variables for sensitive data
4. Consider using connection pooling for production
5. Store OpenAI API key in environment variables instead of hardcoding

## Migration from CSV

Your existing CSV data can be imported:

```python
import pandas as pd
from database import save_feedback, save_idea

# Import feedback
df = pd.read_csv("crowd_feedback.csv")
for _, row in df.iterrows():
    save_feedback(row['Product'], row['Feature'], row['SubFeature'], 
                  row['Feedback'], row['ImprovementStatus'])

# Import ideas
idea_df = pd.read_csv("idea_pool.csv")
for _, row in idea_df.iterrows():
    # Note: votes will be reset to 0
    save_idea(row['Feature'], row['SubFeature'], row['Idea'])
```

## Troubleshooting

### Connection Error
- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check credentials in `.env` file
- Ensure database `feedback_db` exists

### Authentication Issues
- Run `python init_db.py` again to recreate users
- Check session state is cleared between logins

### Import Errors
- Ensure all new files are in the project root
- Verify `database.py` and `auth.py` are present
