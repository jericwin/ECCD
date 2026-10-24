from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from db import execute_query
from utils.audit import log_action

school_bp = Blueprint('school', __name__)

@school_bp.route('/school/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'school':
        return redirect(url_for('auth.login'))
        
    admin = execute_query(
        "SELECT sa.*, s.name as school_name FROM school_admins sa JOIN schools s ON sa.school_id = s.id WHERE sa.user_id = %s",
        (session['user_id'],),
        fetch_one=True
    )
    if not admin:
        return redirect(url_for('main.landing'))
        
    s_id = admin['school_id']
    
    # Fetch school details including capacity
    school = execute_query("SELECT is_accepting_enrollees, capacity FROM schools WHERE id = %s", (s_id,), fetch_one=True)
    is_accepting = school['is_accepting_enrollees'] if school else True
    capacity = school['capacity'] if school and school.get('capacity') else 100
    
    # Stats
    teachers_count = execute_query(
        "SELECT COUNT(*) as count FROM teachers WHERE school_id = %s",
        (s_id,), fetch_one=True
    )['count']
    
    pending_enrollments_count = execute_query(
        "SELECT COUNT(*) as count FROM enrollment_requests WHERE school_id = %s AND status = 'pending'",
        (s_id,), fetch_one=True
    )['count']
    
    enrolled_learners_count = execute_query(
        "SELECT COUNT(*) as count FROM enrollment_requests WHERE school_id = %s AND status = 'accepted'",
        (s_id,), fetch_one=True
    )['count']
    
    available_slots = max(0, capacity - enrolled_learners_count)
    
    # Recent Enrollments
    pending_enrollments = execute_query(
        """SELECT er.*, l.full_name as learner_name, p.parent_name
           FROM enrollment_requests er
           JOIN learners l ON er.learner_id = l.id
           JOIN parents p ON l.parent_id = p.id
           WHERE er.school_id = %s AND er.status = 'pending'
           ORDER BY er.created_at ASC LIMIT 10""",
        (s_id,), fetch_all=True
    ) or []
    
    # Teachers list for assignment
    teachers = execute_query("SELECT id, full_name, center_name FROM teachers WHERE school_id = %s", (s_id,), fetch_all=True) or []
    # Classrooms list for assignment
    classrooms = execute_query(
        """SELECT c.*, t.full_name as teacher_name 
           FROM classrooms c 
           JOIN teachers t ON c.teacher_id = t.id 
           WHERE t.school_id = %s AND c.status = 'active'""", 
        (s_id,), fetch_all=True) or []
    
    return render_template(
        'school/dashboard.html',
        admin=admin,
        teachers_count=teachers_count,
        pending_enrollments_count=pending_enrollments_count,
        enrolled_learners_count=enrolled_learners_count,
        available_slots=available_slots,
        pending_enrollments=pending_enrollments,
        teachers=teachers,
        classrooms=classrooms,
        is_accepting=is_accepting,
        active_page='dashboard'
    )

@school_bp.route('/school/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session or session.get('role') != 'school':
        return redirect(url_for('auth.login'))
        
    admin = execute_query("SELECT school_id FROM school_admins WHERE user_id = %s", (session['user_id'],), fetch_one=True)
    s_id = admin['school_id']
    
    if request.method == 'POST':
        name = request.form.get('name')
        capacity = request.form.get('capacity')
        address = request.form.get('address')
        street_address = request.form.get('street_address')
        city_municipality = request.form.get('city_municipality')
        province_name = request.form.get('province_name')
        postal_code = request.form.get('postal_code')
        latitude = request.form.get('latitude') or None
        longitude = request.form.get('longitude') or None
        
        execute_query(
            """UPDATE schools SET name = %s, capacity = %s, address = %s, 
               street_address = %s, city_municipality = %s, province_name = %s, postal_code = %s,
               latitude = %s, longitude = %s WHERE id = %s""",
            (name, capacity, address, street_address, city_municipality, province_name, postal_code, latitude, longitude, s_id), commit=True
        )
        log_action(session['user_id'], 'UPDATED_SCHOOL_PROFILE', 'school', s_id, None, name)
        flash('School profile updated successfully.', 'success')
        return redirect(url_for('school.profile'))
        
    school = execute_query("SELECT * FROM schools WHERE id = %s", (s_id,), fetch_one=True)
    return render_template('school/profile.html', school=school, active_page='profile')

@school_bp.route('/school/settings/toggle_enrollment', methods=['POST'])
def toggle_enrollment():
    if 'user_id' not in session or session.get('role') != 'school':
        return redirect(url_for('auth.login'))
        
    admin = execute_query("SELECT school_id FROM school_admins WHERE user_id = %s", (session['user_id'],), fetch_one=True)
    if admin:
        s_id = admin['school_id']
        school = execute_query("SELECT is_accepting_enrollees FROM schools WHERE id = %s", (s_id,), fetch_one=True)
        new_status = not school['is_accepting_enrollees']
        execute_query("UPDATE schools SET is_accepting_enrollees = %s WHERE id = %s", (new_status, s_id), commit=True)
        
        status_text = "Accepting Enrollees" if new_status else "Not Accepting Enrollees"
        log_action(session['user_id'], 'TOGGLED_ENROLLMENT_STATUS', 'school', s_id, None, status_text)
        flash(f"Enrollment status updated to: {status_text}", "success")
        
    return redirect(url_for('school.dashboard'))

@school_bp.route('/school/learners')
def learners():
    if 'user_id' not in session or session.get('role') != 'school':
        return redirect(url_for('auth.login'))
        
    admin = execute_query("SELECT school_id FROM school_admins WHERE user_id = %s", (session['user_id'],), fetch_one=True)
    s_id = admin['school_id']
    
    # Fetch all active learners for this school
    active_learners = execute_query(
        """SELECT l.*, p.parent_name, c.name as classroom_name, t.full_name as teacher_name
           FROM learners l
           JOIN parents p ON l.parent_id = p.id
           JOIN classroom_learners cl ON l.id = cl.learner_id
           JOIN classrooms c ON cl.classroom_id = c.id
           JOIN teachers t ON c.teacher_id = t.id
           WHERE t.school_id = %s
           ORDER BY l.full_name ASC""",
        (s_id,), fetch_all=True
    ) or []
    
    # Also fetch classrooms so admin can reassign
    classrooms = execute_query(
        """SELECT c.*, t.full_name as teacher_name 
           FROM classrooms c 
           JOIN teachers t ON c.teacher_id = t.id 
           WHERE t.school_id = %s AND c.status = 'active'""", 
        (s_id,), fetch_all=True) or []
        
    return render_template('school/learners.html', learners=active_learners, classrooms=classrooms, active_page='learners')

@school_bp.route('/school/learners/<int:learner_id>/reassign', methods=['POST'])
def reassign_learner(learner_id):
    if 'user_id' not in session or session.get('role') != 'school':
        return redirect(url_for('auth.login'))
        
    admin = execute_query("SELECT school_id FROM school_admins WHERE user_id = %s", (session['user_id'],), fetch_one=True)
    s_id = admin['school_id']
    new_classroom_id = request.form.get('classroom_id')
    
    if new_classroom_id:
        execute_query(
            "UPDATE classroom_learners SET classroom_id = %s WHERE learner_id = %s",
            (new_classroom_id, learner_id), commit=True
        )
        
        # Also update enrollment_requests to match
        execute_query(
            "UPDATE enrollment_requests SET classroom_id = %s WHERE learner_id = %s AND school_id = %s AND status = 'accepted'",
            (new_classroom_id, learner_id, s_id), commit=True
        )
        
        learner = execute_query("SELECT full_name FROM learners WHERE id = %s", (learner_id,), fetch_one=True)
        log_action(session['user_id'], 'REASSIGNED_LEARNER', 'learner', learner_id, None, f"To classroom {new_classroom_id}")
        flash(f"Learner {learner['full_name']} reassigned successfully.", "success")
    else:
        flash("Invalid classroom selected.", "error")
        
    return redirect(url_for('school.learners'))

@school_bp.route('/school/enrollments/<int:req_id>/process', methods=['POST'])
def process_enrollment(req_id):
    if 'user_id' not in session or session.get('role') != 'school':
        return redirect(url_for('auth.login'))
        
    action = request.form.get('action')
    classroom_id = request.form.get('classroom_id')
    
    req = execute_query("SELECT * FROM enrollment_requests WHERE id = %s", (req_id,), fetch_one=True)
    if not req:
        flash('Request not found.', 'error')
        return redirect(url_for('school.dashboard'))
        
    if action == 'accept':
        if not classroom_id:
            flash('You must select a classroom to assign the learner to.', 'error')
            return redirect(url_for('school.dashboard'))
            
        execute_query("UPDATE enrollment_requests SET status = 'accepted', classroom_id = %s WHERE id = %s", (classroom_id, req_id), commit=True)
        # Add to classroom learners
        execute_query(
            "INSERT INTO classroom_learners (classroom_id, learner_id) VALUES (%s, %s)",
            (classroom_id, req['learner_id']), commit=True
        )
        
        log_action(session['user_id'], 'ACCEPTED_ENROLLMENT', 'enrollment_request', req_id, 'pending', 'accepted')
        
        # Notify parent
        learner = execute_query("SELECT parent_id, full_name FROM learners WHERE id = %s", (req['learner_id'],), fetch_one=True)
        parent = execute_query("SELECT user_id FROM parents WHERE id = %s", (learner['parent_id'],), fetch_one=True)
        if parent:
            execute_query(
                "INSERT INTO notifications (user_id, title, message, link_url) VALUES (%s, %s, %s, %s)",
                (parent['user_id'], 'Enrollment Accepted', f"Your enrollment request for {learner['full_name']} has been accepted.", '/parent/dashboard'),
                commit=True
            )
            
        flash('Enrollment accepted and learner assigned to classroom.', 'success')
    elif action == 'reject':
        rejection_reason = request.form.get('rejection_reason')
        execute_query("UPDATE enrollment_requests SET status = 'rejected', rejection_reason = %s WHERE id = %s", (rejection_reason, req_id), commit=True)
        
        log_action(session['user_id'], 'REJECTED_ENROLLMENT', 'enrollment_request', req_id, 'pending', 'rejected')
        
        # Notify parent
        learner = execute_query("SELECT parent_id, full_name FROM learners WHERE id = %s", (req['learner_id'],), fetch_one=True)
        parent = execute_query("SELECT user_id FROM parents WHERE id = %s", (learner['parent_id'],), fetch_one=True)
        if parent:
            msg = f"Your enrollment request for {learner['full_name']} was rejected."
            if rejection_reason:
                msg += f" Reason: {rejection_reason}"
            execute_query(
                "INSERT INTO notifications (user_id, title, message, link_url) VALUES (%s, %s, %s, %s)",
                (parent['user_id'], 'Enrollment Rejected', msg, '/parent/dashboard'),
                commit=True
            )
            
        flash('Enrollment request rejected.', 'info')
        
    # Redirect back to where they came from
    referrer = request.referrer
    if referrer and '/school/enrollments' in referrer:
        return redirect(url_for('school.enrollments'))
    return redirect(url_for('school.dashboard'))

@school_bp.route('/school/enrollments')
def enrollments():
    if 'user_id' not in session or session.get('role') != 'school':
        return redirect(url_for('auth.login'))
        
    admin = execute_query("SELECT school_id FROM school_admins WHERE user_id = %s", (session['user_id'],), fetch_one=True)
    s_id = admin['school_id']
    
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    query = """
        SELECT er.*, l.full_name as learner_name, p.parent_name
        FROM enrollment_requests er
        JOIN learners l ON er.learner_id = l.id
        JOIN parents p ON l.parent_id = p.id
        WHERE er.school_id = %s
    """
    params = [s_id]
    
    if search:
        query += " AND l.full_name LIKE %s"
        params.append(f"%{search}%")
        
    if status_filter:
        query += " AND er.status = %s"
        params.append(status_filter)
        
    query += " ORDER BY er.created_at DESC"
    
    enrollments_list = execute_query(query, tuple(params), fetch_all=True) or []
    
    classrooms = execute_query(
        """SELECT c.*, t.full_name as teacher_name 
           FROM classrooms c 
           JOIN teachers t ON c.teacher_id = t.id 
           WHERE t.school_id = %s AND c.status = 'active'""", 
        (s_id,), fetch_all=True) or []
        
    return render_template('school/enrollments.html', enrollments=enrollments_list, classrooms=classrooms, active_page='enrollments')

@school_bp.route('/school/teachers', methods=['GET', 'POST'])
def manage_teachers():
    if 'user_id' not in session or session.get('role') != 'school':
        return redirect(url_for('auth.login'))
        
    admin = execute_query("SELECT school_id FROM school_admins WHERE user_id = %s", (session['user_id'],), fetch_one=True)
    s_id = admin['school_id']
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            username = request.form.get('username')
            password = request.form.get('password')
            email = request.form.get('email')
            full_name = request.form.get('full_name')
            center_name = request.form.get('center_name', '')
            
            hashed_pw = generate_password_hash(password)
            try:
                user_res = execute_query(
                    "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, 'teacher')",
                    (username, hashed_pw, email), commit=True
                )
                execute_query(
                    "INSERT INTO teachers (user_id, school_id, full_name, center_name) VALUES (%s, %s, %s, %s)",
                    (user_res['lastrowid'], s_id, full_name, center_name), commit=True
                )
                flash('Teacher account created successfully.', 'success')
            except Exception as e:
                flash(f'Error creating teacher: {e}', 'error')
                
        elif action == 'delete':
            teacher_id = request.form.get('teacher_id')
            teacher = execute_query("SELECT user_id FROM teachers WHERE id = %s AND school_id = %s", (teacher_id, s_id), fetch_one=True)
            if teacher:
                # Delete user (cascades to teacher if FK constraints are set, else manual delete)
                execute_query("DELETE FROM users WHERE id = %s", (teacher['user_id'],), commit=True)
                flash('Teacher account deleted.', 'success')
            else:
                flash('Teacher not found or unauthorized.', 'error')
                
        return redirect(url_for('school.manage_teachers'))
        
    teachers = execute_query(
        """SELECT t.*, u.username, u.email,
           (SELECT COUNT(*) FROM classrooms c WHERE c.teacher_id = t.id AND c.status = 'active') as active_classes
           FROM teachers t 
           JOIN users u ON t.user_id = u.id 
           WHERE t.school_id = %s""",
        (s_id,), fetch_all=True
    ) or []
    
    return render_template('school/teachers.html', teachers=teachers, active_page='manage_teachers')

@school_bp.route('/school/teachers/<int:teacher_id>/toggle', methods=['POST'])
def toggle_teacher(teacher_id):
    if 'user_id' not in session or session.get('role') != 'school':
        return redirect(url_for('auth.login'))
        
    admin = execute_query("SELECT school_id FROM school_admins WHERE user_id = %s", (session['user_id'],), fetch_one=True)
    s_id = admin['school_id']
    
    teacher = execute_query("SELECT is_active, full_name FROM teachers WHERE id = %s AND school_id = %s", (teacher_id, s_id), fetch_one=True)
    if teacher:
        new_status = not teacher['is_active']
        execute_query("UPDATE teachers SET is_active = %s WHERE id = %s", (new_status, teacher_id), commit=True)
        status_str = 'Activated' if new_status else 'Deactivated'
        log_action(session['user_id'], 'TOGGLED_TEACHER_STATUS', 'teacher', teacher_id, None, status_str)
        flash(f"Teacher {teacher['full_name']} has been {status_str.lower()}.", "success")
    else:
        flash("Teacher not found or unauthorized.", "error")
        
    return redirect(url_for('school.manage_teachers'))

@school_bp.route('/school/teachers/<int:teacher_id>/edit', methods=['POST'])
def edit_teacher(teacher_id):
    if 'user_id' not in session or session.get('role') != 'school':
        return redirect(url_for('auth.login'))
        
    admin = execute_query("SELECT school_id FROM school_admins WHERE user_id = %s", (session['user_id'],), fetch_one=True)
    s_id = admin['school_id']
    
    full_name = request.form.get('full_name')
    center_name = request.form.get('center_name', '')
    
    teacher = execute_query("SELECT id FROM teachers WHERE id = %s AND school_id = %s", (teacher_id, s_id), fetch_one=True)
    if teacher:
        execute_query(
            "UPDATE teachers SET full_name = %s, center_name = %s WHERE id = %s",
            (full_name, center_name, teacher_id), commit=True
        )
        log_action(session['user_id'], 'EDITED_TEACHER', 'teacher', teacher_id, None, full_name)
        flash("Teacher information updated successfully.", "success")
    else:
        flash("Teacher not found or unauthorized.", "error")
        
    return redirect(url_for('school.manage_teachers'))
