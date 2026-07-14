import mysql.connector
from config import Config
import os

def init_db():
    print(f"Initializing database '{Config.DB_NAME}' on {Config.DB_HOST}...")
    
    # Try to connect without specifying database to create database if it doesn't exist
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
        cursor.close()
        conn.close()
        print(f"Database '{Config.DB_NAME}' ensured.")
    except Exception as e:
        print(f"Warning: Could not create/verify database: {e}")

    # Now connect to the database and run schema.sql
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = conn.cursor()
        
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
        if not os.path.exists(schema_path):
            print(f"Error: {schema_path} does not exist!")
            return
            
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
            
        # Split statements by semicolon
        # Note: simplistic splitter, works as long as semi-colons are not within strings
        statements = schema_sql.split(';')
        for statement in statements:
            stmt = statement.strip()
            if stmt:
                print(f"Executing: {stmt[:50]}...")
                cursor.execute(stmt)
                
        conn.commit()
        print("Database schema loaded successfully!")
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"Created tables: {[t[0] for t in tables]}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error initializing schema: {e}")

if __name__ == "__main__":
    init_db()
