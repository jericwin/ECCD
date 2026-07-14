-- Migration: Add announcements table for teacher-to-parent announcements
-- This table is separate from classroom-scoped posts and allows teachers
-- to broadcast announcements to all parents of their learners.

CREATE TABLE IF NOT EXISTS announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'general',  -- 'general', 'event', 'reminder', 'urgent'
    priority VARCHAR(20) DEFAULT 'normal',   -- 'normal', 'high', 'urgent'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
) ENGINE=InnoDB;
