from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from db import execute_query
from utils.audit import log_action

provincial_bp = Blueprint('provincial', __name__)

def require_provincial():
    return 'user_id' in session and session.get('role') == 'provincial'

def get_province_id():
    admin = execute_query(
        "SELECT province_id FROM provincial_admins WHERE user_id = %s",
        (session['user_id'],), fetch_one=True
    )
    return admin['province_id'] if admin else None

# ─── Dashboard ────────────────────────────────────────────────────────────────

@provincial_bp.route('/provincial/dashboard')
def dashboard():
    if not require_provincial():
        return redirect(url_for('auth.login'))

    admin = execute_query(
        """SELECT pa.*, p.name as province_name
           FROM provincial_admins pa
           JOIN provinces p ON pa.province_id = p.id
           WHERE pa.user_id = %s""",
        (session['user_id'],), fetch_one=True
    )
    if not admin:
        return redirect(url_for('main.landing'))

    province_id = admin['province_id']

    municipalities_count = execute_query(
        "SELECT COUNT(*) as c FROM municipalities WHERE province_id = %s", (province_id,), fetch_one=True
    )['c']

    total_schools = execute_query(
        """SELECT COUNT(*) as c FROM schools s
           JOIN municipalities m ON s.municipality_id = m.id
           WHERE m.province_id = %s""", (province_id,), fetch_one=True
    )['c']

    approved_schools = execute_query(
        """SELECT COUNT(*) as c FROM schools s
           JOIN municipalities m ON s.municipality_id = m.id
           WHERE m.province_id = %s AND s.status = 'approved'""", (province_id,), fetch_one=True
    )['c']

    pending_schools_count = execute_query(
        """SELECT COUNT(*) as c FROM schools s
           JOIN municipalities m ON s.municipality_id = m.id
           WHERE m.province_id = %s AND s.status = 'pending'""", (province_id,), fetch_one=True
    )['c']

    rejected_schools_count = execute_query(
        """SELECT COUNT(*) as c FROM schools s
           JOIN municipalities m ON s.municipality_id = m.id
           WHERE m.province_id = %s AND s.status = 'rejected'""", (province_id,), fetch_one=True
    )['c']

    # Recent pending schools (up to 5)
    pending_schools = execute_query(
        """SELECT s.*, m.name as municipality_name FROM schools s
           JOIN municipalities m ON s.municipality_id = m.id
           WHERE m.province_id = %s AND s.status = 'pending'
           ORDER BY s.created_at ASC LIMIT 5""",
        (province_id,), fetch_all=True
    ) or []

    # Recent audit activity
    recent_activities = execute_query(
        """SELECT al.*, u.username FROM audit_logs al
           JOIN users u ON al.user_id = u.id
           ORDER BY al.timestamp DESC LIMIT 8""",
        fetch_all=True
    ) or []

    # Unread notifications
    notifications = execute_query(
        "SELECT * FROM notifications WHERE user_id = %s AND is_read = 0 ORDER BY created_at DESC LIMIT 5",
        (session['user_id'],), fetch_all=True
    ) or []

    return render_template(
        'provincial/dashboard.html',
        admin=admin,
        municipalities_count=municipalities_count,
        total_schools=total_schools,
        approved_schools=approved_schools,
        pending_schools_count=pending_schools_count,
        rejected_schools_count=rejected_schools_count,
        pending_schools=pending_schools,
        recent_activities=recent_activities,
        notifications=notifications,
        active_page='dashboard'
    )

# ─── Municipality Management ──────────────────────────────────────────────────

@provincial_bp.route('/provincial/municipalities')
def manage_municipalities():
    if not require_provincial():
        return redirect(url_for('auth.login'))

    province_id = get_province_id()
    search = request.args.get('search', '')

    query = """SELECT m.*,
               (SELECT COUNT(*) FROM schools s WHERE s.municipality_id = m.id) as schools_count,
               (SELECT COUNT(*) FROM schools s WHERE s.municipality_id = m.id AND s.status='pending') as pending_schools
               FROM municipalities m WHERE m.province_id = %s"""
    params = [province_id]

    if search:
        query += " AND m.name LIKE %s"
        params.append(f'%{search}%')
    query += " ORDER BY m.name ASC"

    municipalities = execute_query(query, tuple(params), fetch_all=True) or []

    admins = []
    if municipalities:
        m_ids = [str(m['id']) for m in municipalities]
        fmt = ','.join(['%s'] * len(m_ids))
        admins = execute_query(
            f"""SELECT u.id, u.username, u.email, u.is_active, ma.municipality_id
                FROM users u JOIN municipality_admins ma ON u.id = ma.user_id
                WHERE ma.municipality_id IN ({fmt})""",
            tuple(m_ids), fetch_all=True
        ) or []

    return render_template(
        'provincial/municipalities.html',
        municipalities=municipalities,
        admins=admins,
        search=search,
        active_page='municipalities'
    )

