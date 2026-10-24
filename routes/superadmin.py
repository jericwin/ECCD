from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from db import execute_query
from utils.audit import log_action

superadmin_bp = Blueprint('superadmin', __name__)

def require_superadmin():
    return 'user_id' in session and session.get('role') == 'superadmin'

# ─── Dashboard ────────────────────────────────────────────────────────────────

@superadmin_bp.route('/superadmin/dashboard')
def dashboard():
    if not require_superadmin():
        return redirect(url_for('auth.login'))

    total_users      = execute_query("SELECT COUNT(*) as c FROM users", fetch_one=True)['c']
    total_parents    = execute_query("SELECT COUNT(*) as c FROM users WHERE role='parent'", fetch_one=True)['c']
    total_teachers   = execute_query("SELECT COUNT(*) as c FROM users WHERE role='teacher'", fetch_one=True)['c']
    total_schools    = execute_query("SELECT COUNT(*) as c FROM schools", fetch_one=True)['c']
    total_munis      = execute_query("SELECT COUNT(*) as c FROM municipalities", fetch_one=True)['c']
    total_provincial = execute_query("SELECT COUNT(*) as c FROM users WHERE role='provincial'", fetch_one=True)['c']
    active_users     = execute_query("SELECT COUNT(*) as c FROM users WHERE is_active=1", fetch_one=True)['c']
    inactive_users   = execute_query("SELECT COUNT(*) as c FROM users WHERE is_active=0", fetch_one=True)['c']
    pending_schools  = execute_query("SELECT COUNT(*) as c FROM schools WHERE status='pending'", fetch_one=True)['c']
    pending_enroll   = execute_query("SELECT COUNT(*) as c FROM enrollment_requests WHERE status='pending'", fetch_one=True)['c']

    recent_activities = execute_query(
        """SELECT al.*, u.username, u.role FROM audit_logs al
           JOIN users u ON al.user_id = u.id
           ORDER BY al.timestamp DESC LIMIT 10""",
        fetch_all=True
    ) or []

    notifications = execute_query(
        "SELECT * FROM notifications WHERE user_id=%s AND is_read=0 ORDER BY created_at DESC LIMIT 5",
        (session['user_id'],), fetch_all=True
    ) or []

    return render_template('superadmin/dashboard.html',
        total_users=total_users, total_parents=total_parents,
        total_teachers=total_teachers, total_schools=total_schools,
        total_munis=total_munis, total_provincial=total_provincial,
        active_users=active_users, inactive_users=inactive_users,
        pending_schools=pending_schools, pending_enroll=pending_enroll,
        recent_activities=recent_activities, notifications=notifications,
        active_page='dashboard'
    )

# ─── Account Management ───────────────────────────────────────────────────────

@superadmin_bp.route('/superadmin/accounts')
def accounts():
    if not require_superadmin():
        return redirect(url_for('auth.login'))

    role_filter   = request.args.get('role', 'all')
    status_filter = request.args.get('status', 'all')
    search        = request.args.get('search', '')

    query = """
        SELECT u.id, u.username, u.email, u.role, u.is_active, u.created_at,
               p.name  AS province_name,
               m.name  AS municipality_name,
               s.name  AS school_name
        FROM users u
        LEFT JOIN provincial_admins   pa ON u.id = pa.user_id
        LEFT JOIN provinces            p ON pa.province_id = p.id
        LEFT JOIN municipality_admins  ma ON u.id = ma.user_id
        LEFT JOIN municipalities       m ON ma.municipality_id = m.id
        LEFT JOIN school_admins        sa ON u.id = sa.user_id
        LEFT JOIN schools              s ON sa.school_id = s.id
        WHERE 1=1
    """
    params = []

    if role_filter != 'all':
        query += " AND u.role = %s"; params.append(role_filter)
    if status_filter == 'active':
        query += " AND u.is_active = 1"
    elif status_filter == 'inactive':
        query += " AND u.is_active = 0"
    if search:
        query += " AND (u.username LIKE %s OR u.email LIKE %s)"
        params += [f'%{search}%', f'%{search}%']

    query += " ORDER BY u.created_at DESC"
    users = execute_query(query, tuple(params), fetch_all=True) or []

    provinces     = execute_query("SELECT * FROM provinces ORDER BY name", fetch_all=True) or []
    municipalities = execute_query(
        "SELECT m.*, p.name AS province_name FROM municipalities m JOIN provinces p ON m.province_id=p.id ORDER BY p.name, m.name",
        fetch_all=True
    ) or []

    return render_template('superadmin/accounts.html',
        users=users, provinces=provinces, municipalities=municipalities,
        role_filter=role_filter, status_filter=status_filter, search=search,
        active_page='accounts'
    )

