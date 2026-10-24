from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash
from db import execute_query
from utils.audit import log_action

municipality_bp = Blueprint('municipality', __name__)

def get_municipality_id():
    admin = execute_query(
        "SELECT municipality_id FROM municipality_admins WHERE user_id = %s",
        (session['user_id'],), fetch_one=True
    )
    return admin['municipality_id'] if admin else None

def require_municipality():
    if 'user_id' not in session or session.get('role') != 'municipality':
        return False
    return True

# ─── Dashboard ────────────────────────────────────────────────────────────────

@municipality_bp.route('/municipality/dashboard')
def dashboard():
    if not require_municipality():
        return redirect(url_for('auth.login'))

    admin = execute_query(
        """SELECT m.*, ma.municipality_id
           FROM municipality_admins ma
           JOIN municipalities m ON ma.municipality_id = m.id
           WHERE ma.user_id = %s""",
        (session['user_id'],), fetch_one=True
    )
    if not admin:
        return redirect(url_for('main.landing'))

    m_id = admin['municipality_id']

    schools_count = execute_query(
        "SELECT COUNT(*) as c FROM schools WHERE municipality_id = %s", (m_id,), fetch_one=True
    )['c']
    approved_count = execute_query(
        "SELECT COUNT(*) as c FROM schools WHERE municipality_id = %s AND status='approved'", (m_id,), fetch_one=True
    )['c']
    pending_count = execute_query(
        "SELECT COUNT(*) as c FROM schools WHERE municipality_id = %s AND status='pending'", (m_id,), fetch_one=True
    )['c']
    rejected_count = execute_query(
        "SELECT COUNT(*) as c FROM schools WHERE municipality_id = %s AND status='rejected'", (m_id,), fetch_one=True
    )['c']

    # Total enrolled learners across all schools in municipality
    total_enrolled = execute_query(
        """SELECT COUNT(*) as c FROM enrollment_requests er
           JOIN schools s ON er.school_id = s.id
           WHERE s.municipality_id = %s AND er.status = 'approved'""",
        (m_id,), fetch_one=True
    )['c']

    # Recent schools for dashboard overview
    recent_schools = execute_query(
        "SELECT * FROM schools WHERE municipality_id = %s ORDER BY created_at DESC LIMIT 5", (m_id,), fetch_all=True
    ) or []

    # Unread notifications
    notifications = execute_query(
        "SELECT * FROM notifications WHERE user_id = %s AND is_read = 0 ORDER BY created_at DESC LIMIT 5",
        (session['user_id'],), fetch_all=True
    ) or []

    return render_template(
        'municipality/dashboard.html',
        admin=admin,
        schools_count=schools_count,
        approved_count=approved_count,
        pending_count=pending_count,
        rejected_count=rejected_count,
        total_enrolled=total_enrolled,
        recent_schools=recent_schools,
        notifications=notifications,
        active_page='dashboard'
    )

# ─── School Management ────────────────────────────────────────────────────────

@municipality_bp.route('/municipality/schools')
def schools():
    if not require_municipality():
        return redirect(url_for('auth.login'))

    m_id = get_municipality_id()
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '')

    base_query = """
        SELECT s.*,
               (SELECT COUNT(*) FROM enrollment_requests er WHERE er.school_id = s.id AND er.status = 'approved') as enrolled_count,
               (SELECT COUNT(*) FROM enrollment_requests er WHERE er.school_id = s.id AND er.status = 'pending') as pending_enrollments
        FROM schools s
        WHERE s.municipality_id = %s
    """
    params = [m_id]

    if status_filter != 'all':
        base_query += " AND s.status = %s"
        params.append(status_filter)

    if search:
        base_query += " AND s.name LIKE %s"
        params.append(f'%{search}%')

    base_query += " ORDER BY s.created_at DESC"

    schools_list = execute_query(base_query, tuple(params), fetch_all=True) or []

    # Get all admins for these schools
    admins = []
    if schools_list:
        s_ids = [str(s['id']) for s in schools_list]
        fmt = ','.join(['%s'] * len(s_ids))
        admins = execute_query(
            f"""SELECT u.id, u.username, u.email, sa.school_id
                FROM users u JOIN school_admins sa ON u.id = sa.user_id
                WHERE sa.school_id IN ({fmt})""",
            tuple(s_ids), fetch_all=True
        ) or []

    return render_template(
        'municipality/schools.html',
        schools=schools_list,
        admins=admins,
        status_filter=status_filter,
        search=search,
        active_page='schools'
    )

