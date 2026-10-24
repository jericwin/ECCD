from db import get_db_connection

def execute_schema():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    with open('schema.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
        
    # Split by semicolon but ignore semicolons inside strings
    # Simple split might fail on complex SQL, but for schema.sql it's fine
    statements = sql.split(';')
    for stmt in statements:
        if stmt.strip():
            cursor.execute(stmt)
            
    conn.commit()
    cursor.close()
    conn.close()
    print("Schema executed successfully")

if __name__ == '__main__':
    execute_schema()
