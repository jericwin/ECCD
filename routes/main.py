from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from db import execute_query

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    # If already logged in, redirect to respective dashboard
    if 'user_id' in session:
        role = session.get('role')
        if role == 'teacher' or role == 'school':
            return redirect(url_for('school.dashboard')) if role == 'school' else redirect(url_for('teacher.dashboard'))
        elif role == 'parent':
            return redirect(url_for('parent.dashboard'))
        elif role == 'municipality':
            return redirect(url_for('municipality.dashboard'))
        elif role == 'provincial':
            return redirect(url_for('provincial.dashboard'))
    return render_template('public/landing.html')

@main_bp.route('/api/public/schools')
def get_public_schools():
    try:
        schools = execute_query(
            "SELECT id, name, address, latitude, longitude, is_accepting_enrollees FROM schools WHERE status = 'approved'",
            fetch_all=True
        )
        for school in schools:
            if school['latitude'] is not None:
                school['latitude'] = float(school['latitude'])
            if school['longitude'] is not None:
                school['longitude'] = float(school['longitude'])
        return jsonify({'schools': schools})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
