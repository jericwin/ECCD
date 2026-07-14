from flask import Blueprint, render_template, session, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    # If already logged in, redirect to respective dashboard
    if 'user_id' in session:
        role = session.get('role')
        if role == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif role == 'parent':
            return redirect(url_for('parent.dashboard'))
    return render_template('landing.html')