@superadmin_bp.route('/superadmin/accounts/<int:user_id>/toggle', methods=['POST'])
def toggle_user(user_id):
    if not require_superadmin():
        return redirect(url_for('auth.login'))
    u = execute_query("SELECT is_active, username FROM users WHERE id=%s", (user_id,), fetch_one=True)
    if u:
        ns = 0 if u['is_active'] else 1
        execute_query("UPDATE users SET is_active=%s WHERE id=%s", (ns, user_id), commit=True)
        log_action(session['user_id'], 'ACTIVATED_USER' if ns else 'DEACTIVATED_USER', 'user', user_id, None, u['username'])
        flash(f"Account {'activated' if ns else 'deactivated'}.", 'success')
    return redirect(request.referrer or url_for('superadmin.accounts'))

@superadmin_bp.route('/superadmin/accounts/<int:user_id>/edit', methods=['POST'])
def edit_user(user_id):
    if not require_superadmin():
        return redirect(url_for('auth.login'))
    username = request.form.get('username')
    email    = request.form.get('email')
    password = request.form.get('password')
    try:
        if password:
            execute_query("UPDATE users SET username=%s, email=%s, password=%s WHERE id=%s",
                          (username, email, generate_password_hash(password), user_id), commit=True)
        else:
            execute_query("UPDATE users SET username=%s, email=%s WHERE id=%s",
                          (username, email, user_id), commit=True)
        log_action(session['user_id'], 'EDITED_USER', 'user', user_id, None, username)
        flash("Account updated.", 'success')
    except Exception as e:
        flash(f"Error: {e}", 'error')
    return redirect(request.referrer or url_for('superadmin.accounts'))

