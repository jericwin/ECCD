from db import execute_query

sql = (
    "CREATE TABLE IF NOT EXISTS interventions ("
    "id INT AUTO_INCREMENT PRIMARY KEY,"
    "learner_id INT NOT NULL,"
    "teacher_id INT NOT NULL,"
    "bmi_status VARCHAR(20) NOT NULL,"
    "program_type VARCHAR(100) NOT NULL,"
    "description TEXT NOT NULL,"
    "start_date DATE NOT NULL,"
    "end_date DATE,"
    "status VARCHAR(20) DEFAULT 'ongoing',"
    "outcome TEXT,"
    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
    "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
    "FOREIGN KEY (learner_id) REFERENCES learners(id) ON DELETE CASCADE,"
    "FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE"
    ") ENGINE=InnoDB"
)

execute_query(sql, (), commit=True)
print("interventions table created OK")
