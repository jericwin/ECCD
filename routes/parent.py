import os
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from werkzeug.utils import secure_filename
from db import execute_query

parent_bp = Blueprint('parent', __name__)

@parent_bp.context_processor
def inject_notifications():
    if 'user_id' in session and session.get('role') == 'parent':
        user_id = session['user_id']
        
        # 1. Dynamically check for upcoming due dates (1 day before)
        # Find classwork due tomorrow that the learner hasn't submitted yet
        parent = execute_query("SELECT id FROM parents WHERE user_id = %s", (user_id,), fetch_one=True)
        if parent:
            learners = execute_query("SELECT id FROM learners WHERE parent_id = %s", (parent['id'],), fetch_all=True) or []
            for l in learners:
                tomorrow_str = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                upcoming = execute_query(
                    """SELECT cw.id, cw.title FROM classwork cw
                       JOIN classroom_learners cl ON cw.classroom_id = cl.classroom_id
                       WHERE cl.learner_id = %s AND cw.due_date = %s
                       AND cw.id NOT IN (SELECT classwork_id FROM classwork_submissions WHERE learner_id = %s)""",
                    (l['id'], tomorrow_str, l['id']),
                    fetch_all=True
                ) or []
                
                for cw in upcoming:
                    # Check if we already inserted a notification for this
                    msg = f"Reminder: '{cw['title']}' is due tomorrow!"
                    existing = execute_query(
                        "SELECT id FROM notifications WHERE user_id = %s AND title = 'Upcoming Deadline' AND message = %s",
                        (user_id, msg),
                        fetch_one=True
                    )
                    if not existing:
                        link = url_for('parent.classwork_submission', classwork_id=cw['id'])
                        execute_query(
                            """INSERT INTO notifications (user_id, title, message, link_url)
                               VALUES (%s, %s, %s, %s)""",
                            (user_id, 'Upcoming Deadline', msg, link),
                            commit=True
                        )
        
        # Fetch all unread notifications
        notifications = execute_query(
            "SELECT * FROM notifications WHERE user_id = %s AND is_read = FALSE ORDER BY created_at DESC",
            (user_id,),
            fetch_all=True
        ) or []
        return dict(unread_notifications=notifications)
    return dict(unread_notifications=[])

@parent_bp.route('/notifications')
def notifications():
    if 'user_id' not in session or session.get('role') != 'parent':
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    
    all_notifications = execute_query(
        "SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,),
        fetch_all=True
    ) or []
    
    return render_template(
        'parent/notifications.html',
        active_page='notifications',
        notifications=all_notifications
    )

@parent_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
def read_notification(notification_id):
    if 'user_id' in session:
        execute_query("UPDATE notifications SET is_read = TRUE WHERE id = %s AND user_id = %s", (notification_id, session['user_id']), commit=True)
        link = request.form.get('link_url')
        if link:
            return redirect(link)
    return redirect(url_for('parent.notifications'))

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_parent_and_child(user_id):
    if 'profile' in session and session.get('role') == 'parent':
        p_data = session['profile']
        return p_data.get('parent'), p_data.get('learner')
    parent = execute_query("SELECT * FROM parents WHERE user_id = %s", (user_id,), fetch_one=True)
    if not parent:
        return None, None
    learner = execute_query("SELECT * FROM learners WHERE parent_id = %s", (parent['id'],), fetch_one=True)
    return parent, learner

@parent_bp.route('/parent/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'parent':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.login'))
        
    parent, learner = get_parent_and_child(session['user_id'])
    if not parent or not learner:
        flash('Child profile not found. Please contact administration.', 'error')
        return redirect(url_for('main.landing'))
        
    # Get classroom details if enrolled
    classroom = execute_query(
        """SELECT c.*, t.full_name as teacher_name FROM classrooms c
           JOIN classroom_learners cl ON cl.classroom_id = c.id
           JOIN teachers t ON c.teacher_id = t.id
           WHERE cl.learner_id = %s""",
        (learner['id'],),
        fetch_one=True
    )
    
    # Get stats
    res = execute_query(
        "SELECT COUNT(*) as count FROM classroom_learners WHERE learner_id = %s",
        (learner['id'],),
        fetch_one=True
    )
    enrolled_classes_count = res['count'] if res else 0
    
    bmi_record = execute_query(
        "SELECT * FROM bmi_records WHERE learner_id = %s ORDER BY recorded_date DESC LIMIT 1",
        (learner['id'],),
        fetch_one=True
    )
    
    return render_template(
        'parent/dashboard.html',
        active_page='dashboard',
        parent=parent,
        learner=learner,
        classroom=classroom,
        enrolled_classes_count=enrolled_classes_count,
        bmi_record=bmi_record
    )

