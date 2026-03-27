import psycopg2
from psycopg2.extras import RealDictCursor
import os
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv('.env.windows')

def _get_db_config():
    # Streamlit Cloud secrets take priority, then env vars
    try:
        import streamlit as st
        s = st.secrets
        return {
            "host":     s["DB_HOST"],
            "database": s["DB_NAME"],
            "user":     s["DB_USER"],
            "password": s["DB_PASSWORD"],
            "port":     s.get("DB_PORT", "5432"),
            "sslmode":  s.get("DB_SSLMODE", "require"),
        }
    except Exception:
        return {
            "host":     os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "feedback_db"),
            "user":     os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "postgres"),
            "port":     os.getenv("DB_PORT", "5432"),
            "sslmode":  os.getenv("DB_SSLMODE", "disable"),
        }

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(**_get_db_config())
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_database():
    import hashlib
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL CHECK (role IN ('customer', 'owner'))
            )
        """)

        # Seed default owner account if not exists
        default_owner     = "owner1"
        default_password  = hashlib.sha256("owner123".encode()).hexdigest()
        cur.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, 'owner')
            ON CONFLICT (username) DO NOTHING
        """, (default_owner, default_password))
        
        # Create customers table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_email VARCHAR(100) PRIMARY KEY,
                customer_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                product VARCHAR(100),
                feature VARCHAR(100),
                subfeature VARCHAR(100),
                feedback_text TEXT,
                urgency VARCHAR(50),
                customer_email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_email) REFERENCES customers(customer_email) ON DELETE SET NULL
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ideas (
                id SERIAL PRIMARY KEY,
                feature VARCHAR(100),
                subfeature VARCHAR(100),
                idea_text TEXT,
                thumbs_up INTEGER DEFAULT 0,
                thumbs_down INTEGER DEFAULT 0,
                customer_email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_email) REFERENCES customers(customer_email) ON DELETE SET NULL
            )
        """)
        
        # Create innovative_ideas table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS innovative_ideas (
                id SERIAL PRIMARY KEY,
                customer_email VARCHAR(100),
                idea_text TEXT,
                thumbs_up INTEGER DEFAULT 0,
                thumbs_down INTEGER DEFAULT 0,
                approved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_email) REFERENCES customers(customer_email) ON DELETE SET NULL
            )
        """)
        
        # Create management_decisions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS management_decisions (
                id SERIAL PRIMARY KEY,
                product VARCHAR(50) NOT NULL,
                feature VARCHAR(100) NOT NULL,
                sub_feature VARCHAR(100) NOT NULL,
                urgency VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cur.close()

def register_customer(customer_email, customer_name):
    """Register or update customer in customers table"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO customers (customer_email, customer_name) 
               VALUES (%s, %s) 
               ON CONFLICT (customer_email) 
               DO UPDATE SET customer_name = EXCLUDED.customer_name""",
            (customer_email, customer_name)
        )
        conn.commit()
        cur.close()

def save_feedback(product, feature, subfeature, feedback_text, urgency, customer_name=None, customer_email=None):
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Register customer first if provided
        if customer_email and customer_name:
            register_customer(customer_email, customer_name)
        
        cur.execute(
            "INSERT INTO feedback (product, feature, subfeature, feedback_text, urgency, customer_email) VALUES (%s, %s, %s, %s, %s, %s)",
            (product, feature, subfeature, feedback_text, urgency, customer_email)
        )
        conn.commit()
        cur.close()

def get_feedback(limit=100):
    """Get feedback with customer details via JOIN"""
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT f.*, c.customer_name 
            FROM feedback f
            LEFT JOIN customers c ON f.customer_email = c.customer_email
            ORDER BY f.created_at DESC 
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        return rows

def save_idea(feature, subfeature, idea_text, customer_email=None, customer_name=None):
    """Save idea with customer reference"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Register customer first if provided
        if customer_email and customer_name:
            register_customer(customer_email, customer_name)
        
        cur.execute(
            "INSERT INTO ideas (feature, subfeature, idea_text, customer_email) VALUES (%s, %s, %s, %s)",
            (feature, subfeature, idea_text, customer_email)
        )
        conn.commit()
        cur.close()

def get_ideas():
    """Get ideas with customer details via JOIN"""
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT i.*, c.customer_name 
            FROM ideas i
            LEFT JOIN customers c ON i.customer_email = c.customer_email
            ORDER BY i.created_at DESC
        """)
        rows = cur.fetchall()
        cur.close()
        return rows

