import db
from werkzeug.security import generate_password_hash

def seed():
    password = generate_password_hash("password123")
    
    # 1. Superadmin (already created in previous run maybe? Let's check or ignore error)
    try:
        db.execute_query("INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)", ('superadmin', password, 'super@eccd.gov.ph', 'superadmin'), commit=True)
        print("Created SuperAdmin: superadmin / password123")
    except Exception as e:
        print("Superadmin exists:", e)
        
    # 2. Province & Provincial Admin
    try:
        prov_res = db.execute_query("INSERT INTO provinces (name) VALUES (%s)", ('Metro Manila',), commit=True)
        prov_id = prov_res['lastrowid']
        p_user_id = db.execute_query("INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)", ('provincial', password, 'provincial@eccd.gov.ph', 'provincial'), commit=True)['lastrowid']
        db.execute_query("INSERT INTO provincial_admins (user_id, province_id) VALUES (%s, %s)", (p_user_id, prov_id), commit=True)
        print("Created Provincial: provincial / password123")
    except Exception as e:
        print("Provincial exists:", e)
        prov_id = db.execute_query("SELECT id FROM provinces WHERE name='Metro Manila'", fetch_one=True)['id']
    
    # 3. Municipality & Municipal Admin
    try:
        mun_res = db.execute_query("INSERT INTO municipalities (province_id, name) VALUES (%s, %s)", (prov_id, 'Quezon City'), commit=True)
        mun_id = mun_res['lastrowid']
        m_user_id = db.execute_query("INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)", ('municipality', password, 'qc@eccd.gov.ph', 'municipality'), commit=True)['lastrowid']
        db.execute_query("INSERT INTO municipality_admins (user_id, municipality_id) VALUES (%s, %s)", (m_user_id, mun_id), commit=True)
        print("Created Municipality: municipality / password123")
    except Exception as e:
        print("Municipality exists:", e)
        mun_id = db.execute_query("SELECT id FROM municipalities WHERE name='Quezon City'", fetch_one=True)['id']
    
    # 4. School & School Admin
    try:
        school_res = db.execute_query("INSERT INTO schools (municipality_id, name, address, status, is_accepting_enrollees) VALUES (%s, %s, %s, %s, %s)", (mun_id, 'QC Central Daycare', 'Commonwealth, QC', 'approved', True), commit=True)
        school_id = school_res['lastrowid']
        s_user_id = db.execute_query("INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)", ('schooladmin', password, 'school@eccd.gov.ph', 'school'), commit=True)['lastrowid']
        db.execute_query("INSERT INTO school_admins (user_id, school_id) VALUES (%s, %s)", (s_user_id, school_id), commit=True)
        print("Created School: schooladmin / password123")
    except Exception as e:
        print("School exists:", e)

if __name__ == '__main__':
    seed()
