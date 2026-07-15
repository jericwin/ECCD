import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from db import execute_query

auth_bp = Blueprint('auth', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_identity = request.form.get('login_identity')
        password = request.form.get('password')
        
        if not login_identity or not password:
            flash('All fields are required.', 'error')
            return render_template('login.html', login_identity=login_identity)
            
        # Lookup user by username OR email
        user = execute_query(
            "SELECT * FROM users WHERE (username = %s OR email = %s)",
            (login_identity, login_identity),
            fetch_one=True
        )
        
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            role = user['role']
            
            # Cache profile data in session to avoid redundant DB queries on every navigation
            if role == 'teacher':
                teacher = execute_query("SELECT id, full_name, center_name, position, profile_photo, theme FROM teachers WHERE user_id = %s", (user['id'],), fetch_one=True)
                if teacher:
                    session['theme'] = teacher.get('theme', 'green')
                    session['profile'] = teacher
            elif role == 'parent':
                parent = execute_query("SELECT id, parent_name, mobile, address, theme FROM parents WHERE user_id = %s", (user['id'],), fetch_one=True)
                if parent:
                    session['theme'] = parent.get('theme', 'green')
                    # Convert dates in learner record to string so it can be JSON serialized in Flask session cookie
                    learner = execute_query("SELECT id, learner_id, full_name, center_name, photo, gender, birthdate FROM learners WHERE parent_id = %s", (parent['id'],), fetch_one=True)
                    if learner:
                        if learner.get('birthdate'):
                            learner['birthdate'] = str(learner['birthdate'])
                    session['profile'] = {
                        'parent': parent,
                        'learner': learner
                    }
            
            flash('Logged in successfully!', 'success')
            
            if role == 'teacher':
                return redirect(url_for('teacher.dashboard'))
            elif role == 'parent':
                return redirect(url_for('parent.dashboard'))
        else:
            flash('Invalid username/email or password. Please try again.', 'error')
            return render_template('login.html', login_identity=login_identity)
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.landing'))

@auth_bp.route('/register/teacher', methods=['GET', 'POST'])
def register_teacher():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        employee_id = request.form.get('employee_id')
        position = request.form.get('position')
        center_name = request.form.get('center_name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        address = request.form.get('address')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        security_answer = request.form.get('security_answer')
        
        form_data = {
            'full_name': full_name, 'employee_id': employee_id, 'position': position,
            'center_name': center_name, 'email': email, 'mobile': mobile,
            'address': address, 'username': username
        }
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register_teacher.html', form_data=form_data)
            
        # Check duplicate username or email
        existing_user = execute_query(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (username, email),
            fetch_one=True
        )
        if existing_user:
            flash('Username or Email already registered.', 'error')
            return render_template('register_teacher.html', form_data=form_data)
            
        # Check duplicate employee ID
        existing_emp = execute_query(
            "SELECT id FROM teachers WHERE employee_id = %s",
            (employee_id,),
            fetch_one=True
        )
        if existing_emp:
            flash('Employee ID already registered.', 'error')
            return render_template('register_teacher.html', form_data=form_data)
            
        # Handle file upload
        photo_filename = None
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename != '' and allowed_file(file.filename):
                os.makedirs(os.path.join(current_app.config['UPLOAD_FOLDER'], 'teachers'), exist_ok=True)
                ext = file.filename.rsplit('.', 1)[1].lower()
                photo_filename = f"teacher_{username}.{ext}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'teachers', photo_filename))

        # Insert user
        hashed_pw = generate_password_hash(password)
        try:
            user_res = execute_query(
                "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)",
                (username, hashed_pw, email, 'teacher'),
                commit=True
            )
            user_id = user_res['lastrowid']
            
            # Insert teacher profile
            execute_query(
                """INSERT INTO teachers (user_id, full_name, employee_id, position, center_name, mobile, address, profile_photo, security_answer) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (user_id, full_name, employee_id, position, center_name, mobile, address, photo_filename, security_answer),
                commit=True
            )
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login', role='teacher'))
        except Exception as e:
            flash(f'An error occurred during registration: {e}', 'error')
            return render_template('register_teacher.html', form_data=form_data)

    return render_template('register_teacher.html', form_data={})

@auth_bp.route('/register/parent', methods=['GET', 'POST'])
def register_parent():
    if request.method == 'POST':
        # Parent fields
        parent_name = request.form.get('parent_name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        relationship = request.form.get('relationship')
        address = request.form.get('address')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Child fields
        learner_full_name = request.form.get('learner_full_name')
        learner_id = request.form.get('learner_id')
        center_name = request.form.get('center_name')
        gender = request.form.get('gender')
        birthdate = request.form.get('birthdate')
        
        form_data = {
            'parent_name': parent_name, 'email': email, 'mobile': mobile,
            'relationship': relationship, 'address': address, 'username': username,
            'learner_full_name': learner_full_name, 'learner_id': learner_id, 'center_name': center_name,
            'gender': gender, 'birthdate': birthdate
        }
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register_parent.html', form_data=form_data)
            
        # Check duplicate username or email
        existing_user = execute_query(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (username, email),
            fetch_one=True
        )
        if existing_user:
            flash('Username or Email already registered.', 'error')
            return render_template('register_parent.html', form_data=form_data)
            
        # Check duplicate learner ID
        existing_lrn = execute_query(
            "SELECT id FROM learners WHERE learner_id = %s",
            (learner_id,),
            fetch_one=True
        )
        if existing_lrn:
            flash('Learner ID (LRN) already registered.', 'error')
            return render_template('register_parent.html', form_data=form_data)
            
        # Handle file upload
        photo_filename = None
        if 'learner_photo' in request.files:
            file = request.files['learner_photo']
            if file and file.filename != '' and allowed_file(file.filename):
                os.makedirs(os.path.join(current_app.config['UPLOAD_FOLDER'], 'learners'), exist_ok=True)
                ext = file.filename.rsplit('.', 1)[1].lower()
                photo_filename = f"learner_{learner_id}.{ext}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'learners', photo_filename))

        # Insert user
        hashed_pw = generate_password_hash(password)
        try:
            user_res = execute_query(
                "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)",
                (username, hashed_pw, email, 'parent'),
                commit=True
            )
            user_id = user_res['lastrowid']
            
            # Insert parent profile
            parent_res = execute_query(
                "INSERT INTO parents (user_id, parent_name, mobile, address) VALUES (%s, %s, %s, %s)",
                (user_id, parent_name, mobile, address),
                commit=True
            )
            parent_pk = parent_res['lastrowid']
            
            # Insert learner
            execute_query(
                "INSERT INTO learners (parent_id, learner_id, full_name, relationship, center_name, photo, gender, birthdate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (parent_pk, learner_id, learner_full_name, relationship, center_name, photo_filename, gender, birthdate),
                commit=True
            )
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login', role='parent'))
        except Exception as e:
            flash(f'An error occurred during registration: {e}', 'error')
            return render_template('register_parent.html', form_data=form_data)

    return render_template('register_parent.html', form_data={})

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    step = int(request.form.get('step', 1))
    
    if request.method == 'POST':
        if step == 1:
            username = request.form.get('username')
            email = request.form.get('email')
            role = request.form.get('role')
            
            # Look up user
            user = execute_query(
                "SELECT id, role FROM users WHERE username = %s AND email = %s AND role = %s",
                (username, email, role),
                fetch_one=True
            )
            
            if user:
                return render_template('forgot_password.html', step=2, user_id=user['id'], role=user['role'])
            else:
                flash('No matching account found with those details.', 'error')
                return render_template('forgot_password.html', step=1)
                
        elif step == 2:
            user_id = request.form.get('user_id')
            answer = request.form.get('answer')
            
            # Check user role
            user = execute_query("SELECT role FROM users WHERE id = %s", (user_id,), fetch_one=True)
            if not user:
                flash('Something went wrong. Start again.', 'error')
                return render_template('forgot_password.html', step=1)
                
            role = user['role']
            verified = False
            
            if role == 'teacher':
                teacher = execute_query("SELECT security_answer FROM teachers WHERE user_id = %s", (user_id,), fetch_one=True)
                if teacher and teacher['security_answer'].lower().strip() == answer.lower().strip():
                    verified = True
            elif role == 'parent':
                # Check child LRN associated with this parent
                learner = execute_query(
                    """SELECT l.learner_id FROM learners l 
                       JOIN parents p ON l.parent_id = p.id 
                       WHERE p.user_id = %s""", 
                    (user_id,), fetch_one=True
                )
                if learner and learner['learner_id'].lower().strip() == answer.lower().strip():
                    verified = True
                    
            if verified:
                return render_template('forgot_password.html', step=3, user_id=user_id)
            else:
                flash('Verification failed. Invalid answer.', 'error')
                return render_template('forgot_password.html', step=2, user_id=user_id, role=role)
                
        elif step == 3:
            user_id = request.form.get('user_id')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('forgot_password.html', step=3, user_id=user_id)
                
            hashed_pw = generate_password_hash(password)
            try:
                execute_query("UPDATE users SET password = %s WHERE id = %s", (hashed_pw, user_id), commit=True)
                flash('Password reset successful! You can now log in.', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                flash(f'An error occurred: {e}', 'error')
                return render_template('forgot_password.html', step=3, user_id=user_id)
                
    return render_template('forgot_password.html', step=1)