def update_idea_vote(idea_id, vote_type):
    with get_db_connection() as conn:
        cur = conn.cursor()
        if vote_type == "up":
            cur.execute("UPDATE ideas SET thumbs_up = thumbs_up + 1 WHERE id = %s", (idea_id,))
        else:
            cur.execute("UPDATE ideas SET thumbs_down = thumbs_down + 1 WHERE id = %s", (idea_id,))
        cur.close()

def verify_user(username, password):
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE username = %s AND password_hash = %s", (username, password_hash))
        user = cur.fetchone()
        cur.close()
        return user

def create_user(username, password, role):
    import hashlib
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", 
                   (username, password_hash, role))
        cur.close()

def save_innovative_idea(customer_email, idea_text, customer_name=None):
    """Save innovative idea with customer reference"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Register customer first if provided
        if customer_email and customer_name:
            register_customer(customer_email, customer_name)
        
        cur.execute(
            "INSERT INTO innovative_ideas (customer_email, idea_text) VALUES (%s, %s)",
            (customer_email, idea_text)
        )
        
        conn.commit()
        cur.close()

def get_all_innovative_ideas():
    """Get all innovative ideas with customer details via JOIN"""
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT ii.*, c.customer_name 
            FROM innovative_ideas ii
            LEFT JOIN customers c ON ii.customer_email = c.customer_email
            ORDER BY ii.created_at DESC
        """)
        rows = cur.fetchall()
        cur.close()
        return rows

def update_innovative_idea_vote(idea_id, vote_type):
    """Update vote count for innovative idea"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        if vote_type == "up":
            cur.execute("UPDATE innovative_ideas SET thumbs_up = COALESCE(thumbs_up, 0) + 1 WHERE id = %s", (idea_id,))
        else:
            cur.execute("UPDATE innovative_ideas SET thumbs_down = COALESCE(thumbs_down, 0) + 1 WHERE id = %s", (idea_id,))
        conn.commit()
        cur.close()
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Add voting columns if they don't exist
        try:
            cur.execute("ALTER TABLE innovative_ideas ADD COLUMN IF NOT EXISTS thumbs_up INTEGER DEFAULT 0")
            cur.execute("ALTER TABLE innovative_ideas ADD COLUMN IF NOT EXISTS thumbs_down INTEGER DEFAULT 0")
        except:
            pass
        
        if vote_type == "up":
            cur.execute("UPDATE innovative_ideas SET thumbs_up = COALESCE(thumbs_up, 0) + 1 WHERE id = %s", (idea_id,))
        else:
            cur.execute("UPDATE innovative_ideas SET thumbs_down = COALESCE(thumbs_down, 0) + 1 WHERE id = %s", (idea_id,))
        cur.close()
def check_user_vote(idea_id, customer_email):
    """Check if user has already voted on this idea"""
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            
            # Create votes table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS idea_votes (
                    id SERIAL PRIMARY KEY,
                    idea_id INTEGER,
                    customer_email VARCHAR(100),
                    vote_type VARCHAR(10),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(idea_id, customer_email)
                )
            """)
            
            cur.execute("SELECT vote_type FROM idea_votes WHERE idea_id = %s AND customer_email = %s", (idea_id, customer_email))
            result = cur.fetchone()
            cur.close()
            return result[0] if result else None
    except:
        return None

def record_user_vote(idea_id, customer_email, vote_type):
    """Record or update user's vote"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Create votes table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS idea_votes (
                id SERIAL PRIMARY KEY,
                idea_id INTEGER,
                customer_email VARCHAR(100),
                vote_type VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(idea_id, customer_email)
            )
        """)
        
        # Insert or update vote
        cur.execute("""
            INSERT INTO idea_votes (idea_id, customer_email, vote_type) 
            VALUES (%s, %s, %s)
            ON CONFLICT (idea_id, customer_email) 
            DO UPDATE SET vote_type = EXCLUDED.vote_type
        """, (idea_id, customer_email, vote_type))
        
        conn.commit()
        cur.close()
def save_management_decision(product, feature, sub_feature, urgency):
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Create table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS management_decisions (
                id SERIAL PRIMARY KEY,
                product VARCHAR(50) NOT NULL,
                feature VARCHAR(100) NOT NULL,
                sub_feature VARCHAR(100) NOT NULL,
                urgency VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute(
            "INSERT INTO management_decisions (product, feature, sub_feature, urgency) VALUES (%s, %s, %s, %s)",
            (product, feature, sub_feature, urgency)
        )
        conn.commit()
        cur.close()