@provincial_bp.route('/provincial/municipalities', methods=['POST'])
def add_municipality():
    if not require_provincial():
        return redirect(url_for('auth.login'))
    province_id = get_province_id()
    name = request.form.get('name')
    if name:
        execute_query(
            "INSERT INTO municipalities (province_id, name) VALUES (%s, %s)",
            (province_id, name), commit=True
        )
        log_action(session['user_id'], 'CREATED_MUNICIPALITY', 'municipality', None, None, name)
        flash(f"Municipality '{name}' created successfully.", 'success')
    return redirect(url_for('provincial.manage_municipalities'))

@provincial_bp.route('/provincial/municipalities/<int:m_id>/edit', methods=['POST'])
def edit_municipality(m_id):
    if not require_provincial():
        return redirect(url_for('auth.login'))
    name = request.form.get('name')
    if name:
        execute_query("UPDATE municipalities SET name = %s WHERE id = %s", (name, m_id), commit=True)
        log_action(session['user_id'], 'EDITED_MUNICIPALITY', 'municipality', m_id, None, name)
        flash(f"Municipality updated to '{name}'.", 'success')
    return redirect(url_for('provincial.manage_municipalities'))

@provincial_bp.route('/provincial/municipalities/<int:m_id>/delete', methods=['POST'])
def delete_municipality(m_id):
    if not require_provincial():
        return redirect(url_for('auth.login'))
    execute_query("DELETE FROM municipalities WHERE id = %s", (m_id,), commit=True)
    log_action(session['user_id'], 'DELETED_MUNICIPALITY', 'municipality', m_id, None, None)
    flash("Municipality deleted.", 'success')
    return redirect(url_for('provincial.manage_municipalities'))

@provincial_bp.route('/provincial/municipalities/<int:m_id>/admin', methods=['POST'])
def create_municipality_admin(m_id):
    if not require_provincial():
        return redirect(url_for('auth.login'))
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    try:
        user_res = execute_query(
            "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, 'municipality')",
            (username, generate_password_hash(password), email), commit=True
        )
        execute_query(
            "INSERT INTO municipality_admins (user_id, municipality_id) VALUES (%s, %s)",
            (user_res['lastrowid'], m_id), commit=True
        )
        log_action(session['user_id'], 'CREATED_MUNICIPALITY_ADMIN', 'user', user_res['lastrowid'], None, username)
        flash("Municipality Admin account created.", 'success')
    except Exception as e:
        flash(f"Error: {e}", 'error')
    return redirect(url_for('provincial.manage_municipalities'))

@provincial_bp.route('/provincial/admins/<int:user_id>/toggle', methods=['POST'])
def toggle_admin_status(user_id):
    if not require_provincial():
        return redirect(url_for('auth.login'))
    user = execute_query("SELECT is_active, username FROM users WHERE id = %s", (user_id,), fetch_one=True)
    if user:
        new_status = 0 if user['is_active'] else 1
        execute_query("UPDATE users SET is_active = %s WHERE id = %s", (new_status, user_id), commit=True)
        action = 'ACTIVATED' if new_status else 'DEACTIVATED'
        log_action(session['user_id'], f'{action}_MUNICIPALITY_ADMIN', 'user', user_id, None, user['username'])
        flash(f"Account {'activated' if new_status else 'deactivated'} successfully.", 'success')
    return redirect(url_for('provincial.manage_municipalities'))

@provincial_bp.route('/provincial/admins/<int:user_id>/delete', methods=['POST'])
def delete_municipality_admin(user_id):
    if not require_provincial():
        return redirect(url_for('auth.login'))
    execute_query("DELETE FROM users WHERE id = %s", (user_id,), commit=True)
    log_action(session['user_id'], 'DELETED_MUNICIPALITY_ADMIN', 'user', user_id, None, None)
    flash("Municipality Admin removed.", 'success')
    return redirect(url_for('provincial.manage_municipalities'))

# ─── School Validation ────────────────────────────────────────────────────────

@provincial_bp.route('/provincial/schools/validation')
def school_validation():
    if not require_provincial():
        return redirect(url_for('auth.login'))

    province_id = get_province_id()
    status_filter = request.args.get('status', 'pending')
    search = request.args.get('search', '')

    query = """SELECT s.*, m.name as municipality_name FROM schools s
               JOIN municipalities m ON s.municipality_id = m.id
               WHERE m.province_id = %s"""
    params = [province_id]

    if status_filter != 'all':
        query += " AND s.status = %s"
        params.append(status_filter)

    if search:
        query += " AND (s.name LIKE %s OR m.name LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])

    query += " ORDER BY s.created_at ASC"
    schools = execute_query(query, tuple(params), fetch_all=True) or []

    return render_template(
        'provincial/school_validation.html',
        schools=schools,
        status_filter=status_filter,
        search=search,
        active_page='school_validation'
    )

