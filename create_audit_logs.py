from db import execute_query

def create_audit_logs():
    execute_query(
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            action VARCHAR(255) NOT NULL,
            entity_type VARCHAR(100) NOT NULL,
            entity_id INT,
            old_value TEXT,
            new_value TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """,
        (),
        commit=True
    )
    print("audit_logs table created successfully.")

if __name__ == '__main__':
    create_audit_logs()
