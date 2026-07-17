-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 17, 2026 at 01:05 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `eccd_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `announcements`
--

CREATE TABLE `announcements` (
  `id` int(11) NOT NULL,
  `teacher_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `category` varchar(50) DEFAULT 'general',
  `priority` varchar(20) DEFAULT 'normal',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `announcements`
--

INSERT INTO `announcements` (`id`, `teacher_id`, `title`, `content`, `category`, `priority`, `created_at`, `updated_at`) VALUES
(1, 1, 'Hi', 'Hello', 'general', 'normal', '2026-07-15 04:53:08', '2026-07-15 04:53:08');

-- --------------------------------------------------------

--
-- Table structure for table `assessments`
--

CREATE TABLE `assessments` (
  `id` int(11) NOT NULL,
  `learner_id` int(11) NOT NULL,
  `classwork_id` int(11) NOT NULL,
  `score` int(11) DEFAULT NULL,
  `remarks` text DEFAULT NULL,
  `graded_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `attendance`
--

CREATE TABLE `attendance` (
  `id` int(11) NOT NULL,
  `learner_id` int(11) NOT NULL,
  `classroom_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `attendance`
--

INSERT INTO `attendance` (`id`, `learner_id`, `classroom_id`, `date`, `status`, `created_at`) VALUES
(1, 2, 1, '2026-07-15', 'present', '2026-07-15 05:09:23');

-- --------------------------------------------------------

--
-- Table structure for table `bmi_records`
--

CREATE TABLE `bmi_records` (
  `id` int(11) NOT NULL,
  `learner_id` int(11) NOT NULL,
  `height` decimal(5,2) NOT NULL,
  `weight` decimal(5,2) NOT NULL,
  `bmi` decimal(4,2) NOT NULL,
  `status` varchar(50) NOT NULL,
  `recorded_date` date NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bmi_records`
--

INSERT INTO `bmi_records` (`id`, `learner_id`, `height`, `weight`, `bmi`, `status`, `recorded_date`, `created_at`) VALUES
(1, 2, 90.00, 80.00, 98.77, 'Obese', '2026-07-15', '2026-07-15 05:06:03');

-- --------------------------------------------------------

--
-- Table structure for table `classrooms`
--

CREATE TABLE `classrooms` (
  `id` int(11) NOT NULL,
  `teacher_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `subject` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `age_group` varchar(50) DEFAULT NULL,
  `school_year` varchar(50) DEFAULT NULL,
  `schedule` varchar(255) DEFAULT NULL,
  `theme_color` varchar(50) DEFAULT 'success',
  `max_learners` int(11) DEFAULT 30,
  `banner` varchar(255) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'active',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `classrooms`
--

INSERT INTO `classrooms` (`id`, `teacher_id`, `name`, `subject`, `description`, `age_group`, `school_year`, `schedule`, `theme_color`, `max_learners`, `banner`, `status`, `created_at`) VALUES
(1, 1, 'Punay', 'Math', 'Go', '3-4 Years', '2025-2026', '8 AM - 10 AM', 'success', 30, NULL, 'active', '2026-07-15 04:55:54');

-- --------------------------------------------------------

--
-- Table structure for table `classroom_learners`
--

CREATE TABLE `classroom_learners` (
  `id` int(11) NOT NULL,
  `classroom_id` int(11) NOT NULL,
  `learner_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `classroom_learners`
--

INSERT INTO `classroom_learners` (`id`, `classroom_id`, `learner_id`, `created_at`) VALUES
(1, 1, 2, '2026-07-15 05:04:32');

-- --------------------------------------------------------

--
-- Table structure for table `classwork`
--

CREATE TABLE `classwork` (
  `id` int(11) NOT NULL,
  `classroom_id` int(11) NOT NULL,
  `subject_folder` varchar(100) NOT NULL,
  `type` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'published',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `due_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `classwork`
--

INSERT INTO `classwork` (`id`, `classroom_id`, `subject_folder`, `type`, `title`, `description`, `file_path`, `status`, `created_at`, `due_date`) VALUES
(1, 1, 'Mathematics', 'worksheet', 'Math', 'Math', NULL, 'published', '2026-07-15 05:05:17', '2026-07-16');

-- --------------------------------------------------------

--
-- Table structure for table `classwork_submissions`
--

CREATE TABLE `classwork_submissions` (
  `id` int(11) NOT NULL,
  `classwork_id` int(11) NOT NULL,
  `learner_id` int(11) NOT NULL,
  `submission_text` text DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `submitted_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `enrollment_requests`
--

CREATE TABLE `enrollment_requests` (
  `id` int(11) NOT NULL,
  `classroom_id` int(11) NOT NULL,
  `learner_id` int(11) NOT NULL,
  `status` varchar(20) DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `enrollment_requests`
--

INSERT INTO `enrollment_requests` (`id`, `classroom_id`, `learner_id`, `status`, `created_at`) VALUES
(1, 1, 2, 'accepted', '2026-07-15 04:56:08');

-- --------------------------------------------------------

--
-- Table structure for table `immunization_records`
--

CREATE TABLE `immunization_records` (
  `id` int(11) NOT NULL,
  `learner_id` int(11) NOT NULL,
  `vaccine_name` varchar(100) NOT NULL,
  `dose_number` int(11) NOT NULL,
  `date_administered` date NOT NULL,
  `remarks` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `learners`
--

CREATE TABLE `learners` (
  `id` int(11) NOT NULL,
  `parent_id` int(11) NOT NULL,
  `learner_id` varchar(50) DEFAULT NULL,
  `full_name` varchar(255) NOT NULL,
  `relationship` varchar(50) NOT NULL,
  `center_name` varchar(255) DEFAULT NULL,
  `photo` varchar(255) DEFAULT NULL,
  `gender` varchar(10) DEFAULT 'Male',
  `birthdate` date DEFAULT NULL,
  `birth_certificate` varchar(255) DEFAULT NULL,
  `birth_certificate_remarks` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `learners`
--

INSERT INTO `learners` (`id`, `parent_id`, `learner_id`, `full_name`, `relationship`, `center_name`, `photo`, `gender`, `birthdate`, `birth_certificate`, `birth_certificate_remarks`) VALUES
(1, 1, 'LRN-1234567', 'Jenrie', 'Mother', 'Kinder', NULL, 'Male', '2015-01-05', NULL, NULL),
(2, 2, 'LRN-12345678', 'Jenrie', 'Guardian', 'Kinder', NULL, 'Male', '2015-01-05', 'birth_cert_LRN-12345678.jpeg', 'Verified');

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `link_url` varchar(255) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `title`, `message`, `link_url`, `is_read`, `created_at`) VALUES
(1, 3, 'Upcoming Deadline', 'Reminder: \'Math\' is due tomorrow!', '/parent/classwork/1', 1, '2026-07-15 05:05:21'),
(2, 3, 'Birth Certificate Remarks', 'Teacher Jeric Punay left a remark on Jenrie\'s birth certificate: Verified', '/parent/child', 1, '2026-07-17 10:30:02');

-- --------------------------------------------------------

--
-- Table structure for table `parents`
--

CREATE TABLE `parents` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `parent_name` varchar(255) NOT NULL,
  `mobile` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `theme` varchar(20) DEFAULT 'green'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `parents`
--

INSERT INTO `parents` (`id`, `user_id`, `parent_name`, `mobile`, `address`, `theme`) VALUES
(1, 2, 'Jasmine', '0924567898', 'Laguna', 'green'),
(2, 3, 'Jasmine', '0924567898', 'Laguna', 'rainbow');

-- --------------------------------------------------------

--
-- Table structure for table `posts`
--

CREATE TABLE `posts` (
  `id` int(11) NOT NULL,
  `classroom_id` int(11) NOT NULL,
  `type` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `is_pinned` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `teachers`
--

CREATE TABLE `teachers` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `employee_id` varchar(50) NOT NULL,
  `position` varchar(100) DEFAULT NULL,
  `center_name` varchar(255) DEFAULT NULL,
  `mobile` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `profile_photo` varchar(255) DEFAULT NULL,
  `security_answer` varchar(255) NOT NULL,
  `theme` varchar(20) DEFAULT 'green'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `teachers`
--

INSERT INTO `teachers` (`id`, `user_id`, `full_name`, `employee_id`, `position`, `center_name`, `mobile`, `address`, `profile_photo`, `security_answer`, `theme`) VALUES
(1, 1, 'Jeric Punay', 'EMP-12345', 'Worker', 'Kinder', '09270196752', 'Laguna', NULL, 'PES', 'rainbow');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `email`, `role`, `created_at`) VALUES
(1, 'jeric', 'scrypt:32768:8:1$b5lOl9HZ4OKi6wEX$20616d13ce6be0a2921bd0edab85b055f0ac2a36509d8c6ae92105bcddd3bacb402f159ec0795e29c1eb33e3bf45bc78a7a27879540f5e1a3856c9770502a4c9', 'punay.jeric@gmail.com', 'teacher', '2026-07-15 04:31:14'),
(2, 'jenrie', 'scrypt:32768:8:1$8K2ziafY5A3LmkhZ$ddf4a8794bc67327916072dd043cb4dee43d4e5a21b5108ef9bb64fa0d84e9bd1f0729e02054252c1af648800701796fe09aabca930cd174cd76f4e253e70191', 'jasmine.araza@gmail.com', 'parent', '2026-07-15 04:32:55'),
(3, 'jasmine', 'scrypt:32768:8:1$vi1XS8vTgjqGmvL6$0256a092b5106385e8d070610ee76bfcc84a2c4a77fb0405c426cd403acac03a7483c71416105edd946bcda3589b3f00a0ce7ee63e77afef39453efc0a1b8ba4', 'jasmine.araza1@gmail.com', 'parent', '2026-07-15 04:35:27');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `announcements`
--
ALTER TABLE `announcements`
  ADD PRIMARY KEY (`id`),
  ADD KEY `teacher_id` (`teacher_id`);

--
-- Indexes for table `assessments`
--
ALTER TABLE `assessments`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `learner_id` (`learner_id`,`classwork_id`),
  ADD KEY `classwork_id` (`classwork_id`);

--
-- Indexes for table `attendance`
--
ALTER TABLE `attendance`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `learner_id` (`learner_id`,`classroom_id`,`date`),
  ADD KEY `classroom_id` (`classroom_id`);

--
-- Indexes for table `bmi_records`
--
ALTER TABLE `bmi_records`
  ADD PRIMARY KEY (`id`),
  ADD KEY `learner_id` (`learner_id`);

--
-- Indexes for table `classrooms`
--
ALTER TABLE `classrooms`
  ADD PRIMARY KEY (`id`),
  ADD KEY `teacher_id` (`teacher_id`);

--
-- Indexes for table `classroom_learners`
--
ALTER TABLE `classroom_learners`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `classroom_id` (`classroom_id`,`learner_id`),
  ADD KEY `learner_id` (`learner_id`);

--
-- Indexes for table `classwork`
--
ALTER TABLE `classwork`
  ADD PRIMARY KEY (`id`),
  ADD KEY `classroom_id` (`classroom_id`);

--
-- Indexes for table `classwork_submissions`
--
ALTER TABLE `classwork_submissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `classwork_id` (`classwork_id`,`learner_id`),
  ADD KEY `learner_id` (`learner_id`);

--
-- Indexes for table `enrollment_requests`
--
ALTER TABLE `enrollment_requests`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `classroom_id` (`classroom_id`,`learner_id`),
  ADD KEY `learner_id` (`learner_id`);

--
-- Indexes for table `immunization_records`
--
ALTER TABLE `immunization_records`
  ADD PRIMARY KEY (`id`),
  ADD KEY `learner_id` (`learner_id`);

--
-- Indexes for table `learners`
--
ALTER TABLE `learners`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `learner_id` (`learner_id`),
  ADD KEY `parent_id` (`parent_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `parents`
--
ALTER TABLE `parents`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`);

--
-- Indexes for table `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `classroom_id` (`classroom_id`);

--
-- Indexes for table `teachers`
--
ALTER TABLE `teachers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `user_id` (`user_id`),
  ADD UNIQUE KEY `employee_id` (`employee_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `announcements`
--
ALTER TABLE `announcements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `assessments`
--
ALTER TABLE `assessments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `attendance`
--
ALTER TABLE `attendance`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `bmi_records`
--
ALTER TABLE `bmi_records`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `classrooms`
--
ALTER TABLE `classrooms`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `classroom_learners`
--
ALTER TABLE `classroom_learners`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `classwork`
--
ALTER TABLE `classwork`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `classwork_submissions`
--
ALTER TABLE `classwork_submissions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `enrollment_requests`
--
ALTER TABLE `enrollment_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `immunization_records`
--
ALTER TABLE `immunization_records`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `learners`
--
ALTER TABLE `learners`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `parents`
--
ALTER TABLE `parents`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `posts`
--
ALTER TABLE `posts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `teachers`
--
ALTER TABLE `teachers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `announcements`
--
ALTER TABLE `announcements`
  ADD CONSTRAINT `announcements_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `assessments`
--
ALTER TABLE `assessments`
  ADD CONSTRAINT `assessments_ibfk_1` FOREIGN KEY (`learner_id`) REFERENCES `learners` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `assessments_ibfk_2` FOREIGN KEY (`classwork_id`) REFERENCES `classwork` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `attendance`
--
ALTER TABLE `attendance`
  ADD CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`learner_id`) REFERENCES `learners` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `bmi_records`
--
ALTER TABLE `bmi_records`
  ADD CONSTRAINT `bmi_records_ibfk_1` FOREIGN KEY (`learner_id`) REFERENCES `learners` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `classrooms`
--
ALTER TABLE `classrooms`
  ADD CONSTRAINT `classrooms_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `classroom_learners`
--
ALTER TABLE `classroom_learners`
  ADD CONSTRAINT `classroom_learners_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `classroom_learners_ibfk_2` FOREIGN KEY (`learner_id`) REFERENCES `learners` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `classwork`
--
ALTER TABLE `classwork`
  ADD CONSTRAINT `classwork_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `classwork_submissions`
--
ALTER TABLE `classwork_submissions`
  ADD CONSTRAINT `classwork_submissions_ibfk_1` FOREIGN KEY (`classwork_id`) REFERENCES `classwork` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `classwork_submissions_ibfk_2` FOREIGN KEY (`learner_id`) REFERENCES `learners` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `enrollment_requests`
--
ALTER TABLE `enrollment_requests`
  ADD CONSTRAINT `enrollment_requests_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `enrollment_requests_ibfk_2` FOREIGN KEY (`learner_id`) REFERENCES `learners` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `immunization_records`
--
ALTER TABLE `immunization_records`
  ADD CONSTRAINT `immunization_records_ibfk_1` FOREIGN KEY (`learner_id`) REFERENCES `learners` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `learners`
--
ALTER TABLE `learners`
  ADD CONSTRAINT `learners_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `parents` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `parents`
--
ALTER TABLE `parents`
  ADD CONSTRAINT `parents_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `posts`
--
ALTER TABLE `posts`
  ADD CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `teachers`
--
ALTER TABLE `teachers`
  ADD CONSTRAINT `teachers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