@parent_bp.route('/parent/child')
def child_profile():
    if 'user_id' not in session or session.get('role') != 'parent':
        return redirect(url_for('auth.login'))
        
    parent, learner = get_parent_and_child(session['user_id'])
    if not parent or not learner:
        return redirect(url_for('main.landing'))
        
    # Classroom details
    classroom = execute_query(
        """SELECT c.*, t.full_name as teacher_name FROM classrooms c
           JOIN classroom_learners cl ON cl.classroom_id = c.id
           JOIN teachers t ON c.teacher_id = t.id
           WHERE cl.learner_id = %s""",
        (learner['id'],),
        fetch_one=True
    )
    
    # Developmental logs history
    bmi_records = execute_query(
        "SELECT * FROM bmi_records WHERE learner_id = %s ORDER BY recorded_date DESC",
        (learner['id'],),
        fetch_all=True
    ) or []
    
    attendance_records = execute_query(
        "SELECT * FROM attendance WHERE learner_id = %s ORDER BY date DESC LIMIT 15",
        (learner['id'],),
        fetch_all=True
    ) or []
    
    # Fetch assessment scores
    progress_records = execute_query(
        """SELECT a.*, cw.title, cw.subject_folder FROM assessments a
           JOIN classwork cw ON a.classwork_id = cw.id
           WHERE a.learner_id = %s
           ORDER BY a.graded_at DESC""",
        (learner['id'],),
        fetch_all=True
    ) or []
    
    return render_template(
        'parent/child_profile.html',
        active_page='child_profile',
        learner=learner,
        classroom=classroom,
        bmi_records=bmi_records,
        attendance_records=attendance_records,
        progress_records=progress_records
    )

@parent_bp.route('/parent/child/upload-photo', methods=['POST'])
def upload_child_photo():
    if 'user_id' not in session or session.get('role') != 'parent':
        return redirect(url_for('auth.login'))

    parent, learner = get_parent_and_child(session['user_id'])
    if not parent or not learner:
        flash('Child profile not found.', 'error')
        return redirect(url_for('parent.dashboard'))

    if 'learner_photo' not in request.files:
        flash('No photo selected.', 'error')
        return redirect(request.referrer or url_for('parent.dashboard'))

    file = request.files['learner_photo']
    if file.filename == '':
        flash('No photo selected.', 'error')
        return redirect(request.referrer or url_for('parent.dashboard'))

    if file and allowed_file(file.filename):
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'learners')
        os.makedirs(upload_dir, exist_ok=True)

        # Delete old photo file if it exists
        if learner['photo']:
            old_path = os.path.join(upload_dir, learner['photo'])
            if os.path.exists(old_path):
                os.remove(old_path)

        ext = file.filename.rsplit('.', 1)[1].lower()
        safe_id = secure_filename(str(learner['learner_id']))
        photo_filename = f"learner_{safe_id}.{ext}"
        file.save(os.path.join(upload_dir, photo_filename))

        execute_query(
            "UPDATE learners SET photo = %s WHERE id = %s",
            (photo_filename, learner['id']),
            commit=True
        )
        # Update the session cached profile photo so the update displays immediately without re-login
        if 'profile' in session and session.get('role') == 'parent':
            session['profile']['learner']['photo'] = photo_filename
            session.modified = True
            
        flash('Child photo updated successfully!', 'success')
    else:
        flash('Invalid file type. Please upload a JPG, PNG, or GIF image.', 'error')

    return redirect(request.referrer or url_for('parent.dashboard'))

