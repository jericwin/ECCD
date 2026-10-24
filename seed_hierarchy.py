from db import execute_query
from werkzeug.security import generate_password_hash

def seed_hierarchy():
    hashed_pw = generate_password_hash('password123')
    
    try:
        # 1. Create Province
        res_prov = execute_query("INSERT INTO provinces (name) VALUES ('Test Province')", (), commit=True)
        prov_id = res_prov['lastrowid']
        
        # 2. Create Provincial Admin
        res_prov_user = execute_query(
            "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, 'provincial')",
            ('test_provincial', hashed_pw, 'provincial@test.com'), commit=True
        )
        execute_query("INSERT INTO provincial_admins (user_id, province_id) VALUES (%s, %s)", (res_prov_user['lastrowid'], prov_id), commit=True)
        
        # 3. Create Municipality
        res_mun = execute_query("INSERT INTO municipalities (province_id, name) VALUES (%s, 'Test Municipality')", (prov_id,), commit=True)
        mun_id = res_mun['lastrowid']
        
        # 4. Create Municipality Admin
        res_mun_user = execute_query(
            "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, 'municipality')",
            ('test_municipality', hashed_pw, 'municipality@test.com'), commit=True
        )
        execute_query("INSERT INTO municipality_admins (user_id, municipality_id) VALUES (%s, %s)", (res_mun_user['lastrowid'], mun_id), commit=True)
        
        # 5. Create School
        res_school = execute_query(
            "INSERT INTO schools (municipality_id, name, address, status) VALUES (%s, 'Test School', '123 Test St', 'approved')",
            (mun_id,), commit=True
        )
        school_id = res_school['lastrowid']
        
        # 6. Create School Admin
        res_school_user = execute_query(
            "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, 'school')",
            ('test_school', hashed_pw, 'school@test.com'), commit=True
        )
        execute_query("INSERT INTO school_admins (user_id, school_id) VALUES (%s, %s)", (res_school_user['lastrowid'], school_id), commit=True)
        
        print("Hierarchy seed complete.")
        print("Provincial login -> Username: test_provincial | Password: password123")
        print("Municipality login -> Username: test_municipality | Password: password123")
        print("School login       -> Username: test_school       | Password: password123")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    seed_hierarchy()
