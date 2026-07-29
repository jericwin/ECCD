from db import execute_query
from werkzeug.security import generate_password_hash

def seed():
    hashed_pw = generate_password_hash('password123')
    
    # 1. Create Teacher
    try:
        res_teacher_user = execute_query(
            "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)",
            ('test_teacher', hashed_pw, 'teacher@test.com', 'teacher'),
            commit=True
        )
        teacher_user_id = res_teacher_user['lastrowid']
        
        res_teacher = execute_query(
            "INSERT INTO teachers (user_id, full_name, employee_id, security_answer) VALUES (%s, %s, %s, %s)",
            (teacher_user_id, 'Test Teacher', 'T001', 'dog'),
            commit=True
        )
        teacher_id = res_teacher['lastrowid']
    except Exception as e:
        print(f"Error creating teacher: {e}")
        return

    # 2. Create Parent
    try:
        res_parent_user = execute_query(
            "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)",
            ('test_parent', hashed_pw, 'parent@test.com', 'parent'),
            commit=True
        )
        parent_user_id = res_parent_user['lastrowid']
        
        res_parent = execute_query(
            "INSERT INTO parents (user_id, parent_name) VALUES (%s, %s)",
            (parent_user_id, 'Test Parent'),
            commit=True
        )
        parent_id = res_parent['lastrowid']
    except Exception as e:
        print(f"Error creating parent: {e}")
        return

    # 3. Create Classroom
    try:
        res_classroom = execute_query(
            "INSERT INTO classrooms (teacher_id, name, subject, status, max_learners) VALUES (%s, %s, %s, %s, %s)",
            (teacher_id, 'Test Classroom', 'General', 'active', 30),
            commit=True
        )
        classroom_id = res_classroom['lastrowid']
    except Exception as e:
        print(f"Error creating classroom: {e}")
        return

    # 4. Create 10 Learners and Enroll them
    for i in range(1, 11):
        try:
            res_learner = execute_query(
                "INSERT INTO learners (parent_id, full_name, relationship, learner_id) VALUES (%s, %s, %s, %s)",
                (parent_id, f'Test Learner {i}', 'Parent', f'LRN-TEST-{i:03d}'),
                commit=True
            )
            learner_id = res_learner['lastrowid']
            
            # Enroll learner
            execute_query(
                "INSERT INTO classroom_learners (classroom_id, learner_id) VALUES (%s, %s)",
                (classroom_id, learner_id),
                commit=True
            )
        except Exception as e:
            print(f"Error creating learner {i}: {e}")

    print("Seed complete.")
    print("Teacher login -> Username: test_teacher | Password: password123")
    print("Parent login -> Username: test_parent | Password: password123")

if __name__ == '__main__':
    seed()
