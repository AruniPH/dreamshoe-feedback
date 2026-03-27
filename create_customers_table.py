"""
Quick script to create customers table
"""
from database import init_database

if __name__ == "__main__":
    print("Creating customers table...")
    try:
        init_database()
        print("✅ Customers table created successfully!")
        print("Check pgAdmin and refresh the tables list.")
    except Exception as e:
        print(f"❌ Error: {e}")
