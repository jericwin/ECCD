from flask import Blueprint, render_template, redirect, url_for, flash, session, request, jsonify
from db import execute_query
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

# ─── Helpers ────────────────────────────────────────────────────────────────

def require_chat_user():
    """Return (user_id, role, display_name) or redirect."""
    user_id = session.get('user_id')
    role    = session.get('role')
    if not user_id or role not in ('parent', 'teacher'):
        return None, None, None

    if role == 'parent':
        row = execute_query("SELECT parent_name FROM parents WHERE user_id = %s", (user_id,), fetch_one=True)
        name = row['parent_name'] if row else 'Parent'
    else:
        row = execute_query("SELECT full_name FROM teachers WHERE user_id = %s", (user_id,), fetch_one=True)
        name = row['full_name'] if row else 'Teacher'

    return user_id, role, name


def get_addable_users(user_id, role):
    """
    Return list of dicts {user_id, display_name, role} that the current user
    is allowed to add to a group chat.
    Parents  → their classroom teacher + other parents in same classroom
    Teachers → parents from their classrooms + teachers in same school
    """
    users = []

    if role == 'parent':
        parent = execute_query("SELECT id FROM parents WHERE user_id = %s", (user_id,), fetch_one=True)
        if not parent:
            return []
        learner = execute_query("SELECT id FROM learners WHERE parent_id = %s", (parent['id'],), fetch_one=True)
        if not learner:
            return []
        cl = execute_query("SELECT classroom_id FROM classroom_learners WHERE learner_id = %s", (learner['id'],), fetch_one=True)
        if not cl:
            return []
        cid = cl['classroom_id']

        teacher = execute_query(
            """SELECT u.id as user_id, t.full_name as display_name, 'teacher' as role
               FROM classrooms c
               JOIN teachers t ON c.teacher_id = t.id
               JOIN users u ON t.user_id = u.id
               WHERE c.id = %s""",
            (cid,), fetch_one=True
        )
        if teacher and teacher['user_id'] != user_id:
            users.append(dict(teacher))

        parents = execute_query(
            """SELECT DISTINCT u.id as user_id, p.parent_name as display_name, 'parent' as role
               FROM classroom_learners cl
               JOIN learners l ON cl.learner_id = l.id
               JOIN parents p ON l.parent_id = p.id
               JOIN users u ON p.user_id = u.id
               WHERE cl.classroom_id = %s AND u.id != %s""",
            (cid, user_id), fetch_all=True
        ) or []
        for p in parents:
            users.append(dict(p))

    elif role == 'teacher':
        teacher = execute_query("SELECT id, school_id FROM teachers WHERE user_id = %s", (user_id,), fetch_one=True)
        if not teacher:
            return []

        parents = execute_query(
            """SELECT DISTINCT u.id as user_id, p.parent_name as display_name, 'parent' as role
               FROM classrooms c
               JOIN classroom_learners cl ON cl.classroom_id = c.id
               JOIN learners l ON cl.learner_id = l.id
               JOIN parents p ON l.parent_id = p.id
               JOIN users u ON p.user_id = u.id
               WHERE c.teacher_id = %s""",
            (teacher['id'],), fetch_all=True
        ) or []
        for p in parents:
            users.append(dict(p))

        if teacher.get('school_id'):
            others = execute_query(
                """SELECT u.id as user_id, t.full_name as display_name, 'teacher' as role
                   FROM teachers t
                   JOIN users u ON t.user_id = u.id
                   WHERE t.school_id = %s AND t.user_id != %s""",
                (teacher['school_id'], user_id), fetch_all=True
            ) or []
            for t in others:
                users.append(dict(t))

    return users


# ─── Routes ─────────────────────────────────────────────────────────────────

@chat_bp.route('/chats')
def list_chats():
    user_id, role, name = require_chat_user()
    if not user_id:
        return redirect(url_for('auth.login'))

    groups = execute_query(
        """SELECT cg.id, cg.name, cg.created_by, cg.created_at,
               (SELECT COUNT(*) FROM chat_group_members m2 WHERE m2.group_id = cg.id) as member_count,
               (SELECT msg.message   FROM chat_messages msg WHERE msg.group_id = cg.id ORDER BY msg.sent_at DESC LIMIT 1) as last_message,
               (SELECT msg.sender_name FROM chat_messages msg WHERE msg.group_id = cg.id ORDER BY msg.sent_at DESC LIMIT 1) as last_sender,
               (SELECT msg.sent_at   FROM chat_messages msg WHERE msg.group_id = cg.id ORDER BY msg.sent_at DESC LIMIT 1) as last_sent_at
           FROM chat_groups cg
           JOIN chat_group_members cgm ON cgm.group_id = cg.id
           WHERE cgm.user_id = %s
           ORDER BY last_sent_at DESC, cg.created_at DESC""",
        (user_id,), fetch_all=True
    ) or []

    return render_template(
        'chat/list.html',
        active_page='group_chat',
        groups=groups,
        current_user_id=user_id,
        my_name=name,
        now=datetime.now()
    )


