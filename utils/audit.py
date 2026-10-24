from db import execute_query

def log_action(user_id, action, entity_type, entity_id=None, old_value=None, new_value=None):
    """
    Logs an action to the audit_logs table.
    
    :param user_id: ID of the user performing the action
    :param action: Description of the action (e.g. 'CREATED_SCHOOL')
    :param entity_type: The type of entity modified (e.g. 'school', 'user', 'enrollment')
    :param entity_id: Optional ID of the modified entity
    :param old_value: Optional old value or state
    :param new_value: Optional new value or state
    """
    try:
        execute_query(
            """
            INSERT INTO audit_logs (user_id, action, entity_type, entity_id, old_value, new_value)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, action, entity_type, entity_id, str(old_value) if old_value else None, str(new_value) if new_value else None),
            commit=True
        )
    except Exception as e:
        print(f"Failed to log audit action: {e}")
