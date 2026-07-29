from db import execute_query
from werkzeug.security import generate_password_hash

p = generate_password_hash('password123')
execute_query("UPDATE users SET password=%s WHERE username IN ('jenrie', 'jasmine', 'jeric')", (p,), commit=True)
print("Passwords updated!")