@parent_bp.route('/parent/announcements')
def announcements():
    if 'user_id' not in session or session.get('role') != 'parent':
        return redirect(url_for('auth.login'))
        
    parent, learner = get_parent_and_child(session['user_id'])
    if not parent or not learner:
        return redirect(url_for('main.landing'))
        
    category_filter = request.args.get('category', '')
    
    # Check if learner is enrolled in any classroom
    enrollment = execute_query(
        """SELECT c.teacher_id FROM classrooms c
           JOIN classroom_learners cl ON cl.classroom_id = c.id
           WHERE cl.learner_id = %s LIMIT 1""",
        (learner['id'],),
        fetch_one=True
    )
    
    # If enrolled, show announcements from the learner's teachers and same-center teachers
    # If not enrolled, show all announcements (so parents are never left without info)
    if enrollment and category_filter:
        announcements_list = execute_query(
            """SELECT a.*, t.full_name as teacher_name, t.center_name
               FROM announcements a
               JOIN teachers t ON a.teacher_id = t.id
               WHERE (
                   a.teacher_id IN (
                       SELECT c.teacher_id FROM classrooms c
                       JOIN classroom_learners cl ON cl.classroom_id = c.id
                       WHERE cl.learner_id = %s
                   )
                   OR t.center_name = %s
               ) AND a.category = %s
               ORDER BY a.created_at DESC""",
            (learner['id'], learner['center_name'], category_filter),
            fetch_all=True
        ) or []
    elif enrollment:
        announcements_list = execute_query(
            """SELECT a.*, t.full_name as teacher_name, t.center_name
               FROM announcements a
               JOIN teachers t ON a.teacher_id = t.id
               WHERE a.teacher_id IN (
                   SELECT c.teacher_id FROM classrooms c
                   JOIN classroom_learners cl ON cl.classroom_id = c.id
                   WHERE cl.learner_id = %s
               )
               OR t.center_name = %s
               ORDER BY a.created_at DESC""",
            (learner['id'], learner['center_name']),
            fetch_all=True
        ) or []
    elif category_filter:
        # Not enrolled — show all announcements filtered by category
        announcements_list = execute_query(
            """SELECT a.*, t.full_name as teacher_name, t.center_name
               FROM announcements a
               JOIN teachers t ON a.teacher_id = t.id
               WHERE a.category = %s
               ORDER BY a.created_at DESC""",
            (category_filter,),
            fetch_all=True
        ) or []
    else:
        # Not enrolled — show all announcements
        announcements_list = execute_query(
            """SELECT a.*, t.full_name as teacher_name, t.center_name
               FROM announcements a
               JOIN teachers t ON a.teacher_id = t.id
               ORDER BY a.created_at DESC""",
            (),
            fetch_all=True
        ) or []
    
    # Count announcements this month
    from datetime import datetime
    now = datetime.now()
    this_month_count = 0
    for ann in announcements_list:
        if ann['created_at'] and ann['created_at'].month == now.month and ann['created_at'].year == now.year:
            this_month_count += 1
    
    return render_template(
        'parent/announcements.html',
        active_page='announcements',
        announcements=announcements_list,
        category_filter=category_filter,
        this_month_count=this_month_count
    )

