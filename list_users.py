from db import execute_query

users = execute_query("SELECT username, email, role FROM users", (), fetch_all=True)
for u in users:
    print(f"Role: {u['role'].ljust(15)} | Username: {u['username'].ljust(20)} | Email: {u['email']}")
