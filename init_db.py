import os
from config import Config
from db import get_db_connection, execute_query
from werkzeug.security import generate_password_hash

def init_db():
    print(f"Connecting to database '{Config.DB_NAME}' on {Config.DB_HOST}:{Config.DB_PORT}...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
        if not os.path.exists(schema_path):
            print(f"Error: {schema_path} does not exist!")
            return
            
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            
        statements = schema_sql.split(';')
        for statement in statements:
            stmt = statement.strip()
            if stmt:
                print(f"Executing: {stmt[:60]}...")
                cursor.execute(stmt)
                
        conn.commit()
        print("✓ Database schema tables loaded successfully!")
        
        # Verify created tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_names = [list(t.values())[0] if isinstance(t, dict) else t[0] for t in tables]
        print(f"✓ Found {len(table_names)} tables: {table_names}")
        
        cursor.close()
        conn.close()
        
        # Ensure superadmin user exists
        admin = execute_query("SELECT id FROM users WHERE username = 'superadmin'", fetch_one=True)
        if not admin:
            hashed_pw = generate_password_hash('password123')
            execute_query(
                "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, 'superadmin')",
                ('superadmin', hashed_pw, 'superadmin@test.com'),
                commit=True
            )
            print("✓ Default superadmin created (Username: superadmin | Password: password123)")
        else:
            print("✓ Superadmin account already exists.")
            
        print("\n🎉 Database initialization completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
