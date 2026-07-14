import mysql.connector
from config import Config

def migrate():
    print("Migrating learners table...")
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("SHOW COLUMNS FROM learners LIKE 'gender'")
        gender_exists = cursor.fetchone()
        
        cursor.execute("SHOW COLUMNS FROM learners LIKE 'birthdate'")
        birthdate_exists = cursor.fetchone()
        
        if not gender_exists:
            print("Adding gender column...")
            cursor.execute("ALTER TABLE learners ADD COLUMN gender VARCHAR(10) DEFAULT 'Male'")
            
        if not birthdate_exists:
            print("Adding birthdate column...")
            cursor.execute("ALTER TABLE learners ADD COLUMN birthdate DATE")
            
        conn.commit()
        print("Migration completed successfully!")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate()
