-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: eccd_db
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `announcements`
--

DROP TABLE IF EXISTS `announcements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `announcements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `teacher_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `category` varchar(50) DEFAULT 'general',
  `priority` varchar(20) DEFAULT 'normal',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `announcements_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `announcements`
--

LOCK TABLES `announcements` WRITE;
/*!40000 ALTER TABLE `announcements` DISABLE KEYS */;
INSERT INTO `announcements` VALUES (1,1,'Hi','Hello','general','normal','2026-07-15 04:53:08','2026-07-15 04:53:08');
/*!40000 ALTER TABLE `announcements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `assessments`
--

DROP TABLE IF EXISTS `assessments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `assessments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `learner_id` int(11) NOT NULL,
  `classwork_id` int(11) NOT NULL,
  `score` int(11) DEFAULT NULL,
  `remarks` text DEFAULT NULL,
  `graded_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `learner_id` (`learner_id`,`classwork_id`),
  KEY `classwork_id` (`classwork_id`),
  CONSTRAINT `assessments_ibfk_1` FOREIGN KEY (`learner_id`) REFERENCES `learners` (`id`) ON DELETE CASCADE,
  CONSTRAINT `assessments_ibfk_2` FOREIGN KEY (`classwork_id`) REFERENCES `classwork` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assessments`
--

LOCK TABLES `assessments` WRITE;
/*!40000 ALTER TABLE `assessments` DISABLE KEYS */;
/*!40000 ALTER TABLE `assessments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attendance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `learner_id` int(11) NOT NULL,
  `classroom_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `learner_id` (`learner_id`,`classroom_id`,`date`),
  KEY `classroom_id` (`classroom_id`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`learner_id`) REFERENCES `learners` (`id`) ON DELETE CASCADE,
  CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance`
--

LOCK TABLES `attendance` WRITE;
/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
INSERT INTO `attendance` VALUES (1,2,1,'2026-07-15','present','2026-07-15 05:09:23');
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bmi_records`
--

DROP TABLE IF EXISTS `bmi_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bmi_records` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `learner_id` int(11) NOT NULL,
  `height` decimal(5,2) NOT NULL,
  `weight` decimal(5,2) NOT NULL,
  `bmi` decimal(4,2) NOT NULL,
  `status` varchar(50) NOT NULL,
  `recorded_date` date NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `learner_id` (`learner_id`),
  CONSTRAINT `bmi_records_ibfk_1` FOREIGN KEY (`learner_id`) REFERENCES `learners` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bmi_records`
--

LOCK TABLES `bmi_records` WRITE;
/*!40000 ALTER TABLE `bmi_records` DISABLE KEYS */;
INSERT INTO `bmi_records` VALUES (1,2,90.00,80.00,98.77,'Obese','2026-07-15','2026-07-15 05:06:03'),(2,2,165.00,66.00,24.24,'Normal','2026-07-22','2026-07-22 08:13:08');
/*!40000 ALTER TABLE `bmi_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classroom_learners`
--

DROP TABLE IF EXISTS `classroom_learners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `classroom_learners` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `classroom_id` int(11) NOT NULL,
  `learner_id` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `classroom_id` (`classroom_id`,`learner_id`),
  KEY `learner_id` (`learner_id`),
  CONSTRAINT `classroom_learners_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE,
  CONSTRAINT `classroom_learners_ibfk_2` FOREIGN KEY (`learner_id`) REFERENCES `learners` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classroom_learners`
--

LOCK TABLES `classroom_learners` WRITE;
/*!40000 ALTER TABLE `classroom_learners` DISABLE KEYS */;
INSERT INTO `classroom_learners` VALUES (1,1,2,'2026-07-15 05:04:32');
/*!40000 ALTER TABLE `classroom_learners` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classrooms`
--

DROP TABLE IF EXISTS `classrooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `classrooms` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
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
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `classrooms_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classrooms`
--

LOCK TABLES `classrooms` WRITE;
/*!40000 ALTER TABLE `classrooms` DISABLE KEYS */;
INSERT INTO `classrooms` VALUES (1,1,'Punay','Math','Go','3-4 Years','2025-2026','8 AM - 10 AM','success',30,NULL,'active','2026-07-15 04:55:54');
/*!40000 ALTER TABLE `classrooms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classwork`
--

DROP TABLE IF EXISTS `classwork`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `classwork` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `classroom_id` int(11) NOT NULL,
  `subject_folder` varchar(100) NOT NULL,
  `type` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'published',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `due_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `classroom_id` (`classroom_id`),
  CONSTRAINT `classwork_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classwork`
--

LOCK TABLES `classwork` WRITE;
/*!40000 ALTER TABLE `classwork` DISABLE KEYS */;
INSERT INTO `classwork` VALUES (1,1,'Mathematics','worksheet','Math','Math',NULL,'published','2026-07-15 05:05:17','2026-07-16');
/*!40000 ALTER TABLE `classwork` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classwork_submissions`
--

DROP TABLE IF EXISTS `classwork_submissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `classwork_submissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `classwork_id` int(11) NOT NULL,
  `learner_id` int(11) NOT NULL,
  `submission_text` text DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `submitted_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `classwork_id` (`classwork_id`,`learner_id`),
  KEY `learner_id` (`learner_id`),
  CONSTRAINT `classwork_submissions_ibfk_1` FOREIGN KEY (`classwork_id`) REFERENCES `classwork` (`id`) ON DELETE CASCADE,
  CONSTRAINT `classwork_submissions_ibfk_2` FOREIGN KEY (`learner_id`) REFERENCES `learners` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classwork_submissions`
--

LOCK TABLES `classwork_submissions` WRITE;
/*!40000 ALTER TABLE `classwork_submissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `classwork_submissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enrollment_requests`
--

DROP TABLE IF EXISTS `enrollment_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `enrollment_requests` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `classroom_id` int(11) NOT NULL,
  `learner_id` int(11) NOT NULL,
  `status` varchar(20) DEFAULT 'pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `classroom_id` (`classroom_id`,`learner_id`),
  KEY `learner_id` (`learner_id`),
  CONSTRAINT `enrollment_requests_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE,
  CONSTRAINT `enrollment_requests_ibfk_2` FOREIGN KEY (`learner_id`) REFERENCES `learners` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enrollment_requests`
--

LOCK TABLES `enrollment_requests` WRITE;
/*!40000 ALTER TABLE `enrollment_requests` DISABLE KEYS */;
INSERT INTO `enrollment_requests` VALUES (1,1,2,'accepted','2026-07-15 04:56:08');
/*!40000 ALTER TABLE `enrollment_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `immunization_records`
--

DROP TABLE IF EXISTS `immunization_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `immunization_records` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `learner_id` int(11) NOT NULL,
  `vaccine_name` varchar(100) NOT NULL,
  `dose_number` int(11) NOT NULL,
  `date_administered` date NOT NULL,
  `remarks` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `learner_id` (`learner_id`),
  CONSTRAINT `immunization_records_ibfk_1` FOREIGN KEY (`learner_id`) REFERENCES `learners` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `immunization_records`
--

LOCK TABLES `immunization_records` WRITE;
/*!40000 ALTER TABLE `immunization_records` DISABLE KEYS */;
/*!40000 ALTER TABLE `immunization_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `learners`
--

DROP TABLE IF EXISTS `learners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `learners` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) NOT NULL,
  `learner_id` varchar(50) DEFAULT NULL,
  `full_name` varchar(255) NOT NULL,
  `relationship` varchar(50) NOT NULL,
  `center_name` varchar(255) DEFAULT NULL,
  `photo` varchar(255) DEFAULT NULL,
  `gender` varchar(10) DEFAULT 'Male',
  `birthdate` date DEFAULT NULL,
  `birth_certificate` varchar(255) DEFAULT NULL,
  `birth_certificate_remarks` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `learner_id` (`learner_id`),
  KEY `parent_id` (`parent_id`),
  CONSTRAINT `learners_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `parents` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `learners`
--

LOCK TABLES `learners` WRITE;
/*!40000 ALTER TABLE `learners` DISABLE KEYS */;
INSERT INTO `learners` VALUES (1,1,'LRN-1234567','Jenrie','Mother','Kinder',NULL,'Male','2015-01-05',NULL,NULL),(2,2,'LRN-12345678','Jenrie','Guardian','Kinder',NULL,'Male','2015-01-05','birth_cert_LRN-12345678.jpeg','Verified'),(3,3,'LRN-12345678910','Jenrie','Father','Kinder',NULL,'Male','2015-01-05',NULL,NULL);
/*!40000 ALTER TABLE `learners` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notifications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `link_url` varchar(255) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (1,3,'Upcoming Deadline','Reminder: \'Math\' is due tomorrow!','/parent/classwork/1',1,'2026-07-15 05:05:21'),(2,3,'Birth Certificate Remarks','Teacher Jeric Punay left a remark on Jenrie\'s birth certificate: Verified','/parent/child',1,'2026-07-17 10:30:02');
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parents`
--

DROP TABLE IF EXISTS `parents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `parents` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `parent_name` varchar(255) NOT NULL,
  `mobile` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `theme` varchar(20) DEFAULT 'green',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `parents_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parents`
--

LOCK TABLES `parents` WRITE;
/*!40000 ALTER TABLE `parents` DISABLE KEYS */;
INSERT INTO `parents` VALUES (1,2,'Jasmine','0924567898','Laguna','green'),(2,3,'Jasmine','0924567898','Laguna','rainbow'),(3,4,'Jasmine','0924567898','paete','green');
/*!40000 ALTER TABLE `parents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posts`
--

DROP TABLE IF EXISTS `posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `posts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `classroom_id` int(11) NOT NULL,
  `type` varchar(50) NOT NULL,
  `title` varchar(255) NOT NULL,
  `content` text DEFAULT NULL,
  `file_path` varchar(255) DEFAULT NULL,
  `is_pinned` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `classroom_id` (`classroom_id`),
  CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`classroom_id`) REFERENCES `classrooms` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts`
--

LOCK TABLES `posts` WRITE;
/*!40000 ALTER TABLE `posts` DISABLE KEYS */;
/*!40000 ALTER TABLE `posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teachers`
--

DROP TABLE IF EXISTS `teachers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `teachers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `employee_id` varchar(50) NOT NULL,
  `position` varchar(100) DEFAULT NULL,
  `center_name` varchar(255) DEFAULT NULL,
  `mobile` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `profile_photo` varchar(255) DEFAULT NULL,
  `security_answer` varchar(255) NOT NULL,
  `theme` varchar(20) DEFAULT 'green',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `employee_id` (`employee_id`),
  CONSTRAINT `teachers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teachers`
--

LOCK TABLES `teachers` WRITE;
/*!40000 ALTER TABLE `teachers` DISABLE KEYS */;
INSERT INTO `teachers` VALUES (1,1,'Jeric Punay','EMP-12345','Worker','Kinder','09270196752','Laguna',NULL,'PES','rainbow');
/*!40000 ALTER TABLE `teachers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `role` varchar(20) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'jeric','scrypt:32768:8:1$b5lOl9HZ4OKi6wEX$20616d13ce6be0a2921bd0edab85b055f0ac2a36509d8c6ae92105bcddd3bacb402f159ec0795e29c1eb33e3bf45bc78a7a27879540f5e1a3856c9770502a4c9','punay.jeric@gmail.com','teacher','2026-07-15 04:31:14'),(2,'jenrie','scrypt:32768:8:1$8K2ziafY5A3LmkhZ$ddf4a8794bc67327916072dd043cb4dee43d4e5a21b5108ef9bb64fa0d84e9bd1f0729e02054252c1af648800701796fe09aabca930cd174cd76f4e253e70191','jasmine.araza@gmail.com','parent','2026-07-15 04:32:55'),(3,'jasmine','scrypt:32768:8:1$vi1XS8vTgjqGmvL6$0256a092b5106385e8d070610ee76bfcc84a2c4a77fb0405c426cd403acac03a7483c71416105edd946bcda3589b3f00a0ce7ee63e77afef39453efc0a1b8ba4','jasmine.araza1@gmail.com','parent','2026-07-15 04:35:27'),(4,'jenrie1','scrypt:32768:8:1$veKffY11ckewb7BU$fc7dd611efebbc0907658186ee32888819ef2db3599ff0160807d4384cb94fb6e32ad9999aeff5e307e1471a0ac41bf579d4c15c164a2f64a6d51ecc1e8fc905','jasmine.araza123@gmail.com','parent','2026-07-22 07:41:05');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-22 16:30:43
