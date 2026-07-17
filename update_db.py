from db import execute_query

def add_birth_cert_column():
    try:
        execute_query("ALTER TABLE learners ADD COLUMN birth_certificate VARCHAR(255) DEFAULT NULL", commit=True)
        print("Successfully added birth_certificate column to learners table.")
    except Exception as e:
        print(f"Error or column might already exist: {e}")

if __name__ == '__main__':
    add_birth_cert_column()