@municipality_bp.route('/municipality/schools/add', methods=['POST'])
def add_school():
    if not require_municipality():
        return redirect(url_for('auth.login'))

    m_id = get_municipality_id()
    name = request.form.get('name')
    address = request.form.get('address')
    street_address = request.form.get('street_address')
    city_municipality = request.form.get('city_municipality')
    province_name = request.form.get('province_name')
    postal_code = request.form.get('postal_code')
    latitude = request.form.get('latitude') or None
    longitude = request.form.get('longitude') or None
    capacity = request.form.get('capacity') or 100

    try:
        res = execute_query(
            """INSERT INTO schools (municipality_id, name, address, street_address, city_municipality,
               province_name, postal_code, latitude, longitude, capacity, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')""",
            (m_id, name, address, street_address, city_municipality,
             province_name, postal_code, latitude, longitude, capacity),
            commit=True
        )
        school_id = res['lastrowid']
        log_action(session['user_id'], 'REGISTERED_SCHOOL', 'school', school_id, None, name)

        # Notify provincial admins
        muni = execute_query("SELECT province_id, name FROM municipalities WHERE id = %s", (m_id,), fetch_one=True)
        if muni:
            provincial_admins = execute_query(
                "SELECT user_id FROM provincial_admins WHERE province_id = %s",
                (muni['province_id'],), fetch_all=True
            ) or []
            for pa in provincial_admins:
                execute_query(
                    "INSERT INTO notifications (user_id, title, message, link_url) VALUES (%s, %s, %s, %s)",
                    (pa['user_id'], 'New School Registered',
                     f"A new school '{name}' in {muni['name']} is pending validation.",
                     '/provincial/dashboard'),
                    commit=True
                )

        flash(f"School '{name}' registered successfully! Pending provincial validation.", 'success')
    except Exception as e:
        flash(f'Error registering school: {e}', 'error')

    return redirect(url_for('municipality.schools'))

@municipality_bp.route('/municipality/schools/<int:school_id>/edit', methods=['POST'])
def edit_school(school_id):
    if not require_municipality():
        return redirect(url_for('auth.login'))

    m_id = get_municipality_id()
    school = execute_query("SELECT * FROM schools WHERE id = %s AND municipality_id = %s", (school_id, m_id), fetch_one=True)
    if not school:
        flash('Unauthorized.', 'error')
        return redirect(url_for('municipality.schools'))

    name = request.form.get('name')
    address = request.form.get('address')
    street_address = request.form.get('street_address')
    city_municipality = request.form.get('city_municipality')
    province_name = request.form.get('province_name')
    postal_code = request.form.get('postal_code')
    latitude = request.form.get('latitude') or None
    longitude = request.form.get('longitude') or None
    capacity = request.form.get('capacity') or school['capacity']

    execute_query(
        """UPDATE schools SET name=%s, address=%s, street_address=%s, city_municipality=%s,
           province_name=%s, postal_code=%s, latitude=%s, longitude=%s, capacity=%s WHERE id=%s""",
        (name, address, street_address, city_municipality,
         province_name, postal_code, latitude, longitude, capacity, school_id),
        commit=True
    )
    log_action(session['user_id'], 'EDITED_SCHOOL', 'school', school_id, None, name)
    flash(f"School '{name}' updated successfully.", 'success')
    return redirect(url_for('municipality.schools'))

@municipality_bp.route('/municipality/schools/<int:school_id>/resubmit', methods=['POST'])
def resubmit_school(school_id):
    """Resubmit a rejected school for provincial re-validation."""
    if not require_municipality():
        return redirect(url_for('auth.login'))

    m_id = get_municipality_id()
    school = execute_query(
        "SELECT * FROM schools WHERE id = %s AND municipality_id = %s AND status = 'rejected'",
        (school_id, m_id), fetch_one=True
    )
    if not school:
        flash('This school cannot be resubmitted.', 'error')
        return redirect(url_for('municipality.schools'))

    execute_query("UPDATE schools SET status = 'pending' WHERE id = %s", (school_id,), commit=True)
    log_action(session['user_id'], 'RESUBMITTED_SCHOOL', 'school', school_id, None, school['name'])

    # Notify provincial admins
    muni = execute_query("SELECT province_id, name FROM municipalities WHERE id = %s", (m_id,), fetch_one=True)
    if muni:
        provincial_admins = execute_query(
            "SELECT user_id FROM provincial_admins WHERE province_id = %s",
            (muni['province_id'],), fetch_all=True
        ) or []
        for pa in provincial_admins:
            execute_query(
                "INSERT INTO notifications (user_id, title, message, link_url) VALUES (%s, %s, %s, %s)",
                (pa['user_id'], 'School Resubmitted for Validation',
                 f"School '{school['name']}' in {muni['name']} has been resubmitted for validation.",
                 '/provincial/dashboard'),
                commit=True
            )

    flash(f"School '{school['name']}' has been resubmitted for provincial validation.", 'success')
    return redirect(url_for('municipality.schools'))