@parent_bp.route('/parent/enroll', methods=['GET', 'POST'])
def enroll():
    if 'user_id' not in session or session.get('role') != 'parent':
        return redirect(url_for('auth.login'))
        
    parent, learner = get_parent_and_child(session['user_id'])
    if not parent or not learner:
        return redirect(url_for('main.landing'))

    if request.method == 'POST':
        classroom_id = request.form.get('classroom_id')
        if not classroom_id:
            flash('No classroom selected.', 'error')
            return redirect(url_for('parent.enroll'))
            
        # Check if already enrolled
        is_enrolled = execute_query(
            "SELECT * FROM classroom_learners WHERE classroom_id = %s AND learner_id = %s",
            (classroom_id, learner['id']),
            fetch_one=True
        )
        if is_enrolled:
            flash('Your child is already enrolled in this classroom.', 'error')
            return redirect(url_for('parent.enroll'))
            
        # Check if request already pending
        is_pending = execute_query(
            "SELECT * FROM enrollment_requests WHERE classroom_id = %s AND learner_id = %s AND status = 'pending'",
            (classroom_id, learner['id']),
            fetch_one=True
        )
        if is_pending:
            flash('You already have a pending enrollment request for this classroom.', 'info')
            return redirect(url_for('parent.enroll'))
            
        try:
            execute_query(
                "INSERT INTO enrollment_requests (classroom_id, learner_id, status) VALUES (%s, %s, 'pending')",
                (classroom_id, learner['id']),
                commit=True
            )
            flash('Enrollment request submitted! Waiting for teacher approval.', 'success')
        except Exception as e:
            flash(f"Error submitting enrollment request: {e}", "error")
            
        return redirect(url_for('parent.enroll'))
        
    # GET request: fetch active classrooms
    query = request.args.get('q', '').strip()
    if query:
        search_pattern = f"%{query}%"
        classrooms = execute_query(
            """SELECT c.*, t.full_name as teacher_name, t.center_name,
               (SELECT COUNT(*) FROM classroom_learners cl WHERE cl.classroom_id = c.id) as learners_count,
               (SELECT status FROM enrollment_requests er WHERE er.classroom_id = c.id AND er.learner_id = %s ORDER BY created_at DESC LIMIT 1) as request_status,
               (SELECT id FROM classroom_learners cl2 WHERE cl2.classroom_id = c.id AND cl2.learner_id = %s) as is_enrolled
               FROM classrooms c
               JOIN teachers t ON c.teacher_id = t.id
               WHERE c.status = 'active' AND (c.name LIKE %s OR t.full_name LIKE %s)
               ORDER BY c.created_at DESC""",
            (learner['id'], learner['id'], search_pattern, search_pattern),
            fetch_all=True
        ) or []
    else:
        classrooms = execute_query(
            """SELECT c.*, t.full_name as teacher_name, t.center_name,
               (SELECT COUNT(*) FROM classroom_learners cl WHERE cl.classroom_id = c.id) as learners_count,
               (SELECT status FROM enrollment_requests er WHERE er.classroom_id = c.id AND er.learner_id = %s ORDER BY created_at DESC LIMIT 1) as request_status,
               (SELECT id FROM classroom_learners cl2 WHERE cl2.classroom_id = c.id AND cl2.learner_id = %s) as is_enrolled
               FROM classrooms c
               JOIN teachers t ON c.teacher_id = t.id
               WHERE c.status = 'active'
               ORDER BY c.created_at DESC""",
            (learner['id'], learner['id']),
            fetch_all=True
        ) or []

    return render_template(
        'parent/enroll.html',
        active_page='enroll',
        classrooms=classrooms,
        query=query
    )

@parent_bp.route('/parent/classroom/<int:classroom_id>')
def classroom_view(classroom_id):
    if 'user_id' not in session or session.get('role') != 'parent':
        return redirect(url_for('auth.login'))
        
    parent, learner = get_parent_and_child(session['user_id'])
    if not parent or not learner:
        return redirect(url_for('main.landing'))
        
    # Check if enrolled
    is_enrolled = execute_query(
        "SELECT * FROM classroom_learners WHERE classroom_id = %s AND learner_id = %s",
        (classroom_id, learner['id']),
        fetch_one=True
    )
    if not is_enrolled:
        flash("You are not enrolled in this classroom.", "error")
        return redirect(url_for('parent.enroll'))
        
    # Classroom details
    classroom = execute_query(
        """SELECT c.*, t.full_name as teacher_name FROM classrooms c
           JOIN teachers t ON c.teacher_id = t.id
           WHERE c.id = %s""",
        (classroom_id,),
        fetch_one=True
    )
    if not classroom:
        return redirect(url_for('parent.enroll'))
        
    # Attendance
    attendance = execute_query(
        "SELECT * FROM attendance WHERE classroom_id = %s AND learner_id = %s ORDER BY date DESC",
        (classroom_id, learner['id']),
        fetch_all=True
    ) or []
    
    # Classwork and assessments
    classwork = execute_query(
        """SELECT cw.*, a.score, a.remarks, a.graded_at 
           FROM classwork cw
           LEFT JOIN assessments a ON cw.id = a.classwork_id AND a.learner_id = %s
           WHERE cw.classroom_id = %s
           ORDER BY cw.created_at DESC""",
        (learner['id'], classroom_id),
        fetch_all=True
    ) or []
    
    # Group classwork by subject_folder for nicer display if needed, but for now a simple list works.
    
    return render_template(
        'parent/classroom_view.html',
        active_page='enroll',
        classroom=classroom,
        attendance=attendance,
        classwork=classwork
    )

