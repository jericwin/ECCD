from db import execute_query

def add_remarks_column():
    try:
        execute_query("ALTER TABLE learners ADD COLUMN birth_certificate_remarks TEXT DEFAULT NULL", commit=True)
        print("Successfully added birth_certificate_remarks column to learners table.")
    except Exception as e:
        print(f"Error or column might already exist: {e}")

if __name__ == '__main__':
    add_remarks_column()