@municipality_bp.route('/municipality/schools/<int:school_id>/delete', methods=['POST'])
def delete_school(school_id):
    if not require_municipality():
        return redirect(url_for('auth.login'))
    execute_query("DELETE FROM schools WHERE id = %s", (school_id,), commit=True)
    log_action(session['user_id'], 'DELETED_SCHOOL', 'school', school_id, None, None)
    flash("School deleted.", 'success')
    return redirect(url_for('municipality.schools'))

@municipality_bp.route('/municipality/schools/<int:school_id>/admin', methods=['POST'])
def create_school_admin(school_id):
    if not require_municipality():
        return redirect(url_for('auth.login'))

    m_id = get_municipality_id()
    school = execute_query("SELECT * FROM schools WHERE id = %s AND municipality_id = %s", (school_id, m_id), fetch_one=True)
    if not school:
        flash('Unauthorized.', 'error')
        return redirect(url_for('municipality.schools'))
    if school['status'] != 'approved':
        flash('Cannot create admin for unapproved school.', 'error')
        return redirect(url_for('municipality.schools'))

    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')

    try:
        user_res = execute_query(
            "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, 'school')",
            (username, generate_password_hash(password), email), commit=True
        )
        execute_query(
            "INSERT INTO school_admins (user_id, school_id) VALUES (%s, %s)",
            (user_res['lastrowid'], school_id), commit=True
        )
        flash("School Admin account created successfully.", 'success')
    except Exception as e:
        flash(f"Error: {e}", 'error')

    return redirect(url_for('municipality.schools'))

@municipality_bp.route('/municipality/admins/<int:user_id>/delete', methods=['POST'])
def delete_school_admin(user_id):
    if not require_municipality():
        return redirect(url_for('auth.login'))
    execute_query("DELETE FROM users WHERE id = %s", (user_id,), commit=True)
    log_action(session['user_id'], 'DELETED_SCHOOL_ADMIN', 'user', user_id, None, None)
    flash("School Admin removed.", 'success')
    return redirect(url_for('municipality.schools'))

# ─── Monitoring ───────────────────────────────────────────────────────────────

@municipality_bp.route('/municipality/monitoring')
def monitoring():
    if not require_municipality():
        return redirect(url_for('auth.login'))

    m_id = get_municipality_id()

    # All schools with enrollment stats
    schools_stats = execute_query(
        """SELECT s.*,
               (SELECT COUNT(*) FROM enrollment_requests er WHERE er.school_id = s.id AND er.status = 'approved') as enrolled_count,
               (SELECT COUNT(*) FROM enrollment_requests er WHERE er.school_id = s.id AND er.status = 'pending') as pending_enrollments,
               (SELECT COUNT(*) FROM enrollment_requests er WHERE er.school_id = s.id AND er.status = 'rejected') as rejected_enrollments
           FROM schools s
           WHERE s.municipality_id = %s
           ORDER BY s.name ASC""",
        (m_id,), fetch_all=True
    ) or []

    # Summary stats
    total_enrolled = sum(s['enrolled_count'] for s in schools_stats)
    total_pending = sum(s['pending_enrollments'] for s in schools_stats)
    total_capacity = sum((s['capacity'] or 0) for s in schools_stats)
    total_slots = sum(max(0, (s['capacity'] or 0) - s['enrolled_count']) for s in schools_stats)

    return render_template(
        'municipality/monitoring.html',
        schools_stats=schools_stats,
        total_enrolled=total_enrolled,
        total_pending=total_pending,
        total_capacity=total_capacity,
        total_slots=total_slots,
        active_page='monitoring'
    )

# ─── Notifications ────────────────────────────────────────────────────────────

@municipality_bp.route('/municipality/notifications')
def notifications():
    if not require_municipality():
        return redirect(url_for('auth.login'))

    notifs = execute_query(
        "SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC",
        (session['user_id'],), fetch_all=True
    ) or []

    # Mark all as read
    execute_query(
        "UPDATE notifications SET is_read = 1 WHERE user_id = %s AND is_read = 0",
        (session['user_id'],), commit=True
    )

    return render_template(
        'municipality/notifications.html',
        notifications=notifs,
        active_page='notifications'
    )
