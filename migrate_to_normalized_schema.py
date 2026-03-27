"""
Migration script to normalize database with customers table
Run this ONCE to migrate existing data
"""
import psycopg2
from database import get_db_connection

def migrate_database():
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        print("Starting migration...")
        
        # Step 1: Create customers table
        print("1. Creating customers table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_email VARCHAR(100) PRIMARY KEY,
                customer_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        
        # Step 2: Migrate data from feedback table
        print("2. Migrating customers from feedback table...")
        cur.execute("""
            INSERT INTO customers (customer_email, customer_name)
            SELECT DISTINCT customer_email, customer_name
            FROM feedback
            WHERE customer_email IS NOT NULL 
              AND customer_name IS NOT NULL
            ON CONFLICT (customer_email) DO NOTHING
        """)
        conn.commit()
        
        # Step 3: Migrate data from innovative_ideas table
        print("3. Migrating customers from innovative_ideas table...")
        cur.execute("""
            INSERT INTO customers (customer_email, customer_name)
            SELECT DISTINCT customer_email, customer_name
            FROM innovative_ideas
            WHERE customer_email IS NOT NULL 
              AND customer_name IS NOT NULL
            ON CONFLICT (customer_email) DO NOTHING
        """)
        conn.commit()
        
        # Step 4: Add customer_email to ideas table if not exists
        print("4. Adding customer_email column to ideas table...")
        cur.execute("""
            ALTER TABLE ideas 
            ADD COLUMN IF NOT EXISTS customer_email VARCHAR(100)
        """)
        conn.commit()
        
        # Step 5: Add foreign key constraints
        print("5. Adding foreign key constraints...")
        
        # For feedback table
        try:
            cur.execute("""
                ALTER TABLE feedback 
                ADD CONSTRAINT fk_feedback_customer 
                FOREIGN KEY (customer_email) 
                REFERENCES customers(customer_email) 
                ON DELETE SET NULL
            """)
            conn.commit()
            print("   - Added FK to feedback table")
        except psycopg2.errors.DuplicateObject:
            conn.rollback()
            print("   - FK already exists on feedback table")
        
        # For ideas table
        try:
            cur.execute("""
                ALTER TABLE ideas 
                ADD CONSTRAINT fk_ideas_customer 
                FOREIGN KEY (customer_email) 
                REFERENCES customers(customer_email) 
                ON DELETE SET NULL
            """)
            conn.commit()
            print("   - Added FK to ideas table")
        except psycopg2.errors.DuplicateObject:
            conn.rollback()
            print("   - FK already exists on ideas table")
        
        # For innovative_ideas table
        try:
            cur.execute("""
                ALTER TABLE innovative_ideas 
                ADD CONSTRAINT fk_innovative_ideas_customer 
                FOREIGN KEY (customer_email) 
                REFERENCES customers(customer_email) 
                ON DELETE SET NULL
            """)
            conn.commit()
            print("   - Added FK to innovative_ideas table")
        except psycopg2.errors.DuplicateObject:
            conn.rollback()
            print("   - FK already exists on innovative_ideas table")
        
        # Step 6: Drop redundant customer_name columns (OPTIONAL - commented out for safety)
        print("\n6. Redundant customer_name columns can be dropped manually if desired:")
        print("   ALTER TABLE feedback DROP COLUMN IF EXISTS customer_name;")
        print("   ALTER TABLE innovative_ideas DROP COLUMN IF EXISTS customer_name;")
        print("   (Not executed automatically for data safety)")
        
        # Step 7: Verify migration
        print("\n7. Verifying migration...")
        cur.execute("SELECT COUNT(*) FROM customers")
        customer_count = cur.fetchone()[0]
        print(f"   - Total customers: {customer_count}")
        
        cur.execute("SELECT COUNT(*) FROM feedback WHERE customer_email IS NOT NULL")
        feedback_count = cur.fetchone()[0]
        print(f"   - Feedback entries with customers: {feedback_count}")
        
        cur.execute("SELECT COUNT(*) FROM ideas WHERE customer_email IS NOT NULL")
        ideas_count = cur.fetchone()[0]
        print(f"   - Ideas with customers: {ideas_count}")
        
        cur.execute("SELECT COUNT(*) FROM innovative_ideas WHERE customer_email IS NOT NULL")
        innovative_count = cur.fetchone()[0]
        print(f"   - Innovative ideas with customers: {innovative_count}")
        
        cur.close()
        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test the application to ensure everything works")
        print("2. If satisfied, manually drop redundant customer_name columns")
        print("3. Create indexes for better performance (see below)")
        print("\nRecommended indexes:")
        print("   CREATE INDEX idx_feedback_customer ON feedback(customer_email);")
        print("   CREATE INDEX idx_ideas_customer ON ideas(customer_email);")
        print("   CREATE INDEX idx_innovative_ideas_customer ON innovative_ideas(customer_email);")

if __name__ == "__main__":
    try:
        migrate_database()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Please check your database connection and try again.")
