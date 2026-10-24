from db import execute_query
from werkzeug.security import generate_password_hash

def seed_superadmin():
    hashed_pw = generate_password_hash('password123')
    try:
        execute_query(
            "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, 'superadmin')",
            ('superadmin', hashed_pw, 'superadmin@test.com'), commit=True
        )
        print("Superadmin created: Username: superadmin | Password: password123")
    except Exception as e:
        print(f"Error creating superadmin: {e}")

if __name__ == '__main__':
    seed_superadmin()
