"""
Check database connection and list all tables
"""
from database import get_db_connection

if __name__ == "__main__":
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Check current database
            cur.execute("SELECT current_database();")
            db_name = cur.fetchone()[0]
            print(f"Connected to database: {db_name}")
            
            # List all tables
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            tables = cur.fetchall()
            print(f"\nTables found ({len(tables)}):")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Check if customers table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'customers'
                );
            """)
            exists = cur.fetchone()[0]
            
            if exists:
                print("\n✅ customers table EXISTS")
                
                # Show structure
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'customers'
                    ORDER BY ordinal_position;
                """)
                columns = cur.fetchall()
                print("\nCustomers table structure:")
                for col in columns:
                    print(f"  - {col[0]}: {col[1]}")
            else:
                print("\n❌ customers table DOES NOT EXIST")
                print("\nCreating customers table now...")
                
                cur.execute("""
                    CREATE TABLE customers (
                        customer_email VARCHAR(100) PRIMARY KEY,
                        customer_name VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
                print("✅ customers table created!")
            
            cur.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nCheck your .env.windows file:")
        print("  DB_HOST=localhost")
        print("  DB_NAME=feedback_db")
        print("  DB_USER=postgres")
        print("  DB_PASSWORD=your_password")
        print("  DB_PORT=5432")