@parent_bp.route('/parent/classwork/<int:classwork_id>', methods=['GET', 'POST'])
def classwork_submission(classwork_id):
    if 'user_id' not in session or session.get('role') != 'parent':
        return redirect(url_for('auth.login'))
        
    parent, learner = get_parent_and_child(session['user_id'])
    if not parent or not learner:
        return redirect(url_for('main.landing'))
        
    # Get classwork and classroom
    cw = execute_query(
        """SELECT cw.*, c.name as classroom_name, c.teacher_id 
           FROM classwork cw
           JOIN classrooms c ON cw.classroom_id = c.id
           WHERE cw.id = %s""",
        (classwork_id,),
        fetch_one=True
    )
    if not cw:
        flash("Classwork not found.", "error")
        return redirect(url_for('parent.dashboard'))
        
    # Check enrollment
    is_enrolled = execute_query(
        "SELECT id FROM classroom_learners WHERE classroom_id = %s AND learner_id = %s",
        (cw['classroom_id'], learner['id']),
        fetch_one=True
    )
    if not is_enrolled:
        flash("You are not enrolled in this classroom.", "error")
        return redirect(url_for('parent.enroll'))
        
    # Get grade if any
    assessment = execute_query(
        "SELECT * FROM assessments WHERE classwork_id = %s AND learner_id = %s",
        (classwork_id, learner['id']),
        fetch_one=True
    )
    
    # Handle POST submission
    if request.method == 'POST':
        submission_text = request.form.get('submission_text', '')
        
        file_filename = None
        if 'submission_file' in request.files:
            file = request.files['submission_file']
            if file and file.filename != '' and allowed_file(file.filename):
                os.makedirs(os.path.join(current_app.config['UPLOAD_FOLDER'], 'submissions'), exist_ok=True)
                ext = file.filename.rsplit('.', 1)[1].lower()
                file_filename = f"sub_{classwork_id}_{learner['id']}_{secure_filename(file.filename)}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'submissions', file_filename))
        
        # If no new file but there was an old file, keep it (handled in query using COALESCE or just updating if file exists)
        try:
            if file_filename:
                execute_query(
                    """INSERT INTO classwork_submissions (classwork_id, learner_id, submission_text, file_path)
                       VALUES (%s, %s, %s, %s)
                       ON DUPLICATE KEY UPDATE submission_text = %s, file_path = %s""",
                    (classwork_id, learner['id'], submission_text, file_filename, submission_text, file_filename),
                    commit=True
                )
            else:
                execute_query(
                    """INSERT INTO classwork_submissions (classwork_id, learner_id, submission_text)
                       VALUES (%s, %s, %s)
                       ON DUPLICATE KEY UPDATE submission_text = %s""",
                    (classwork_id, learner['id'], submission_text, submission_text),
                    commit=True
                )
            flash("Your work has been submitted successfully!", "success")
        except Exception as e:
            flash(f"Error submitting work: {e}", "error")
            
        return redirect(url_for('parent.classwork_submission', classwork_id=classwork_id))
        
    # GET: fetch current submission
    submission = execute_query(
        "SELECT * FROM classwork_submissions WHERE classwork_id = %s AND learner_id = %s",
        (classwork_id, learner['id']),
        fetch_one=True
    )
    
    return render_template(
        'parent/classwork_submission.html',
        active_page='enroll',
        classwork=cw,
        submission=submission,
        assessment=assessment
    )