@chat_bp.route('/chats/create', methods=['GET', 'POST'])
def create_chat():
    user_id, role, name = require_chat_user()
    if not user_id:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        group_name  = request.form.get('group_name', '').strip()
        member_ids  = request.form.getlist('member_ids')

        if not group_name:
            flash('Group name is required.', 'error')
            return redirect(url_for('chat.create_chat'))

        result   = execute_query("INSERT INTO chat_groups (name, created_by) VALUES (%s, %s)",
                                 (group_name, user_id), commit=True)
        group_id = result['lastrowid']

        # Add creator
        execute_query(
            "INSERT INTO chat_group_members (group_id, user_id, display_name, display_role) VALUES (%s, %s, %s, %s)",
            (group_id, user_id, name, role), commit=True
        )

        # Add chosen members
        addable = {str(u['user_id']): u for u in get_addable_users(user_id, role)}
        for mid in member_ids:
            if mid in addable and mid != str(user_id):
                u = addable[mid]
                try:
                    execute_query(
                        "INSERT INTO chat_group_members (group_id, user_id, display_name, display_role) VALUES (%s, %s, %s, %s)",
                        (group_id, u['user_id'], u['display_name'], u['role']), commit=True
                    )
                except Exception:
                    pass

        flash(f'Group "{group_name}" created!', 'success')
        return redirect(url_for('chat.view_chat', group_id=group_id))

    available = get_addable_users(user_id, role)
    return render_template('chat/create.html', active_page='group_chat', available_users=available)


@chat_bp.route('/chats/<int:group_id>')
def view_chat(group_id):
    user_id, role, name = require_chat_user()
    if not user_id:
        return redirect(url_for('auth.login'))

    membership = execute_query(
        "SELECT * FROM chat_group_members WHERE group_id = %s AND user_id = %s",
        (group_id, user_id), fetch_one=True
    )
    if not membership:
        flash('You are not a member of this group.', 'error')
        return redirect(url_for('chat.list_chats'))

    group = execute_query("SELECT * FROM chat_groups WHERE id = %s", (group_id,), fetch_one=True)
    if not group:
        flash('Group not found.', 'error')
        return redirect(url_for('chat.list_chats'))

    messages = execute_query(
        "SELECT * FROM chat_messages WHERE group_id = %s ORDER BY sent_at ASC",
        (group_id,), fetch_all=True
    ) or []

    members = execute_query(
        "SELECT * FROM chat_group_members WHERE group_id = %s ORDER BY added_at ASC",
        (group_id,), fetch_all=True
    ) or []

    member_ids     = {m['user_id'] for m in members}
    available_add  = [u for u in get_addable_users(user_id, role) if u['user_id'] not in member_ids]
    is_creator     = (group['created_by'] == user_id)

    return render_template(
        'chat/view.html',
        active_page='group_chat',
        group=group,
        messages=messages,
        members=members,
        available_add=available_add,
        current_user_id=user_id,
        is_creator=is_creator
    )


@chat_bp.route('/chats/<int:group_id>/send', methods=['POST'])
def send_message(group_id):
    user_id, role, name = require_chat_user()
    if not user_id:
        return redirect(url_for('auth.login'))

    membership = execute_query(
        "SELECT id FROM chat_group_members WHERE group_id = %s AND user_id = %s",
        (group_id, user_id), fetch_one=True
    )
    if not membership:
        return redirect(url_for('chat.list_chats'))

    message = request.form.get('message', '').strip()
    if message:
        execute_query(
            "INSERT INTO chat_messages (group_id, sender_user_id, sender_name, sender_role, message) VALUES (%s, %s, %s, %s, %s)",
            (group_id, user_id, name, role, message), commit=True
        )
    return redirect(url_for('chat.view_chat', group_id=group_id))


@chat_bp.route('/chats/<int:group_id>/add-member', methods=['POST'])
def add_member(group_id):
    user_id, role, _ = require_chat_user()
    if not user_id:
        return redirect(url_for('auth.login'))

    membership = execute_query(
        "SELECT id FROM chat_group_members WHERE group_id = %s AND user_id = %s",
        (group_id, user_id), fetch_one=True
    )
    if not membership:
        flash('Access denied.', 'error')
        return redirect(url_for('chat.list_chats'))

    new_uid = request.form.get('user_id', type=int)
    addable = get_addable_users(user_id, role)
    target  = next((u for u in addable if u['user_id'] == new_uid), None)

    if not target:
        flash('Cannot add this user.', 'error')
        return redirect(url_for('chat.view_chat', group_id=group_id))

    try:
        execute_query(
            "INSERT INTO chat_group_members (group_id, user_id, display_name, display_role) VALUES (%s, %s, %s, %s)",
            (group_id, target['user_id'], target['display_name'], target['role']), commit=True
        )
        flash(f'{target["display_name"]} added to the group.', 'success')
    except Exception:
        flash('Already a member.', 'info')

    return redirect(url_for('chat.view_chat', group_id=group_id))


@chat_bp.route('/chats/<int:group_id>/remove-member', methods=['POST'])
def remove_member(group_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    group = execute_query("SELECT * FROM chat_groups WHERE id = %s", (group_id,), fetch_one=True)
    if not group:
        return redirect(url_for('chat.list_chats'))

    # Must be a member
    membership = execute_query(
        "SELECT id FROM chat_group_members WHERE group_id = %s AND user_id = %s",
        (group_id, user_id), fetch_one=True
    )
    if not membership:
        return redirect(url_for('chat.list_chats'))

    target_uid = request.form.get('target_user_id', type=int)
    is_creator = (group['created_by'] == user_id)

    if is_creator or target_uid == user_id:
        execute_query(
            "DELETE FROM chat_group_members WHERE group_id = %s AND user_id = %s",
            (group_id, target_uid), commit=True
        )
        if target_uid == user_id:
            flash('You left the group.', 'info')
            return redirect(url_for('chat.list_chats'))
        flash('Member removed.', 'success')
    else:
        flash('Only the creator can remove others.', 'error')

    return redirect(url_for('chat.view_chat', group_id=group_id))


@chat_bp.route('/chats/search-users')
def search_users():
    user_id, role, _ = require_chat_user()
    if not user_id:
        return jsonify([])

    q     = request.args.get('q', '').strip().lower()
    users = get_addable_users(user_id, role)
    if q:
        users = [u for u in users if q in u['display_name'].lower()]
    return jsonify(users[:20])