@superadmin_bp.route('/superadmin/accounts/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    if not require_superadmin():
        return redirect(url_for('auth.login'))
    u = execute_query("SELECT username, role FROM users WHERE id=%s", (user_id,), fetch_one=True)
    if u:
        execute_query("DELETE FROM users WHERE id=%s", (user_id,), commit=True)
        log_action(session['user_id'], 'DELETED_USER', 'user', user_id, u['role'], None)
        flash(f"User '{u['username']}' deleted.", 'success')
    return redirect(request.referrer or url_for('superadmin.accounts'))

@superadmin_bp.route('/superadmin/admins/create', methods=['POST'])
def create_admin():
    if not require_superadmin():
        return redirect(url_for('auth.login'))

    admin_type = request.form.get('admin_type')
    username   = request.form.get('username')
    email      = request.form.get('email')
    password   = request.form.get('password')

    if not all([username, email, password, admin_type]):
        flash("All fields are required.", 'error')
        return redirect(url_for('superadmin.accounts'))

    try:
        if admin_type == 'provincial':
            province_names = request.form.getlist('province_names[]')
            if not province_names:
                flash("At least one province is required.", 'error')
                return redirect(url_for('superadmin.accounts'))

            # Create the user account
            r = execute_query(
                "INSERT INTO users (username,password,email,role) VALUES(%s,%s,%s,'provincial')",
                (username, generate_password_hash(password), email), commit=True
            )
            user_id = r['lastrowid']

            # Assign each province (auto-create if not exists)
            for pname in province_names:
                pname = pname.strip()
                if not pname:
                    continue
                existing = execute_query(
                    "SELECT id FROM provinces WHERE LOWER(name)=LOWER(%s)",
                    (pname,), fetch_one=True
                )
                if existing:
                    prov_id = existing['id']
                else:
                    res = execute_query(
                        "INSERT INTO provinces (name) VALUES (%s)", (pname,), commit=True
                    )
                    prov_id = res['lastrowid']
                execute_query(
                    "INSERT INTO provincial_admins (user_id, province_id) VALUES (%s, %s)",
                    (user_id, prov_id), commit=True
                )

            log_action(session['user_id'], 'CREATED_PROVINCIAL_ADMIN', 'user', user_id, None, username)
            flash(f"Provincial Admin '{username}' created for {len(province_names)} province(s).", 'success')

        elif admin_type == 'municipality':
            municipality_ids = request.form.getlist('municipality_ids[]')
            if not municipality_ids:
                flash("At least one municipality is required.", 'error')
                return redirect(url_for('superadmin.accounts'))

            # Create the user account
            r = execute_query(
                "INSERT INTO users (username,password,email,role) VALUES(%s,%s,%s,'municipality')",
                (username, generate_password_hash(password), email), commit=True
            )
            user_id = r['lastrowid']

            # Assign each municipality
            for muni_id in municipality_ids:
                execute_query(
                    "INSERT INTO municipality_admins (user_id, municipality_id) VALUES (%s, %s)",
                    (user_id, muni_id), commit=True
                )

            log_action(session['user_id'], 'CREATED_MUNICIPALITY_ADMIN', 'user', user_id, None, username)
            flash(f"Municipality Admin '{username}' created for {len(municipality_ids)} municipality/ies.", 'success')

    except Exception as e:
        flash(f"Error: {e}", 'error')

    return redirect(url_for('superadmin.accounts'))

    if not require_superadmin():
        return redirect(url_for('auth.login'))

# ─── System Management ────────────────────────────────────────────────────────


@superadmin_bp.route('/superadmin/system')
def system():
    if not require_superadmin():
        return redirect(url_for('auth.login'))

    # All schools with stats
    all_schools = execute_query(
        """SELECT s.*, m.name AS municipality_name, p.name AS province_name,
               (SELECT COUNT(*) FROM enrollment_requests er WHERE er.school_id=s.id AND er.status='approved') AS enrolled,
               (SELECT COUNT(*) FROM enrollment_requests er WHERE er.school_id=s.id AND er.status='pending')  AS pending_enroll
           FROM schools s
           JOIN municipalities m ON s.municipality_id=m.id
           JOIN provinces p ON m.province_id=p.id
           ORDER BY p.name, m.name, s.name""",
        fetch_all=True
    ) or []

    # All municipalities
    all_munis = execute_query(
        """SELECT m.*, p.name AS province_name,
               (SELECT COUNT(*) FROM schools s WHERE s.municipality_id=m.id) AS schools_count
           FROM municipalities m JOIN provinces p ON m.province_id=p.id
           ORDER BY p.name, m.name""",
        fetch_all=True
    ) or []

    # All provinces
    all_provinces = execute_query(
        """SELECT p.*,
               (SELECT COUNT(*) FROM municipalities m WHERE m.province_id=p.id) AS muni_count,
               (SELECT COUNT(*) FROM schools s JOIN municipalities m ON s.municipality_id=m.id WHERE m.province_id=p.id) AS school_count
           FROM provinces p ORDER BY p.name""",
        fetch_all=True
    ) or []

    # Enrollment activity summary
    enroll_stats = {
        'total':    execute_query("SELECT COUNT(*) as c FROM enrollment_requests", fetch_one=True)['c'],
        'approved': execute_query("SELECT COUNT(*) as c FROM enrollment_requests WHERE status='approved'", fetch_one=True)['c'],
        'pending':  execute_query("SELECT COUNT(*) as c FROM enrollment_requests WHERE status='pending'", fetch_one=True)['c'],
        'rejected': execute_query("SELECT COUNT(*) as c FROM enrollment_requests WHERE status='rejected'", fetch_one=True)['c'],
    }

    return render_template('superadmin/system.html',
        all_schools=all_schools,
        all_munis=all_munis,
        all_provinces=all_provinces,
        enroll_stats=enroll_stats,
        active_page='system'
    )

@superadmin_bp.route('/superadmin/provinces/create', methods=['POST'])
def create_province():
    if not require_superadmin():
        return redirect(url_for('auth.login'))
    name = request.form.get('name')
    if name:
        try:
            execute_query("INSERT INTO provinces (name) VALUES (%s)", (name,), commit=True)
            log_action(session['user_id'], 'CREATED_PROVINCE', 'province', None, None, name)
            flash(f"Province '{name}' created.", 'success')
        except Exception as e:
            flash(f"Error: {e}", 'error')
    return redirect(url_for('superadmin.system'))

@superadmin_bp.route('/superadmin/municipalities/create', methods=['POST'])
def create_municipality():
    if not require_superadmin():
        return redirect(url_for('auth.login'))
    province_id = request.form.get('province_id')
    name        = request.form.get('name', '').strip()
    if not province_id or not name:
        flash("Province and municipality name are required.", 'error')
        return redirect(url_for('superadmin.system'))
    try:
        execute_query(
            "INSERT INTO municipalities (province_id, name) VALUES (%s, %s)",
            (province_id, name), commit=True
        )
        log_action(session['user_id'], 'CREATED_MUNICIPALITY', 'municipality', None, None, name)
        flash(f"Municipality '{name}' created.", 'success')
    except Exception as e:
        flash(f"Error: {e}", 'error')
    return redirect(url_for('superadmin.system'))


# ─── Audit Logs ───────────────────────────────────────────────────────────────

@superadmin_bp.route('/superadmin/audit')
def audit():
    if not require_superadmin():
        return redirect(url_for('auth.login'))

    action_filter = request.args.get('action', '')
    role_filter   = request.args.get('role', '')
    search        = request.args.get('search', '')

    query = """SELECT al.*, u.username, u.role FROM audit_logs al
               JOIN users u ON al.user_id=u.id WHERE 1=1"""
    params = []
    if action_filter:
        query += " AND al.action LIKE %s"; params.append(f'%{action_filter}%')
    if role_filter:
        query += " AND u.role=%s"; params.append(role_filter)
    if search:
        query += " AND (u.username LIKE %s OR al.action LIKE %s)"
        params += [f'%{search}%', f'%{search}%']
    query += " ORDER BY al.timestamp DESC LIMIT 200"

    logs = execute_query(query, tuple(params), fetch_all=True) or []

    return render_template('superadmin/audit.html',
        logs=logs, action_filter=action_filter,
        role_filter=role_filter, search=search,
        active_page='audit'
    )

# ─── Notifications ────────────────────────────────────────────────────────────

@superadmin_bp.route('/superadmin/notifications')
def notifications():
    if not require_superadmin():
        return redirect(url_for('auth.login'))

    notifs = execute_query(
        "SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC",
        (session['user_id'],), fetch_all=True
    ) or []
    execute_query("UPDATE notifications SET is_read=1 WHERE user_id=%s AND is_read=0",
                  (session['user_id'],), commit=True)

    return render_template('superadmin/notifications.html',
        notifications=notifs, active_page='notifications'
    )

@superadmin_bp.route('/superadmin/notifications/broadcast', methods=['POST'])
def broadcast_notification():
    if not require_superadmin():
        return redirect(url_for('auth.login'))

    title   = request.form.get('title', '').strip()
    message = request.form.get('message', '').strip()
    role    = request.form.get('role', 'all')

    if not title or not message:
        flash("Title and message are required.", 'error')
        return redirect(url_for('superadmin.notifications'))

    if role == 'all':
        targets = execute_query("SELECT id FROM users WHERE role != 'superadmin'", fetch_all=True) or []
    else:
        targets = execute_query("SELECT id FROM users WHERE role=%s", (role,), fetch_all=True) or []

    for t in targets:
        execute_query(
            "INSERT INTO notifications (user_id, title, message) VALUES (%s,%s,%s)",
            (t['id'], title, message), commit=True
        )

    log_action(session['user_id'], 'BROADCAST_NOTIFICATION', 'system', None, None, title)
    flash(f"Notification broadcast to {len(targets)} users.", 'success')
    return redirect(url_for('superadmin.notifications'))