@provincial_bp.route('/provincial/schools/<int:school_id>/approve', methods=['POST'])
def approve_school(school_id):
    if not require_provincial():
        return redirect(url_for('auth.login'))

    execute_query("UPDATE schools SET status = 'approved', rejection_reason = NULL WHERE id = %s", (school_id,), commit=True)
    log_action(session['user_id'], 'APPROVED_SCHOOL', 'school', school_id, 'pending', 'approved')

    school = execute_query("SELECT municipality_id, name FROM schools WHERE id = %s", (school_id,), fetch_one=True)
    if school:
        m_admins = execute_query(
            "SELECT user_id FROM municipality_admins WHERE municipality_id = %s",
            (school['municipality_id'],), fetch_all=True
        ) or []
        for ma in m_admins:
            execute_query(
                "INSERT INTO notifications (user_id, title, message, link_url) VALUES (%s, %s, %s, %s)",
                (ma['user_id'], 'School Approved ✅',
                 f"The school '{school['name']}' has been approved by the Provincial Office.",
                 '/municipality/schools'),
                commit=True
            )

    flash('School approved successfully.', 'success')
    return redirect(url_for('provincial.school_validation'))

@provincial_bp.route('/provincial/schools/<int:school_id>/reject', methods=['POST'])
def reject_school(school_id):
    if not require_provincial():
        return redirect(url_for('auth.login'))

    reason = request.form.get('rejection_reason', '')
    execute_query(
        "UPDATE schools SET status = 'rejected', rejection_reason = %s WHERE id = %s",
        (reason, school_id), commit=True
    )
    log_action(session['user_id'], 'REJECTED_SCHOOL', 'school', school_id, 'pending', 'rejected')

    school = execute_query("SELECT municipality_id, name FROM schools WHERE id = %s", (school_id,), fetch_one=True)
    if school:
        m_admins = execute_query(
            "SELECT user_id FROM municipality_admins WHERE municipality_id = %s",
            (school['municipality_id'],), fetch_all=True
        ) or []
        for ma in m_admins:
            execute_query(
                "INSERT INTO notifications (user_id, title, message, link_url) VALUES (%s, %s, %s, %s)",
                (ma['user_id'], 'School Registration Rejected ❌',
                 f"The registration for '{school['name']}' was rejected. Reason: {reason or 'No reason provided.'}",
                 '/municipality/schools'),
                commit=True
            )

    flash('School registration rejected.', 'info')
    return redirect(url_for('provincial.school_validation'))

# ─── Monitoring ───────────────────────────────────────────────────────────────

@provincial_bp.route('/provincial/monitoring')
def monitoring():
    if not require_provincial():
        return redirect(url_for('auth.login'))

    province_id = get_province_id()

    municipalities = execute_query(
        "SELECT * FROM municipalities WHERE province_id = %s ORDER BY name ASC",
        (province_id,), fetch_all=True
    ) or []

    muni_stats = []
    for m in municipalities:
        m_id = m['id']
        total = execute_query("SELECT COUNT(*) as c FROM schools WHERE municipality_id = %s", (m_id,), fetch_one=True)['c']
        approved = execute_query("SELECT COUNT(*) as c FROM schools WHERE municipality_id = %s AND status='approved'", (m_id,), fetch_one=True)['c']
        pending = execute_query("SELECT COUNT(*) as c FROM schools WHERE municipality_id = %s AND status='pending'", (m_id,), fetch_one=True)['c']
        rejected = execute_query("SELECT COUNT(*) as c FROM schools WHERE municipality_id = %s AND status='rejected'", (m_id,), fetch_one=True)['c']
        enrolled = execute_query(
            """SELECT COUNT(*) as c FROM enrollment_requests er
               JOIN schools s ON er.school_id = s.id
               WHERE s.municipality_id = %s AND er.status = 'approved'""",
            (m_id,), fetch_one=True
        )['c']
        muni_stats.append({
            'name': m['name'],
            'id': m_id,
            'total_schools': total,
            'approved': approved,
            'pending': pending,
            'rejected': rejected,
            'enrolled': enrolled,
        })

    all_schools = execute_query(
        """SELECT s.*, m.name as municipality_name,
               (SELECT COUNT(*) FROM enrollment_requests er WHERE er.school_id = s.id AND er.status='approved') as enrolled_count,
               (SELECT COUNT(*) FROM enrollment_requests er WHERE er.school_id = s.id AND er.status='pending') as pending_enrollments
           FROM schools s JOIN municipalities m ON s.municipality_id = m.id
           WHERE m.province_id = %s ORDER BY m.name, s.name""",
        (province_id,), fetch_all=True
    ) or []

    total_enrolled = sum(s['enrolled_count'] for s in all_schools)
    total_capacity = sum((s['capacity'] or 0) for s in all_schools)

    return render_template(
        'provincial/monitoring.html',
        muni_stats=muni_stats,
        all_schools=all_schools,
        total_enrolled=total_enrolled,
        total_capacity=total_capacity,
        active_page='monitoring'
    )

# ─── Notifications ────────────────────────────────────────────────────────────

@provincial_bp.route('/provincial/notifications')
def notifications():
    if not require_provincial():
        return redirect(url_for('auth.login'))

    notifs = execute_query(
        "SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC",
        (session['user_id'],), fetch_all=True
    ) or []

    execute_query(
        "UPDATE notifications SET is_read = 1 WHERE user_id = %s AND is_read = 0",
        (session['user_id'],), commit=True
    )

    return render_template(
        'provincial/notifications.html',
        notifications=notifs,
        active_page='notifications'
    )
