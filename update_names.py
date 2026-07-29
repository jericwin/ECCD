from db import execute_query

def update_names():
    # Update Teacher
    execute_query("UPDATE users SET username='maria_cruz' WHERE username='test_teacher'", commit=True)
    # The teacher user ID is needed to update the teachers table. Let's just update by the old name if possible, 
    # but we already changed the username. Wait, let's just do it cleanly.
    
    teacher_user = execute_query("SELECT id FROM users WHERE username='maria_cruz' OR username='test_teacher'", fetch_one=True)
    if teacher_user:
        execute_query("UPDATE teachers SET full_name='Maria Clara Cruz' WHERE user_id=%s", (teacher_user['id'],), commit=True)
        execute_query("UPDATE classrooms SET name='Sampaguita Class', subject='Kindergarten' WHERE teacher_id=(SELECT id FROM teachers WHERE user_id=%s)", (teacher_user['id'],), commit=True)
        # update username to maria_cruz if not already
        execute_query("UPDATE users SET username='maria_cruz', email='maria.cruz@gmail.com' WHERE id=%s", (teacher_user['id'],), commit=True)

    # Update Parent
    parent_user = execute_query("SELECT id FROM users WHERE username='juan_delacruz' OR username='test_parent'", fetch_one=True)
    if parent_user:
        execute_query("UPDATE parents SET parent_name='Juan Dela Cruz' WHERE user_id=%s", (parent_user['id'],), commit=True)
        # update username
        execute_query("UPDATE users SET username='juan_delacruz', email='juan.delacruz@gmail.com' WHERE id=%s", (parent_user['id'],), commit=True)
        
        parent_record = execute_query("SELECT id FROM parents WHERE user_id=%s", (parent_user['id'],), fetch_one=True)
        if parent_record:
            pid = parent_record['id']
            # Update learners
            names = [
                'Miguel Dela Cruz', 'Jose Dela Cruz', 'Andres Dela Cruz', 'Emilio Dela Cruz', 
                'Antonio Dela Cruz', 'Apolinario Dela Cruz', 'Diego Dela Cruz', 'Gabriela Dela Cruz', 
                'Melchora Dela Cruz', 'Teresa Dela Cruz'
            ]
            learners = execute_query("SELECT id FROM learners WHERE parent_id=%s ORDER BY id", (pid,), fetch_all=True)
            for idx, l in enumerate(learners):
                if idx < len(names):
                    execute_query("UPDATE learners SET full_name=%s WHERE id=%s", (names[idx], l['id']), commit=True)

    print("Updated names successfully!")
    print("New Teacher login -> Username: maria_cruz | Password: password123")
    print("New Parent login -> Username: juan_delacruz | Password: password123")

if __name__ == '__main__':
    update_names()
