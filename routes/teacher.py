import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from db import execute_query

teacher_bp = Blueprint('teacher', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_teacher_profile(user_id):
    if 'profile' in session and session.get('role') == 'teacher':
        return session['profile']
    return execute_query("SELECT * FROM teachers WHERE user_id = %s", (user_id,), fetch_one=True)

@teacher_bp.route('/teacher/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'teacher':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    if not teacher:
        flash('Teacher profile not found.', 'error')
        return redirect(url_for('main.landing'))
        
    # Get active/draft/archived classrooms
    classrooms = execute_query(
        """SELECT c.*, 
           (SELECT COUNT(*) FROM classroom_learners cl WHERE cl.classroom_id = c.id) as learners_count
           FROM classrooms c WHERE c.teacher_id = %s""",
        (teacher['id'],),
        fetch_all=True
    ) or []
    
    # Calculate stats
    classrooms_count = len([c for c in classrooms if c['status'] == 'active'])
    learners_count = sum(c['learners_count'] for c in classrooms)
    
    announcements_count = 0
    if classrooms:
        class_ids = [c['id'] for c in classrooms]
        format_strings = ','.join(['%s'] * len(class_ids))
        res = execute_query(
            f"SELECT COUNT(*) as count FROM posts WHERE classroom_id IN ({format_strings})",
            tuple(class_ids),
            fetch_one=True
        )
        if res:
            announcements_count = res['count']
            
    return render_template(
        'teacher/dashboard.html',
        active_page='dashboard',
        teacher=teacher,
        classrooms=classrooms[:4],  # limit to 4 on dashboard quick list
        classrooms_count=classrooms_count,
        learners_count=learners_count,
        announcements_count=announcements_count
    )

@teacher_bp.route('/teacher/classrooms')
def classrooms():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    if not teacher:
        return redirect(url_for('main.landing'))
        
    classrooms = execute_query(
        """SELECT c.*, 
           (SELECT COUNT(*) FROM classroom_learners cl WHERE cl.classroom_id = c.id) as learners_count
           FROM classrooms c WHERE c.teacher_id = %s""",
        (teacher['id'],),
        fetch_all=True
    ) or []
    
    return render_template('teacher/classrooms.html', active_page='classrooms', classrooms=classrooms)

@teacher_bp.route('/teacher/classrooms/create', methods=['GET', 'POST'])
def create_classroom():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    if not teacher:
        return redirect(url_for('main.landing'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        subject = request.form.get('subject')
        description = request.form.get('description')
        age_group = request.form.get('age_group')
        school_year = request.form.get('school_year')
        schedule = request.form.get('schedule')
        theme_color = request.form.get('theme_color', 'success')
        max_learners = request.form.get('max_learners', 30)
        action = request.form.get('action', 'publish')  # 'publish' or 'draft'
        
        status = 'active' if action == 'publish' else 'draft'
        
        # Handle file upload
        banner_filename = None
        if 'banner' in request.files:
            file = request.files['banner']
            if file and file.filename != '' and allowed_file(file.filename):
                os.makedirs(os.path.join(current_app.config['UPLOAD_FOLDER'], 'classrooms'), exist_ok=True)
                ext = file.filename.rsplit('.', 1)[1].lower()
                # Unique name using epoch-millisecond or simple safe conversion
                banner_filename = f"banner_{teacher['id']}_{secure_filename(file.filename)}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'classrooms', banner_filename))
                
        try:
            execute_query(
                """INSERT INTO classrooms (teacher_id, name, subject, description, age_group, school_year, schedule, theme_color, max_learners, banner, status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (teacher['id'], name, subject, description, age_group, school_year, schedule, theme_color, max_learners, banner_filename, status),
                commit=True
            )
            flash(f"Classroom '{name}' created successfully!", "success")
            return redirect(url_for('teacher.classrooms'))
        except Exception as e:
            flash(f"Error creating classroom: {e}", "error")
            
    return render_template('teacher/create_classroom.html', active_page='create_classroom')

@teacher_bp.route('/teacher/classrooms/<int:classroom_id>')
def classroom_view(classroom_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    classroom = execute_query("SELECT * FROM classrooms WHERE id = %s AND teacher_id = %s", (classroom_id, teacher['id']), fetch_one=True)
    if not classroom:
        flash("Classroom not found.", "error")
        return redirect(url_for('teacher.classrooms'))
        
    # Get posts (stream)
    posts = execute_query("SELECT * FROM posts WHERE classroom_id = %s ORDER BY is_pinned DESC, created_at DESC", (classroom_id,), fetch_all=True) or []
    
    # Get classwork files
    classwork = execute_query("SELECT * FROM classwork WHERE classroom_id = %s ORDER BY created_at DESC", (classroom_id,), fetch_all=True) or []
    
    # Get enrolled learners
    enrolled_learners = execute_query(
        """SELECT l.*, p.parent_name, cl.id as enrollment_id FROM learners l
           JOIN classroom_learners cl ON cl.learner_id = l.id
           JOIN parents p ON l.parent_id = p.id
           WHERE cl.classroom_id = %s""",
        (classroom_id,),
        fetch_all=True
    ) or []
    
    # Get registered learners not enrolled in *this* class
    enrolled_ids = [el['id'] for el in enrolled_learners]
    if enrolled_ids:
        format_strings = ','.join(['%s'] * len(enrolled_ids))
        unassigned_learners = execute_query(
            f"SELECT l.* FROM learners l WHERE l.id NOT IN ({format_strings})",
            tuple(enrolled_ids),
            fetch_all=True
        ) or []
    else:
        unassigned_learners = execute_query("SELECT * FROM learners", (), fetch_all=True) or []
        
    # Get recorded assessments/grades
    grades = []
    if enrolled_ids:
        format_strings = ','.join(['%s'] * len(enrolled_ids))
        grades = execute_query(
            f"SELECT * FROM assessments WHERE learner_id IN ({format_strings})",
            tuple(enrolled_ids),
            fetch_all=True
        ) or []
        
    # Map grades into a dictionary for quick lookup: (learner_id, classwork_id) -> grade dict
    grades_dict = {(g['learner_id'], g['classwork_id']): g for g in grades}
         
    # Dashboard Data
    upcoming_classwork = execute_query(
        "SELECT * FROM classwork WHERE classroom_id = %s AND due_date >= CURDATE() ORDER BY due_date ASC LIMIT 5",
        (classroom_id,),
        fetch_all=True
    ) or []
    
    recent_submissions = execute_query(
        """SELECT cs.*, l.full_name, cw.title 
           FROM classwork_submissions cs 
           JOIN classwork cw ON cs.classwork_id = cw.id 
           JOIN learners l ON cs.learner_id = l.id 
           LEFT JOIN assessments a ON a.classwork_id = cs.classwork_id AND a.learner_id = cs.learner_id
           WHERE cw.classroom_id = %s AND a.id IS NULL
           ORDER BY cs.submitted_at DESC LIMIT 5""",
        (classroom_id,),
        fetch_all=True
    ) or []
         
    return render_template(
        'teacher/classroom_view.html',
        active_page='classrooms',
        classroom=classroom,
        posts=posts,
        classwork=classwork,
        enrolled_learners=enrolled_learners,
        unassigned_learners=unassigned_learners,
        grades_dict=grades_dict,
        upcoming_classwork=upcoming_classwork,
        recent_submissions=recent_submissions
    )

@teacher_bp.route('/teacher/classrooms/<int:classroom_id>/grades/save', methods=['POST'])
def save_grades(classroom_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    classroom = execute_query("SELECT id FROM classrooms WHERE id = %s AND teacher_id = %s", (classroom_id, teacher['id']), fetch_one=True)
    if not classroom:
        return redirect(url_for('teacher.classrooms'))
        
    # Find all assessments (classwork of type 'assessment')
    assessments_list = execute_query(
        "SELECT id FROM classwork WHERE classroom_id = %s AND type = 'assessment'",
        (classroom_id,),
        fetch_all=True
    ) or []
    
    # Find all enrolled learners
    enrolled_learners = execute_query(
        "SELECT learner_id FROM classroom_learners WHERE classroom_id = %s",
        (classroom_id,),
        fetch_all=True
    ) or []
    
    try:
        for el in enrolled_learners:
            l_id = el['learner_id']
            for ass in assessments_list:
                ass_id = ass['id']
                # Retrieve input score and remarks
                score_str = request.form.get(f'score_{l_id}_{ass_id}', '').strip()
                remarks = request.form.get(f'remarks_{l_id}_{ass_id}', '').strip()
                
                score = int(score_str) if score_str.isdigit() else None
                
                if score is not None or remarks:
                    # Save or update score
                    execute_query(
                        """INSERT INTO assessments (learner_id, classwork_id, score, remarks) 
                           VALUES (%s, %s, %s, %s)
                           ON DUPLICATE KEY UPDATE score = %s, remarks = %s""",
                        (l_id, ass_id, score, remarks, score, remarks),
                        commit=True
                    )
        flash("Student assessments saved successfully!", "success")
    except Exception as e:
        flash(f"Error saving grades: {e}", "error")
        
    return redirect(url_for('teacher.classroom_view', classroom_id=classroom_id))

@teacher_bp.route('/teacher/classrooms/<int:classroom_id>/post', methods=['POST'])
def post_stream(classroom_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    classroom = execute_query("SELECT id FROM classrooms WHERE id = %s AND teacher_id = %s", (classroom_id, teacher['id']), fetch_one=True)
    if not classroom:
        return redirect(url_for('teacher.classrooms'))
        
    post_type = request.form.get('type', 'announcement')
    title = request.form.get('title')
    content = request.form.get('content')
    is_pinned = 'is_pinned' in request.form
    
    file_filename = None
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '' and allowed_file(file.filename):
            os.makedirs(os.path.join(current_app.config['UPLOAD_FOLDER'], 'posts'), exist_ok=True)
            ext = file.filename.rsplit('.', 1)[1].lower()
            file_filename = f"post_{classroom_id}_{secure_filename(file.filename)}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'posts', file_filename))
            
    try:
        execute_query(
            """INSERT INTO posts (classroom_id, type, title, content, file_path, is_pinned)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (classroom_id, post_type, title, content, file_filename, is_pinned),
            commit=True
        )
        flash("Successfully posted to stream!", "success")
    except Exception as e:
        flash(f"Error publishing post: {e}", "error")
        
    return redirect(url_for('teacher.classroom_view', classroom_id=classroom_id))

@teacher_bp.route('/teacher/classrooms/<int:classroom_id>/classwork', methods=['POST'])
def create_classwork(classroom_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    classroom = execute_query("SELECT id FROM classrooms WHERE id = %s AND teacher_id = %s", (classroom_id, teacher['id']), fetch_one=True)
    if not classroom:
        return redirect(url_for('teacher.classrooms'))
        
    subject_folder = request.form.get('subject_folder')
    title = request.form.get('title')
    classwork_type = request.form.get('type')
    description = request.form.get('description')
    due_date = request.form.get('due_date') or None
    
    file_filename = None
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '' and allowed_file(file.filename):
            os.makedirs(os.path.join(current_app.config['UPLOAD_FOLDER'], 'classwork'), exist_ok=True)
            file_filename = f"classwork_{classroom_id}_{secure_filename(file.filename)}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'classwork', file_filename))
            
    try:
        execute_query(
            """INSERT INTO classwork (classroom_id, subject_folder, type, title, description, file_path, due_date)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (classroom_id, subject_folder, classwork_type, title, description, file_filename, due_date),
            commit=True
        )
        
        # Get the ID of the newly created classwork
        new_cw = execute_query("SELECT LAST_INSERT_ID() as id", (), fetch_one=True)
        cw_id = new_cw['id'] if new_cw else None
        
        # Notify parents of all enrolled learners
        parents = execute_query(
            """SELECT DISTINCT p.user_id FROM parents p
               JOIN learners l ON p.id = l.parent_id
               JOIN classroom_learners cl ON l.id = cl.learner_id
               WHERE cl.classroom_id = %s""",
            (classroom_id,),
            fetch_all=True
        ) or []
        
        if cw_id:
            for p in parents:
                msg = f"New {classwork_type} posted: {title}"
                link = url_for('parent.classwork_submission', classwork_id=cw_id)
                execute_query(
                    """INSERT INTO notifications (user_id, title, message, link_url)
                       VALUES (%s, %s, %s, %s)""",
                    (p['user_id'], 'New Classwork', msg, link),
                    commit=True
                )
                
        flash(f"Uploaded resource under '{subject_folder}' successfully!", "success")
    except Exception as e:
        flash(f"Error saving classwork: {e}", "error")
        
    return redirect(url_for('teacher.classroom_view', classroom_id=classroom_id))

@teacher_bp.route('/teacher/classrooms/<int:classroom_id>/assign-learner', methods=['POST'])
def assign_learner(classroom_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    classroom = execute_query("SELECT id FROM classrooms WHERE id = %s AND teacher_id = %s", (classroom_id, teacher['id']), fetch_one=True)
    if not classroom:
        return redirect(url_for('teacher.classrooms'))
        
    learner_id = request.form.get('learner_id')
    if not learner_id:
        flash("No learner selected.", "error")
        return redirect(url_for('teacher.classroom_view', classroom_id=classroom_id))
        
    try:
        execute_query(
            "INSERT INTO classroom_learners (classroom_id, learner_id) VALUES (%s, %s)",
            (classroom_id, learner_id),
            commit=True
        )
        flash("Learner assigned successfully!", "success")
    except Exception as e:
        flash(f"Error enrolling learner: {e}", "error")
        
    return redirect(url_for('teacher.classroom_view', classroom_id=classroom_id))

@teacher_bp.route('/teacher/classrooms/<int:classroom_id>/remove-learner/<int:learner_id>', methods=['POST'])
def remove_learner(classroom_id, learner_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    classroom = execute_query("SELECT id FROM classrooms WHERE id = %s AND teacher_id = %s", (classroom_id, teacher['id']), fetch_one=True)
    if not classroom:
        return redirect(url_for('teacher.classrooms'))
        
    try:
        execute_query(
            "DELETE FROM classroom_learners WHERE classroom_id = %s AND learner_id = %s",
            (classroom_id, learner_id),
            commit=True
        )
        flash("Learner removed from classroom.", "success")
    except Exception as e:
        flash(f"Error unenrolling learner: {e}", "error")
        
    return redirect(url_for('teacher.classroom_view', classroom_id=classroom_id))

@teacher_bp.route('/teacher/classrooms/<int:classroom_id>/archive', methods=['POST'])
def archive_classroom(classroom_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
    execute_query("UPDATE classrooms SET status = 'archived' WHERE id = %s", (classroom_id,), commit=True)
    flash("Classroom archived successfully.", "success")
    return redirect(url_for('teacher.classrooms'))

@teacher_bp.route('/teacher/classrooms/<int:classroom_id>/activate', methods=['POST'])
def activate_classroom(classroom_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
    execute_query("UPDATE classrooms SET status = 'active' WHERE id = %s", (classroom_id,), commit=True)
    flash("Classroom restored.", "success")
    return redirect(url_for('teacher.classrooms'))

@teacher_bp.route('/teacher/classrooms/<int:classroom_id>/publish', methods=['POST'])
def publish_classroom(classroom_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
    execute_query("UPDATE classrooms SET status = 'active' WHERE id = %s", (classroom_id,), commit=True)
    flash("Classroom published successfully.", "success")
    return redirect(url_for('teacher.classrooms'))

@teacher_bp.route('/teacher/classrooms/<int:classroom_id>/delete', methods=['POST'])
def delete_classroom(classroom_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
    execute_query("DELETE FROM classrooms WHERE id = %s", (classroom_id,), commit=True)
    flash("Classroom deleted.", "success")
    return redirect(url_for('teacher.classrooms'))

@teacher_bp.route('/teacher/enrollment_requests')
def enrollment_requests():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    if not teacher:
        return redirect(url_for('main.landing'))
        
    classroom_filter = request.args.get('classroom_id', '')
    
    # Get all classrooms for this teacher for the filter dropdown
    classrooms = execute_query(
        "SELECT id, name FROM classrooms WHERE teacher_id = %s ORDER BY name ASC",
        (teacher['id'],),
        fetch_all=True
    ) or []
        
    if classroom_filter:
        requests_list = execute_query(
            """SELECT er.*, l.full_name as learner_name, p.parent_name, c.name as classroom_name 
               FROM enrollment_requests er
               JOIN learners l ON er.learner_id = l.id
               JOIN parents p ON l.parent_id = p.id
               JOIN classrooms c ON er.classroom_id = c.id
               WHERE c.teacher_id = %s AND er.status = 'pending' AND c.id = %s
               ORDER BY er.created_at DESC""",
            (teacher['id'], classroom_filter),
            fetch_all=True
        ) or []
    else:
        requests_list = execute_query(
            """SELECT er.*, l.full_name as learner_name, p.parent_name, c.name as classroom_name 
               FROM enrollment_requests er
               JOIN learners l ON er.learner_id = l.id
               JOIN parents p ON l.parent_id = p.id
               JOIN classrooms c ON er.classroom_id = c.id
               WHERE c.teacher_id = %s AND er.status = 'pending'
               ORDER BY er.created_at DESC""",
            (teacher['id'],),
            fetch_all=True
        ) or []
    
    return render_template(
        'teacher/enrollment_requests.html',
        active_page='enrollment_requests',
        requests=requests_list,
        classrooms=classrooms,
        classroom_filter=classroom_filter
    )

@teacher_bp.route('/teacher/enrollment_requests/<int:request_id>', methods=['POST'])
def handle_enrollment_request(request_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    
    # Verify the request belongs to one of this teacher's classrooms
    en_request = execute_query(
        """SELECT er.* FROM enrollment_requests er
           JOIN classrooms c ON er.classroom_id = c.id
           WHERE er.id = %s AND c.teacher_id = %s""",
        (request_id, teacher['id']),
        fetch_one=True
    )
    
    if not en_request:
        flash("Request not found.", "error")
        return redirect(url_for('teacher.enrollment_requests'))
        
    action = request.form.get('action')
    
    if action == 'accept':
        try:
            # Check if already enrolled to avoid duplicates
            is_enrolled = execute_query(
                "SELECT id FROM classroom_learners WHERE classroom_id = %s AND learner_id = %s",
                (en_request['classroom_id'], en_request['learner_id']),
                fetch_one=True
            )
            if not is_enrolled:
                execute_query(
                    "INSERT INTO classroom_learners (classroom_id, learner_id) VALUES (%s, %s)",
                    (en_request['classroom_id'], en_request['learner_id']),
                    commit=True
                )
            
            execute_query("UPDATE enrollment_requests SET status = 'accepted' WHERE id = %s", (request_id,), commit=True)
            flash("Enrollment request accepted.", "success")
        except Exception as e:
            flash(f"Error accepting request: {e}", "error")
    elif action == 'reject':
        execute_query("UPDATE enrollment_requests SET status = 'rejected' WHERE id = %s", (request_id,), commit=True)
        flash("Enrollment request rejected.", "success")
        
    return redirect(url_for('teacher.enrollment_requests'))


@teacher_bp.route('/teacher/learners')
def learners():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    if not teacher:
        return redirect(url_for('main.landing'))
        
    # Fetch teacher's classrooms for the filter dropdown
    teacher_classrooms = execute_query("SELECT id, name FROM classrooms WHERE teacher_id = %s", (teacher['id'],), fetch_all=True) or []
    
    # Get all learners that belong to any of this teacher's classrooms
    learners_raw = execute_query(
        """SELECT l.*, p.parent_name, 
           c.name as classroom_name, c.id as classroom_id,
           (SELECT status FROM bmi_records b WHERE b.learner_id = l.id ORDER BY b.recorded_date DESC LIMIT 1) as bmi_status,
           (SELECT COUNT(*) FROM attendance a WHERE a.learner_id = l.id AND a.status = 'present') as present_count,
           (SELECT COUNT(*) FROM attendance a WHERE a.learner_id = l.id) as attendance_total
           FROM learners l
           JOIN parents p ON l.parent_id = p.id
           JOIN classroom_learners cl ON cl.learner_id = l.id
           JOIN classrooms c ON cl.classroom_id = c.id
           WHERE c.teacher_id = %s""",
        (teacher['id'],),
        fetch_all=True
    ) or []
    
    from datetime import date
    
    # Process age, attendance rate, and build parsed list
    learners_list = []
    for l in learners_raw:
        # Age
        age = None
        if l['birthdate']:
            bdate = l['birthdate']
            # If bdate is a string (depends on DB driver), parse it
            if isinstance(bdate, str):
                from datetime import datetime
                try:
                    bdate = datetime.strptime(bdate, "%Y-%m-%d").date()
                except ValueError:
                    pass
            if isinstance(bdate, date):
                today = date.today()
                age = today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
            
        # Attendance rate
        attendance_rate = 100.0
        if l['attendance_total'] and l['attendance_total'] > 0:
            attendance_rate = round((l['present_count'] / l['attendance_total']) * 100, 1)
            
        l_processed = dict(l)
        l_processed['age'] = age
        l_processed['attendance_rate'] = attendance_rate
        learners_list.append(l_processed)
        
    # Apply search and filters
    query = request.args.get('query', '').strip().lower()
    gender_filter = request.args.get('gender', '')
    age_filter = request.args.get('age', '')
    bmi_filter = request.args.get('bmi_status', '')
    attendance_filter = request.args.get('attendance', '')
    classroom_filter = request.args.get('classroom_id', '')
    
    filtered_learners = []
    for l in learners_list:
        # Search query
        if query:
            match_query = (
                query in l['full_name'].lower() or
                (l['learner_id'] and query in l['learner_id'].lower()) or
                query in l['parent_name'].lower()
            )
            if not match_query:
                continue
                
        # Classroom
        if classroom_filter and str(l['classroom_id']) != classroom_filter:
            continue
                
        # Gender
        if gender_filter and l['gender'] != gender_filter:
            continue
            
        # Age Group
        if age_filter:
            if age_filter == '3-4' and (l['age'] is None or l['age'] not in [3, 4]):
                continue
            elif age_filter == '4-5' and (l['age'] is None or l['age'] not in [4, 5]):
                continue
            elif age_filter == '5-6' and (l['age'] is None or l['age'] not in [5, 6]):
                continue
                
        # BMI
        if bmi_filter and l['bmi_status'] != bmi_filter:
            continue
            
        # Attendance Rate
        if attendance_filter:
            if attendance_filter == 'at-risk' and l['attendance_rate'] >= 85.0:
                continue
            elif attendance_filter == 'excellent' and l['attendance_rate'] < 95.0:
                continue
                
        filtered_learners.append(l)
        
    return render_template(
        'teacher/learners.html',
        active_page='learners',
        learners=filtered_learners,
        teacher_classrooms=teacher_classrooms,
        query=query,
        classroom_filter=classroom_filter,
        gender_filter=gender_filter,
        age_filter=age_filter,
        bmi_filter=bmi_filter,
        attendance_filter=attendance_filter
    )

@teacher_bp.route('/teacher/classrooms/<int:classroom_id>/attendance', methods=['GET', 'POST'])
def record_attendance(classroom_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    classroom = execute_query("SELECT * FROM classrooms WHERE id = %s AND teacher_id = %s", (classroom_id, teacher['id']), fetch_one=True)
    if not classroom:
        flash("Classroom not found.", "error")
        return redirect(url_for('teacher.classrooms'))
        
    from datetime import date
    selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    
    if request.method == 'POST':
        # Get selected date from form
        selected_date = request.form.get('date', selected_date)
        
        # Get enrolled learners
        enrolled_learners = execute_query(
            "SELECT learner_id FROM classroom_learners WHERE classroom_id = %s",
            (classroom_id,),
            fetch_all=True
        ) or []
        
        try:
            for el in enrolled_learners:
                l_id = el['learner_id']
                status = request.form.get(f'status_{l_id}', 'present')
                
                # Insert or update
                execute_query(
                    """INSERT INTO attendance (learner_id, classroom_id, date, status) 
                       VALUES (%s, %s, %s, %s)
                       ON DUPLICATE KEY UPDATE status = %s""",
                    (l_id, classroom_id, selected_date, status, status),
                    commit=True
                )
            flash("Attendance saved successfully!", "success")
            return redirect(url_for('teacher.classroom_view', classroom_id=classroom_id))
        except Exception as e:
            flash(f"Error saving attendance: {e}", "error")
            
    # GET request: load learners and their recorded status for the selected date
    enrolled_learners = execute_query(
        """SELECT l.*, 
           (SELECT status FROM attendance a WHERE a.learner_id = l.id AND a.classroom_id = %s AND a.date = %s) as attendance_status
           FROM learners l
           JOIN classroom_learners cl ON cl.learner_id = l.id
           WHERE cl.classroom_id = %s""",
        (classroom_id, selected_date, classroom_id),
        fetch_all=True
    ) or []
    
    return render_template(
        'teacher/attendance.html',
        active_page='classrooms',
        classroom=classroom,
        learners=enrolled_learners,
        selected_date=selected_date
    )

@teacher_bp.route('/teacher/learners/<int:learner_id>/health', methods=['GET', 'POST'])
def learner_health(learner_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    if not teacher:
        return redirect(url_for('main.landing'))
        
    learner = execute_query(
        """SELECT l.*, p.parent_name 
           FROM learners l 
           JOIN parents p ON l.parent_id = p.id 
           WHERE l.id = %s""",
        (learner_id,),
        fetch_one=True
    )
    if not learner:
        flash("Learner not found.", "error")
        return redirect(url_for('teacher.learners'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'bmi':
            height = float(request.form.get('height'))
            weight = float(request.form.get('weight'))
            recorded_date = request.form.get('recorded_date')
            
            # Height in meters
            height_m = height / 100.0
            bmi = round(weight / (height_m * height_m), 2)
            
            # Status classification
            if bmi < 18.5:
                status = 'Underweight'
            elif bmi < 25.0:
                status = 'Normal'
            elif bmi < 30.0:
                status = 'Overweight'
            else:
                status = 'Obese'
                
            try:
                execute_query(
                    """INSERT INTO bmi_records (learner_id, height, weight, bmi, status, recorded_date)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (learner_id, height, weight, bmi, status, recorded_date),
                    commit=True
                )
                flash("BMI record added successfully!", "success")
            except Exception as e:
                flash(f"Error saving BMI record: {e}", "error")
                

        return redirect(url_for('teacher.learner_health', learner_id=learner_id))
        
    # GET request: load logs
    bmi_records = execute_query(
        "SELECT * FROM bmi_records WHERE learner_id = %s ORDER BY recorded_date DESC",
        (learner_id,),
        fetch_all=True
    ) or []
    
    return render_template(
        'teacher/learner_health.html',
        active_page='learners',
        learner=learner,
        bmi_records=bmi_records
    )

@teacher_bp.route('/teacher/reports')
def reports():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    if not teacher:
        return redirect(url_for('main.landing'))
        
    # Get all teacher's classrooms
    classrooms_list = execute_query(
        "SELECT * FROM classrooms WHERE teacher_id = %s ORDER BY name ASC",
        (teacher['id'],),
        fetch_all=True
    ) or []
    
    classroom_id = request.args.get('classroom_id')
    report_type = request.args.get('report_type', 'summary')
    
    selected_classroom = None
    learners_data = []
    
    if classroom_id:
        selected_classroom = execute_query(
            "SELECT * FROM classrooms WHERE id = %s AND teacher_id = %s",
            (classroom_id, teacher['id']),
            fetch_one=True
        )
        
        if selected_classroom:
            # Fetch enrolled learners
            enrolled = execute_query(
                """SELECT l.*, p.parent_name, p.mobile 
                   FROM learners l
                   JOIN classroom_learners cl ON cl.learner_id = l.id
                   JOIN parents p ON l.parent_id = p.id
                   WHERE cl.classroom_id = %s
                   ORDER BY l.full_name ASC""",
                (classroom_id,),
                fetch_all=True
            ) or []
            
            # Prepare batch datasets based on report type
            att_map = {}
            bmi_map = {}
            imm_map = {}
            progress_map = {}
            
            if report_type in ['attendance', 'summary']:
                att_rows = execute_query(
                    """SELECT learner_id, 
                       COUNT(CASE WHEN status = 'present' THEN 1 END) as present_count,
                       COUNT(CASE WHEN status = 'absent' THEN 1 END) as absent_count,
                       COUNT(CASE WHEN status = 'tardy' THEN 1 END) as tardy_count,
                       COUNT(*) as total_count
                       FROM attendance WHERE classroom_id = %s GROUP BY learner_id""",
                    (classroom_id,),
                    fetch_all=True
                ) or []
                att_map = {row['learner_id']: row for row in att_rows}
                
            if report_type in ['bmi', 'summary']:
                bmi_rows = execute_query(
                    """SELECT b.* FROM bmi_records b
                       JOIN (
                           SELECT learner_id, MAX(recorded_date) as max_date 
                           FROM bmi_records GROUP BY learner_id
                       ) latest ON b.learner_id = latest.learner_id AND b.recorded_date = latest.max_date
                       WHERE b.learner_id IN (
                           SELECT learner_id FROM classroom_learners WHERE classroom_id = %s
                       )""",
                    (classroom_id,),
                    fetch_all=True
                ) or []
                bmi_map = {row['learner_id']: row for row in bmi_rows}
                

            if report_type == 'progress':
                progress_rows = execute_query(
                    """SELECT a.score, a.learner_id, cw.title, cw.subject_folder 
                       FROM assessments a 
                       JOIN classwork cw ON a.classwork_id = cw.id 
                       WHERE cw.classroom_id = %s
                       ORDER BY cw.created_at ASC""",
                    (classroom_id,),
                    fetch_all=True
                ) or []
                for row in progress_rows:
                    progress_map.setdefault(row['learner_id'], []).append(row)
            
            # Enrich data based on report type using batch dictionaries
            for l in enrolled:
                learner_row = dict(l)
                l_id = l['id']
                
                # Fetch age
                from datetime import date
                age = None
                if l['birthdate']:
                    bdate = l['birthdate']
                    if isinstance(bdate, str):
                        from datetime import datetime
                        try:
                            bdate = datetime.strptime(bdate, "%Y-%m-%d").date()
                        except ValueError:
                            pass
                    if isinstance(bdate, date):
                        today = date.today()
                        age = today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
                learner_row['age'] = age
                
                if report_type == 'attendance':
                    att_records = att_map.get(l_id, {'present_count': 0, 'absent_count': 0, 'tardy_count': 0, 'total_count': 0})
                    learner_row['present'] = att_records['present_count']
                    learner_row['absent'] = att_records['absent_count']
                    learner_row['tardy'] = att_records['tardy_count']
                    learner_row['total'] = att_records['total_count']
                    
                    rate = 100.0
                    if learner_row['total'] > 0:
                        rate = round((learner_row['present'] / learner_row['total']) * 100, 1)
                    learner_row['rate'] = rate
                    
                elif report_type == 'bmi':
                    learner_row['bmi'] = bmi_map.get(l_id)
                    

                elif report_type == 'progress':
                    progress_recs = progress_map.get(l_id, [])
                    learner_row['assessments'] = progress_recs
                    
                    total_score = 0
                    count = 0
                    for pr in progress_recs:
                        if pr['score'] is not None:
                            total_score += pr['score']
                            count += 1
                    learner_row['avg_score'] = round(total_score / count, 1) if count > 0 else None
                    
                elif report_type == 'summary':
                    att_records = att_map.get(l_id, {'present_count': 0, 'total_count': 0})
                    rate = 100.0
                    if att_records['total_count'] and att_records['total_count'] > 0:
                        rate = round((att_records['present_count'] / att_records['total_count']) * 100, 1)
                    learner_row['rate'] = rate
                    
                    bmi_rec = bmi_map.get(l_id)
                    learner_row['bmi_status'] = bmi_rec['status'] if bmi_rec else None
                    
                learners_data.append(learner_row)
                
    return render_template(
        'teacher/reports.html',
        active_page='reports',
        classrooms=classrooms_list,
        selected_classroom=selected_classroom,
        report_type=report_type,
        learners=learners_data
    )

@teacher_bp.route('/teacher/analytics')
def analytics():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    if not teacher:
        return redirect(url_for('main.landing'))
        
    # Get teacher's classrooms
    classrooms_list = execute_query(
        "SELECT * FROM classrooms WHERE teacher_id = %s",
        (teacher['id'],),
        fetch_all=True
    ) or []
    
    classroom_ids = [c['id'] for c in classrooms_list]
    
    # Defaults
    total_learners = 0
    at_risk_list = []
    bmi_distribution = {'Normal': 0, 'Underweight': 0, 'Overweight': 0, 'Obese': 0}
    classroom_attendance = []
    classroom_grades = []
    
    if classroom_ids:
        format_strings = ','.join(['%s'] * len(classroom_ids))
        
        # Get all learners enrolled in these classrooms
        learners_raw = execute_query(
            f"""SELECT l.*, p.parent_name, cl.classroom_id, c.name as classroom_name 
               FROM learners l
               JOIN parents p ON l.parent_id = p.id
               JOIN classroom_learners cl ON cl.learner_id = l.id
               JOIN classrooms c ON cl.classroom_id = c.id
               WHERE cl.classroom_id IN ({format_strings})""",
            tuple(classroom_ids),
            fetch_all=True
        ) or []
        
        total_learners = len(learners_raw)
        
        # 1. Batch classroom attendance averages
        c_att_rows = execute_query(
            f"""SELECT classroom_id, 
               COUNT(CASE WHEN status = 'present' THEN 1 END) as present_count, 
               COUNT(*) as total_count 
               FROM attendance WHERE classroom_id IN ({format_strings})
               GROUP BY classroom_id""",
            tuple(classroom_ids),
            fetch_all=True
        ) or []
        c_att_map = {row['classroom_id']: row for row in c_att_rows}

        # 2. Batch classroom academic averages
        c_grade_rows = execute_query(
            f"""SELECT cw.classroom_id, AVG(a.score) as avg_score 
               FROM assessments a 
               JOIN classwork cw ON a.classwork_id = cw.id 
               WHERE cw.classroom_id IN ({format_strings})
               GROUP BY cw.classroom_id""",
            tuple(classroom_ids),
            fetch_all=True
        ) or []
        c_grade_map = {row['classroom_id']: row for row in c_grade_rows}

        # Populate classroom levels
        for c in classrooms_list:
            c_id = c['id']
            # Attendance
            att_c = c_att_map.get(c_id, {'present_count': 0, 'total_count': 0})
            c_rate = 100.0
            if att_c['total_count'] > 0:
                c_rate = round((att_c['present_count'] / att_c['total_count']) * 100, 1)
            classroom_attendance.append({'name': c['name'], 'rate': c_rate})

            # Grades
            grade_c = c_grade_map.get(c_id)
            c_grade = round(float(grade_c['avg_score']), 1) if grade_c and grade_c['avg_score'] is not None else 0.0
            classroom_grades.append({'name': c['name'], 'avg': c_grade})

        # 3. Batch individual learner overall attendance totals
        att_all_rows = execute_query(
            f"""SELECT learner_id, 
               COUNT(CASE WHEN status = 'present' THEN 1 END) as present_count, 
               COUNT(*) as total_count 
               FROM attendance 
               WHERE classroom_id IN ({format_strings})
               GROUP BY learner_id""",
            tuple(classroom_ids),
            fetch_all=True
        ) or []
        att_all_map = {row['learner_id']: row for row in att_all_rows}

        # 4. Batch individual learner latest BMIs
        bmi_all_rows = execute_query(
            f"""SELECT b.* FROM bmi_records b
               JOIN (
                   SELECT learner_id, MAX(recorded_date) as max_date 
                   FROM bmi_records GROUP BY learner_id
               ) latest ON b.learner_id = latest.learner_id AND b.recorded_date = latest.max_date
               WHERE b.learner_id IN (
                   SELECT learner_id FROM classroom_learners WHERE classroom_id IN ({format_strings})
               )""",
            tuple(classroom_ids),
            fetch_all=True
        ) or []
        bmi_all_map = {row['learner_id']: row for row in bmi_all_rows}

        # 5. Batch individual learner overall assessments averages
        grade_all_rows = execute_query(
            """SELECT learner_id, AVG(score) as avg_score 
               FROM assessments GROUP BY learner_id""",
            (),
            fetch_all=True
        ) or []
        grade_all_map = {row['learner_id']: row for row in grade_all_rows}

        # Process individual learner growth status and check for At-Risk triggers using batch maps
        for l in learners_raw:
            l_id = l['id']
            risk_reasons = []
            
            # Check Attendance Risk
            att_records = att_all_map.get(l_id, {'present_count': 0, 'total_count': 0})
            l_rate = 100.0
            if att_records['total_count'] > 0:
                l_rate = round((att_records['present_count'] / att_records['total_count']) * 100, 1)
                if l_rate < 85.0:
                    risk_reasons.append(f"Low Attendance ({l_rate}%)")
                
            # Check BMI status
            bmi_rec = bmi_all_map.get(l_id)
            if bmi_rec:
                status = bmi_rec['status']
                if status in bmi_distribution:
                    bmi_distribution[status] += 1
                if status in ['Underweight', 'Obese']:
                    risk_reasons.append(f"Abnormal Nutrition ({status} BMI)")
                    
            # Check Academic Risk
            grade_rec = grade_all_map.get(l_id)
            l_avg = grade_rec['avg_score'] if grade_rec else None
            if l_avg is not None:
                l_avg = float(l_avg)
                if l_avg < 75.0:
                    risk_reasons.append(f"Academic Support Needed (Avg: {round(l_avg, 1)}%)")
                
            # If any risk flags were triggered, add learner to At-Risk alerts box
            if risk_reasons:
                at_risk_list.append({
                    'id': l['id'],
                    'full_name': l['full_name'],
                    'learner_id': l['learner_id'],
                    'classroom_name': l['classroom_name'],
                    'parent_name': l['parent_name'],
                    'risk_reasons': risk_reasons
                })
                
    return render_template(
        'teacher/analytics.html',
        active_page='analytics',
        total_learners=total_learners,
        at_risk_count=len(at_risk_list),
        at_risk_learners=at_risk_list,
        bmi_distribution=bmi_distribution,
        classroom_attendance=classroom_attendance,
        classroom_grades=classroom_grades
    )

@teacher_bp.route('/teacher/announcements')
def announcements():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    if not teacher:
        return redirect(url_for('main.landing'))
        
    category_filter = request.args.get('category', '')
    
    if category_filter:
        announcements_list = execute_query(
            "SELECT * FROM announcements WHERE teacher_id = %s AND category = %s ORDER BY created_at DESC",
            (teacher['id'], category_filter),
            fetch_all=True
        ) or []
    else:
        announcements_list = execute_query(
            "SELECT * FROM announcements WHERE teacher_id = %s ORDER BY created_at DESC",
            (teacher['id'],),
            fetch_all=True
        ) or []
    
    # Count announcements created this month
    from datetime import datetime
    now = datetime.now()
    this_month_count = 0
    for ann in announcements_list:
        if ann['created_at'] and ann['created_at'].month == now.month and ann['created_at'].year == now.year:
            this_month_count += 1
    
    return render_template(
        'teacher/announcements.html',
        active_page='announcements',
        announcements=announcements_list,
        category_filter=category_filter,
        this_month_count=this_month_count
    )

@teacher_bp.route('/teacher/announcements/create', methods=['POST'])
def create_announcement():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    if not teacher:
        return redirect(url_for('main.landing'))
        
    title = request.form.get('title')
    content = request.form.get('content')
    category = request.form.get('category', 'general')
    priority = request.form.get('priority', 'normal')
    
    if not title or not content:
        flash("Title and content are required.", "error")
        return redirect(url_for('teacher.announcements'))
        
    try:
        execute_query(
            """INSERT INTO announcements (teacher_id, title, content, category, priority)
               VALUES (%s, %s, %s, %s, %s)""",
            (teacher['id'], title, content, category, priority),
            commit=True
        )
        flash("Announcement published successfully!", "success")
    except Exception as e:
        flash(f"Error creating announcement: {e}", "error")
        
    return redirect(url_for('teacher.announcements'))

@teacher_bp.route('/teacher/announcements/<int:announcement_id>/edit', methods=['POST'])
def edit_announcement(announcement_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    if not teacher:
        return redirect(url_for('main.landing'))
        
    # Verify ownership
    ann = execute_query(
        "SELECT id FROM announcements WHERE id = %s AND teacher_id = %s",
        (announcement_id, teacher['id']),
        fetch_one=True
    )
    if not ann:
        flash("Announcement not found.", "error")
        return redirect(url_for('teacher.announcements'))
        
    title = request.form.get('title')
    content = request.form.get('content')
    category = request.form.get('category', 'general')
    priority = request.form.get('priority', 'normal')
    
    try:
        execute_query(
            """UPDATE announcements SET title = %s, content = %s, category = %s, priority = %s
               WHERE id = %s AND teacher_id = %s""",
            (title, content, category, priority, announcement_id, teacher['id']),
            commit=True
        )
        flash("Announcement updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating announcement: {e}", "error")
        
    return redirect(url_for('teacher.announcements'))

@teacher_bp.route('/teacher/announcements/<int:announcement_id>/delete', methods=['POST'])
def delete_announcement(announcement_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    if not teacher:
        return redirect(url_for('main.landing'))
        
    try:
        execute_query(
            "DELETE FROM announcements WHERE id = %s AND teacher_id = %s",
            (announcement_id, teacher['id']),
            commit=True
        )
        flash("Announcement deleted.", "success")
    except Exception as e:
        flash(f"Error deleting announcement: {e}", "error")
        
    return redirect(url_for('teacher.announcements'))

@teacher_bp.route('/teacher/classwork/<int:classwork_id>/submissions', methods=['GET', 'POST'])
def classwork_submissions(classwork_id):
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    if not teacher:
        return redirect(url_for('main.landing'))
        
    # Get classwork and classroom verification
    cw = execute_query(
        """SELECT cw.*, c.name as classroom_name 
           FROM classwork cw
           JOIN classrooms c ON cw.classroom_id = c.id
           WHERE cw.id = %s AND c.teacher_id = %s""",
        (classwork_id, teacher['id']),
        fetch_one=True
    )
    if not cw:
        flash("Classwork not found or access denied.", "error")
        return redirect(url_for('teacher.dashboard'))
        
    if request.method == 'POST':
        learner_id = request.form.get('learner_id')
        score = request.form.get('score')
        remarks = request.form.get('remarks', '')
        
        if learner_id and score:
            try:
                execute_query(
                    """INSERT INTO assessments (learner_id, classwork_id, score, remarks)
                       VALUES (%s, %s, %s, %s)
                       ON DUPLICATE KEY UPDATE score = %s, remarks = %s, graded_at = CURRENT_TIMESTAMP""",
                    (learner_id, classwork_id, score, remarks, score, remarks),
                    commit=True
                )
                
                # Notify the parent
                parent_info = execute_query(
                    "SELECT parent_id, user_id FROM parents p JOIN learners l ON p.id = l.parent_id WHERE l.id = %s",
                    (learner_id,),
                    fetch_one=True
                )
                if parent_info:
                    msg = f"A grade of {score}/100 was posted for {cw['title']}."
                    link = url_for('parent.classwork_submission', classwork_id=classwork_id)
                    execute_query(
                        """INSERT INTO notifications (user_id, title, message, link_url)
                           VALUES (%s, %s, %s, %s)""",
                        (parent_info['user_id'], 'Classwork Graded', msg, link),
                        commit=True
                    )
                
                flash('Grade saved successfully.', 'success')
            except Exception as e:
                flash(f'Error saving grade: {e}', 'error')
                
        return redirect(url_for('teacher.classwork_submissions', classwork_id=classwork_id))
        
    # GET: fetch all learners and their submissions & grades
    students = execute_query(
        """SELECT l.id as learner_id, l.full_name, l.learner_id as lrn,
           sub.submission_text, sub.file_path as sub_file, sub.submitted_at,
           a.score, a.remarks
           FROM learners l
           JOIN classroom_learners cl ON l.id = cl.learner_id
           LEFT JOIN classwork_submissions sub ON l.id = sub.learner_id AND sub.classwork_id = %s
           LEFT JOIN assessments a ON l.id = a.learner_id AND a.classwork_id = %s
           WHERE cl.classroom_id = %s
           ORDER BY l.full_name ASC""",
        (classwork_id, classwork_id, cw['classroom_id']),
        fetch_all=True
    ) or []
    
    return render_template(
        'teacher/classwork_submissions.html',
        active_page='classrooms',
        classwork=cw,
        students=students
    )

@teacher_bp.route('/teacher/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('auth.login'))
        
    teacher = get_teacher_profile(session['user_id'])
    if not teacher:
        return redirect(url_for('main.landing'))
    teacher_id = teacher['id']
        
    if request.method == 'POST':
        theme = request.form.get('theme')
        if theme in ['green', 'blue', 'purple', 'white', 'red', 'yellow', 'dark', 'rainbow']:
            execute_query("UPDATE teachers SET theme = %s WHERE id = %s", (theme, teacher_id), commit=True)
            session['theme'] = theme
            flash('Website theme updated successfully!', 'success')
            return redirect(url_for('teacher.settings'))
            
    current_theme = session.get('theme', 'green')
    return render_template(
        'teacher/settings.html',
        active_page='settings',
        current_theme=current_theme
    )
