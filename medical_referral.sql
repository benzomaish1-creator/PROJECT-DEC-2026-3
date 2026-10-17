-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 17, 2026 at 09:28 AM
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
-- Database: `medical_referral`
--

-- --------------------------------------------------------

--
-- Table structure for table `admins`
--

CREATE TABLE `admins` (
  `admin_id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admins`
--

INSERT INTO `admins` (`admin_id`, `username`, `email`, `password`, `created_at`) VALUES
(1, 'System Admin', 'admin@docconnect.com', 'admin1', '2026-07-28 11:17:41');

-- --------------------------------------------------------

--
-- Table structure for table `appointments`
--

CREATE TABLE `appointments` (
  `appointment_id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `doctor_id` int(11) NOT NULL,
  `reason` text NOT NULL,
  `appointment_date` date NOT NULL,
  `appointment_time` time NOT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `feedback` text DEFAULT NULL,
  `payment_status` varchar(20) NOT NULL DEFAULT 'Pending',
  `mpesa_checkout_request_id` varchar(100) DEFAULT NULL,
  `mpesa_receipt_number` varchar(50) DEFAULT NULL,
  `amount_paid` decimal(10,2) DEFAULT NULL,
  `payment_phone` varchar(20) DEFAULT NULL,
  `follow_up_of_appointment_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `appointments`
--

INSERT INTO `appointments` (`appointment_id`, `patient_id`, `doctor_id`, `reason`, `appointment_date`, `appointment_time`, `status`, `created_at`, `feedback`, `payment_status`, `mpesa_checkout_request_id`, `mpesa_receipt_number`, `amount_paid`, `payment_phone`, `follow_up_of_appointment_id`) VALUES
(55, 9, 23, 'gingivitis', '2026-08-02', '09:40:00', 'Completed', '2026-08-02 05:39:05', 'done', 'Pending', NULL, NULL, NULL, NULL, NULL),
(56, 11, 23, 'tooth cavity', '2026-08-03', '09:40:00', 'Completed', '2026-08-02 05:40:59', 'done', 'Pending', NULL, NULL, NULL, NULL, NULL),
(57, 10, 19, 'anxiety disorder', '2026-08-03', '09:40:00', 'Completed', '2026-08-02 05:42:15', 'done', 'Pending', NULL, NULL, NULL, NULL, NULL),
(58, 9, 23, 'root canal', '2026-08-11', '09:40:00', 'Completed', '2026-08-02 05:50:10', 'done', 'Pending', NULL, NULL, NULL, NULL, NULL),
(59, 11, 23, 'gingivitis', '2026-08-12', '09:40:00', 'Completed', '2026-08-02 05:51:59', 'done', 'Pending', NULL, NULL, NULL, NULL, NULL),
(60, 10, 19, 'depression disorder', '2026-08-12', '09:40:00', 'Completed', '2026-08-02 05:53:36', 'done', 'Pending', NULL, NULL, NULL, NULL, NULL),
(61, 11, 23, 'check up', '2026-08-24', '11:00:00', 'Completed', '2026-08-02 11:09:36', 'continue with your dosage', 'Pending', NULL, NULL, NULL, NULL, 59),
(62, 10, 6, 'urinary track', '2026-08-17', '11:00:00', 'Completed', '2026-08-02 12:20:56', NULL, 'Pending', NULL, NULL, NULL, NULL, NULL),
(63, 10, 28, 'please come on time', '2026-08-10', '11:00:00', 'Completed', '2026-08-02 12:29:16', 'ok', 'Pending', NULL, NULL, NULL, NULL, NULL),
(64, 11, 23, 'cavity', '2026-08-17', '11:00:00', 'Declined', '2026-08-16 01:59:53', 'not feeling well i was attending another doc but i canreffer you to another dentist', 'Pending', NULL, NULL, NULL, NULL, NULL),
(65, 9, 19, 'anxiety', '2026-08-16', '09:00:00', 'Completed', '2026-08-16 02:33:16', 'keep time', 'Pending', NULL, NULL, NULL, NULL, NULL),
(66, 9, 23, 'tooth ache', '2026-08-24', '14:20:00', 'Completed', '2026-08-24 10:14:40', 'please avail', 'Pending', NULL, NULL, NULL, NULL, NULL),
(67, 9, 23, 'checking if there is any improvement', '2026-09-02', '04:20:00', 'Completed', '2026-08-25 21:15:15', 'take dosage properly', 'Pending', NULL, NULL, NULL, NULL, 55),
(68, 9, 2, 'skin rash', '2026-10-03', '10:20:00', 'Pending', '2026-09-23 04:01:02', NULL, 'Pending', NULL, NULL, NULL, NULL, NULL),
(69, 9, 6, 'urinary track', '2026-10-18', '09:40:00', 'Pending', '2026-10-17 06:49:59', NULL, 'Pending', NULL, NULL, NULL, NULL, NULL),
(70, 9, 21, 'headache , sweating', '2026-10-19', '11:00:00', 'Pending', '2026-10-17 07:19:15', NULL, 'Pending', NULL, NULL, NULL, NULL, NULL),
(71, 11, 18, 'back pain,fever', '2026-10-21', '15:00:00', 'Pending', '2026-10-17 07:25:24', NULL, 'Pending', NULL, NULL, NULL, NULL, NULL);

--
-- Triggers `appointments`
--
DELIMITER $$
CREATE TRIGGER `trg_appt_no_double_book_insert` BEFORE INSERT ON `appointments` FOR EACH ROW BEGIN
  DECLARE slot_taken INT;
  IF NEW.status NOT IN ('Declined', 'Completed', 'Cancelled') THEN
    SELECT COUNT(*) INTO slot_taken FROM appointments
      WHERE doctor_id = NEW.doctor_id
        AND appointment_date = NEW.appointment_date
        AND appointment_time = NEW.appointment_time
        AND status NOT IN ('Declined', 'Completed', 'Cancelled');
    IF slot_taken > 0 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'This doctor already has an appointment at that date and time.';
    END IF;
  END IF;
END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `trg_appt_no_double_book_update` BEFORE UPDATE ON `appointments` FOR EACH ROW BEGIN
  DECLARE slot_taken INT;
  IF NEW.status NOT IN ('Declined', 'Completed', 'Cancelled')
     AND (NEW.appointment_date <> OLD.appointment_date
          OR NEW.appointment_time <> OLD.appointment_time
          OR NEW.doctor_id <> OLD.doctor_id) THEN
    SELECT COUNT(*) INTO slot_taken FROM appointments
      WHERE doctor_id = NEW.doctor_id
        AND appointment_date = NEW.appointment_date
        AND appointment_time = NEW.appointment_time
        AND status NOT IN ('Declined', 'Completed', 'Cancelled')
        AND appointment_id <> NEW.appointment_id;
    IF slot_taken > 0 THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'This doctor already has an appointment at that date and time.';
    END IF;
  END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `audit_log`
--

CREATE TABLE `audit_log` (
  `log_id` int(11) NOT NULL,
  `actor_type` varchar(20) NOT NULL,
  `actor_id` int(11) DEFAULT NULL,
  `action` varchar(100) NOT NULL,
  `details` text DEFAULT NULL,
  `ip_address` varchar(64) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `audit_log`
--

INSERT INTO `audit_log` (`log_id`, `actor_type`, `actor_id`, `action`, `details`, `ip_address`, `created_at`) VALUES
(77, 'patient', 9, 'appointment_booked', 'Appointment #55 booked with Dr. Alice Mutiso on 2026-08-02 at 09:40.', '127.0.0.1', '2026-08-02 05:39:05'),
(78, 'patient', 11, 'appointment_booked', 'Appointment #56 booked with Dr. Alice Mutiso on 2026-08-03 at 09:40.', '127.0.0.1', '2026-08-02 05:40:59'),
(79, 'patient', 10, 'appointment_booked', 'Appointment #57 booked with Dr. Brian Maina on 2026-08-03 at 09:40.', '127.0.0.1', '2026-08-02 05:42:15'),
(80, 'doctor', 23, 'appointment_confirmed', 'Appointment #56 set to Confirmed.', '127.0.0.1', '2026-08-02 05:43:17'),
(81, 'doctor', 23, 'appointment_completed', 'Appointment #56 set to Completed. Reason: done', '127.0.0.1', '2026-08-02 05:43:29'),
(82, 'doctor', 23, 'appointment_confirmed', 'Appointment #55 set to Confirmed.', '127.0.0.1', '2026-08-02 05:43:37'),
(83, 'doctor', 23, 'appointment_completed', 'Appointment #55 set to Completed. Reason: done', '127.0.0.1', '2026-08-02 05:43:47'),
(84, 'doctor', 19, 'appointment_confirmed', 'Appointment #57 set to Confirmed.', '127.0.0.1', '2026-08-02 05:45:05'),
(85, 'doctor', 19, 'appointment_completed', 'Appointment #57 set to Completed. Reason: done', '127.0.0.1', '2026-08-02 05:45:33'),
(86, 'patient', 9, 'appointment_booked', 'Appointment #58 booked with Dr. Alice Mutiso on 2026-08-11 at 09:40.', '127.0.0.1', '2026-08-02 05:50:10'),
(87, 'patient', 11, 'appointment_booked', 'Appointment #59 booked with Dr. Alice Mutiso on 2026-08-12 at 09:40.', '127.0.0.1', '2026-08-02 05:51:59'),
(88, 'patient', 10, 'appointment_booked', 'Appointment #60 booked with Dr. Brian Maina on 2026-08-12 at 09:40.', '127.0.0.1', '2026-08-02 05:53:36'),
(89, 'doctor', NULL, 'failed_login', 'Failed doctor login attempt for email: alicemutiso@gmail.com', '127.0.0.1', '2026-08-02 05:55:11'),
(90, 'doctor', 23, 'appointment_confirmed', 'Appointment #59 set to Confirmed.', '127.0.0.1', '2026-08-02 05:55:41'),
(91, 'doctor', 23, 'appointment_completed', 'Appointment #59 set to Completed. Reason: done', '127.0.0.1', '2026-08-02 05:55:55'),
(92, 'doctor', 23, 'appointment_confirmed', 'Appointment #58 set to Confirmed.', '127.0.0.1', '2026-08-02 05:56:02'),
(93, 'doctor', 23, 'appointment_completed', 'Appointment #58 set to Completed. Reason: done', '127.0.0.1', '2026-08-02 05:56:13'),
(94, 'doctor', 19, 'appointment_confirmed', 'Appointment #60 set to Confirmed.', '127.0.0.1', '2026-08-02 05:57:02'),
(95, 'doctor', 19, 'appointment_completed', 'Appointment #60 set to Completed. Reason: done', '127.0.0.1', '2026-08-02 05:57:11'),
(96, 'doctor', NULL, 'failed_login', 'Failed doctor login attempt for email: alicemutiso@gmail.com', '127.0.0.1', '2026-08-02 10:58:00'),
(97, 'doctor', 23, 'appointment_confirmed', 'Appointment #61 set to Confirmed.', '127.0.0.1', '2026-08-02 11:10:27'),
(98, 'doctor', 23, 'appointment_completed', 'Appointment #61 set to Completed. Reason: continue with your dosage', '127.0.0.1', '2026-08-02 11:11:11'),
(99, 'admin', 1, 'admin_login', 'Admin \'System Admin\' logged in.', '127.0.0.1', '2026-08-02 11:17:22'),
(100, 'admin', 1, 'admin_generated_patients_report', 'All-patients report generated.', '127.0.0.1', '2026-08-02 11:18:15'),
(101, 'admin', 1, 'admin_generated_appointments_report', 'Appointments report generated for 2026-08-02 to 2026-08-31.', '127.0.0.1', '2026-08-02 11:27:17'),
(102, 'admin', 1, 'admin_generated_appointments_report', 'Appointments report generated for 2026-08-02 to 2026-08-31.', '127.0.0.1', '2026-08-02 11:27:45'),
(103, 'admin', 1, 'admin_generated_doctors_report', 'All-doctors report generated.', '127.0.0.1', '2026-08-02 12:12:15'),
(104, 'admin', 1, 'admin_generated_patients_report', 'All-patients report generated.', '127.0.0.1', '2026-08-02 12:12:26'),
(105, 'admin', 1, 'admin_generated_appointments_report', 'Appointments report generated for 2026-08-02 to 2026-08-31.', '127.0.0.1', '2026-08-02 12:12:59'),
(106, 'patient', 10, 'appointment_booked', 'Appointment #62 booked with Dr. Alex  peter on 2026-08-17 at 11:00.', '127.0.0.1', '2026-08-02 12:20:56'),
(107, 'doctor', 6, 'appointment_confirmed', 'Appointment #62 set to Confirmed.', '127.0.0.1', '2026-08-02 12:23:23'),
(108, 'doctor', 6, 'appointment_completed', 'Appointment #62 set to Completed.', '127.0.0.1', '2026-08-02 12:23:57'),
(109, 'doctor', 6, 'referral_created', 'Referred patient #10 to doctor #28. Reason: needs screening machines', '127.0.0.1', '2026-08-02 12:24:45'),
(110, 'doctor', 28, 'referral_accepted', 'Referral #11 accepted.', '127.0.0.1', '2026-08-02 12:27:14'),
(111, 'doctor', 28, 'referral_scheduled', 'Referral #11 scheduled as appointment #63 on 2026-08-10 at 11:00.', '127.0.0.1', '2026-08-02 12:29:16'),
(112, 'doctor', 28, 'appointment_completed', 'Appointment #63 set to Completed. Reason: ok', '127.0.0.1', '2026-08-02 12:34:46'),
(113, 'admin', 1, 'admin_login', 'Admin \'System Admin\' logged in.', '127.0.0.1', '2026-08-02 12:35:48'),
(114, 'admin', 1, 'admin_generated_referrals_report', 'All-referrals report generated.', '127.0.0.1', '2026-08-02 12:35:59'),
(115, 'admin', 1, 'admin_generated_doctors_report', 'All-doctors report generated.', '127.0.0.1', '2026-08-02 12:36:14'),
(116, 'admin', 1, 'doctor_removed', 'Admin \'System Admin\' removed Dr. william Thomas (williamthomas@gmail.com).', '127.0.0.1', '2026-08-02 12:39:45'),
(117, 'admin', 1, 'admin_generated_doctors_report', 'All-doctors report generated.', '127.0.0.1', '2026-08-02 12:39:54'),
(118, 'admin', 1, 'admin_generated_patients_report', 'All-patients report generated.', '127.0.0.1', '2026-08-02 12:40:01'),
(119, 'patient', 12, 'patient_registered', 'New patient registered: Benjamin maina (benjaminmaina@gmail.com)', '127.0.0.1', '2026-08-02 12:44:16'),
(120, 'doctor', 30, 'doctor_registered', 'New doctor registered: irene maina (irenemaina@gmail.com)', '127.0.0.1', '2026-08-02 12:52:25'),
(121, 'admin', 1, 'admin_login', 'Admin \'System Admin\' logged in.', '127.0.0.1', '2026-08-03 07:12:56'),
(122, 'admin', 1, 'admin_generated_doctors_report', 'All-doctors report generated.', '127.0.0.1', '2026-08-03 07:13:41'),
(123, 'patient', 11, 'appointment_booked', 'Appointment #64 booked with Dr. Alice Mutiso on 2026-08-17 at 11:00.', '127.0.0.1', '2026-08-16 01:59:53'),
(124, 'patient', 9, 'appointment_booked', 'Appointment #65 booked with Dr. Brian Maina on 2026-08-16 at 09:00.', '127.0.0.1', '2026-08-16 02:33:17'),
(125, 'patient', 9, 'appointment_booked', 'Appointment #66 booked with Dr. Alice Mutiso on 2026-08-24 at 14:20.', '127.0.0.1', '2026-08-24 10:14:41'),
(126, 'doctor', 23, 'appointment_confirmed', 'Appointment #66 set to Confirmed.', '127.0.0.1', '2026-08-25 21:02:29'),
(127, 'doctor', 23, 'appointment_completed', 'Appointment #66 set to Completed. Reason: please avail', '127.0.0.1', '2026-08-25 21:03:07'),
(128, 'doctor', 23, 'appointment_declined', 'Appointment #64 set to Declined. Reason: not feeling well i was attending another doc but i canreffer you to another dentist', '127.0.0.1', '2026-08-25 21:04:53'),
(129, 'doctor', 23, 'appointment_confirmed', 'Appointment #67 set to Confirmed.', '127.0.0.1', '2026-08-25 21:15:55'),
(130, 'doctor', 23, 'appointment_completed', 'Appointment #67 set to Completed. Reason: take dosage properly', '127.0.0.1', '2026-08-25 21:19:44'),
(131, 'patient', 9, 'appointment_booked', 'Appointment #68 booked with Dr. Emilly mathew on 2026-10-03 at 10:20.', '127.0.0.1', '2026-09-23 04:01:02'),
(132, 'admin', 1, 'admin_login', 'Admin \'System Admin\' logged in.', '127.0.0.1', '2026-09-23 04:07:04'),
(133, 'admin', 1, 'admin_login', 'Admin \'System Admin\' logged in.', '127.0.0.1', '2026-10-02 09:35:04'),
(134, 'admin', 1, 'admin_generated_doctors_report', 'All-doctors report generated.', '127.0.0.1', '2026-10-02 09:40:39'),
(135, 'admin', 1, 'admin_generated_doctors_report', 'All-doctors report generated.', '127.0.0.1', '2026-10-02 09:49:12'),
(136, 'admin', NULL, 'failed_login', 'Failed admin login attempt for email: admin@docconnect.com', '127.0.0.1', '2026-10-15 08:43:19'),
(137, 'admin', 1, 'admin_login', 'Admin \'System Admin\' logged in.', '127.0.0.1', '2026-10-15 08:43:55'),
(138, 'admin', 1, 'admin_generated_doctors_report', 'All-doctors report generated.', '127.0.0.1', '2026-10-15 08:44:07'),
(139, 'admin', 1, 'admin_generated_patients_report', 'All-patients report generated.', '127.0.0.1', '2026-10-15 08:45:25'),
(140, 'doctor', 19, 'appointment_confirmed', 'Appointment #65 set to Confirmed.', '127.0.0.1', '2026-10-15 08:58:07'),
(141, 'doctor', 19, 'appointment_completed', 'Appointment #65 set to Completed. Reason: keep time', '127.0.0.1', '2026-10-15 08:58:25'),
(142, 'admin', NULL, 'failed_login', 'Failed admin login attempt for email: admin@doccconect.com', '127.0.0.1', '2026-10-15 09:00:31'),
(143, 'admin', 1, 'admin_login', 'Admin \'System Admin\' logged in.', '127.0.0.1', '2026-10-15 09:01:58'),
(144, 'admin', 1, 'admin_login', 'Admin \'System Admin\' logged in.', '127.0.0.1', '2026-10-15 09:24:07'),
(145, 'admin', 1, 'admin_login', 'Admin \'System Admin\' logged in.', '127.0.0.1', '2026-10-15 09:39:24'),
(146, 'admin', 1, 'admin_generated_doctors_report', 'All-doctors report generated.', '127.0.0.1', '2026-10-15 10:46:50'),
(147, 'admin', 1, 'admin_login', 'Admin \'System Admin\' logged in.', '127.0.0.1', '2026-10-15 11:16:45'),
(148, 'admin', 1, 'admin_generated_doctors_report', 'All-doctors report generated.', '127.0.0.1', '2026-10-15 11:16:57'),
(149, 'admin', 1, 'admin_login', 'Admin \'System Admin\' logged in.', '127.0.0.1', '2026-10-16 09:19:14'),
(150, 'doctor', NULL, 'failed_login', 'Failed doctor login attempt for email: brianmaina@gmail.com', '127.0.0.1', '2026-10-16 09:22:23'),
(151, 'admin', 1, 'admin_generated_doctors_report', 'All-doctors report generated.', '127.0.0.1', '2026-10-16 09:24:44'),
(152, 'doctor', NULL, 'failed_login', 'Failed doctor login attempt for email: brianmaina@gmail.com', '127.0.0.1', '2026-10-16 09:26:30'),
(153, 'patient', 9, 'appointment_booked', 'Appointment #69 booked with Dr. Alex  peter on 2026-10-18 at 09:40.', '127.0.0.1', '2026-10-17 06:50:00'),
(154, 'patient', 9, 'appointment_booked', 'Appointment #70 booked with Dr. Samuel Karanja on 2026-10-19 at 11:00.', '127.0.0.1', '2026-10-17 07:19:15'),
(155, 'patient', 11, 'appointment_booked', 'Appointment #71 booked with Dr. Susan Musyoka on 2026-10-21 at 15:00.', '127.0.0.1', '2026-10-17 07:25:24');

-- --------------------------------------------------------

--
-- Table structure for table `doctors`
--

CREATE TABLE `doctors` (
  `doctor_id` int(11) NOT NULL,
  `firstname` varchar(100) NOT NULL,
  `middlename` text DEFAULT NULL,
  `surname` text NOT NULL,
  `business_phone` varchar(20) NOT NULL,
  `personal_phone` varchar(20) NOT NULL,
  `email` varchar(150) NOT NULL,
  `gender` enum('Male','Female') NOT NULL,
  `county` text NOT NULL,
  `address` varchar(255) NOT NULL,
  `speciality` varchar(100) NOT NULL,
  `profile_description` text DEFAULT NULL,
  `id_number` int(20) NOT NULL,
  `language` text DEFAULT NULL,
  `profile_photo` varchar(255) DEFAULT NULL,
  `consultation_fee` decimal(10,2) NOT NULL DEFAULT 100.00,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `doctors`
--

INSERT INTO `doctors` (`doctor_id`, `firstname`, `middlename`, `surname`, `business_phone`, `personal_phone`, `email`, `gender`, `county`, `address`, `speciality`, `profile_description`, `id_number`, `language`, `profile_photo`, `password`, `created_at`) VALUES
(1, 'Clare', 'kate', 'olivia', '254745131917', '254729225710', 'clareolivia@gmail.com', 'Female', 'Mombasa', 'NyaliBuiliding,3rd Fllor,rm 5', 'ENT Specialist', 'Dr clare olivia is an ear, nose, and throat specialist with expertise in diagnosing and treating ENT disorders in both adults and children. She manages hearing problems, sinus diseases, throat infections, allergies, and voice disorders using evidence-based treatment methods. She believes in delivering compassionate, patient-focused care while maintaining high clinical standards. Her commitment to continuous learning allows her to provide modern and effective treatment options. She is dedicated to improving the quality of life of every patient through comprehensive ENT healthcare.', 56456353, 'English,Swahil, French', 'picture3w.jpg', '123456', '2026-06-27 09:17:49'),
(2, 'Emilly', 'jessica', 'mathew', '0790061452', '254729225710', 'emillymathew@gmail.com', 'Female', 'Kiambu', 'nairobi,moi avenue', 'Dermatologist', 'A highly experienced dermatologist dedicated to diagnosing, treating, and preventing a wide range of skin, hair, and nail conditions. With more than 12 years of clinical experience, this specialist provides comprehensive care for patients of all ages, managing conditions such as acne, eczema, psoriasis, dermatitis, fungal infections, skin allergies, pigmentation disorders, and hair loss. Every treatment plan is tailored to the patient\'s unique needs, ensuring effective and long-lasting results.\n\nPassionate about promoting healthy skin, this dermatologist emphasizes preventive care, patient education, and early detection of skin diseases. Patients receive practical guidance on skincare routines, sun protection, and lifestyle habits that contribute to overall skin health. By combining evidence-based medical practices with a compassionate approach, every consultation is designed to make patients feel comfortable, informed, and actively involved in their treatment.\n\nCommitted to continuous professional development, this specialist stays current with the latest advances in dermatology, modern diagnostic techniques, and innovative treatment options. Known for being approachable, attentive, and detail-oriented, the focus is always on delivering high-quality care while building trust and confidence with every patient. Whether addressing chronic skin conditions, performing routine skin assessments, or offering preventive advice, the goal is to improve both skin health and overall quality of life through personalized, professional care.\n', 38520185, 'English,Swahil, French', 'picture6w.jpg', '123456', '2026-06-27 09:44:19'),
(6, 'Alex ', 'henry', 'peter', '0712345678', '0709098787', 'alexpeter@gmail.com', 'Male', 'Nyeri', 'nyeri house ,2nd floor', 'Urologist', 'A highly skilled urologist dedicated to diagnosing, treating, and managing conditions affecting the urinary tract and the male reproductive system. With extensive clinical experience, this specialist provides comprehensive care for patients experiencing kidney stones, urinary tract infections (UTIs), bladder disorders, prostate conditions, urinary incontinence, erectile dysfunction, and other urological concerns. Each patient receives a thorough evaluation and a personalized treatment plan designed to achieve the best possible outcomes.\n\nCommitted to delivering compassionate, patient-centered care, this urologist emphasizes early diagnosis, preventive health, and patient education. Every consultation includes clear explanations of medical conditions, treatment options, and lifestyle recommendations to help patients make informed decisions about their health. Modern diagnostic tools and evidence-based treatment approaches are used to ensure accurate diagnoses and effective management of both common and complex urological conditions.\n\nDedicated to continuous professional development, this specialist stays up to date with the latest advancements in urology, including minimally invasive procedures and modern surgical techniques. Known for professionalism, empathy, and attention to detail, the focus is on creating a comfortable and confidential environment where patients feel respected and supported. Whether providing routine urological evaluations, managing chronic conditions, or performing specialized procedures, the goal is to improve urinary health, restore function, and enhance the overall quality of life for every patient.\n', 363580, 'english,swahili', 'picture2m.jpg', '123456', '2026-06-27 17:34:16'),
(7, 'josphine', 'joyce', 'usuf', '0722601867', '0721617766', 'josphineusuf@gmail.com', 'Male', 'Uasin Gishu', 'uasin gishu town,5th floor', 'Cardiologist', 'A highly experienced cardiologist dedicated to the prevention, diagnosis, and treatment of diseases affecting the heart and blood vessels. With years of clinical expertise, this specialist provides comprehensive care for patients with conditions such as hypertension, coronary artery disease, heart failure, irregular heart rhythms (arrhythmias), high cholesterol, and other cardiovascular disorders. Every patient receives a detailed assessment and a personalized treatment plan tailored to their specific health needs and lifestyle.\n\nCommitted to promoting heart health, this cardiologist emphasizes preventive care through regular screenings, early diagnosis, and patient education. Patients are guided on maintaining a heart-healthy lifestyle by adopting balanced nutrition, regular physical activity, stress management, and effective management of risk factors such as diabetes and high blood pressure. The goal is to prevent complications and improve long-term cardiovascular health.\n\nBy combining modern diagnostic techniques with evidence-based treatment approaches, this specialist ensures accurate diagnosis and effective management of both acute and chronic heart conditions. Dedicated to continuous professional development, the cardiologist remains up to date with the latest advancements in cardiovascular medicine and treatment technologies. Known for a compassionate and patient-centered approach, every consultation is conducted in a supportive and respectful environment where patients feel comfortable discussing their concerns. The ultimate goal is to improve heart function, enhance quality of life, and help patients achieve lasting cardiovascular wellness through personalized, high-quality medical care.\n', 87654321, 'english', 'picture8w.jpg', '123456', '2026-06-27 17:49:22'),
(10, 'mercy', 'irene', 'ethan', '0798989876', '0721617766', 'mercyethan@gmail.com', 'Female', 'Machakos', 'mbewa house,2nd floor', 'Gynecologist', 'A compassionate and experienced gynecologist dedicated to providing comprehensive healthcare for women at every stage of life. This specialist focuses on the prevention, diagnosis, and treatment of conditions affecting the female reproductive system, including menstrual disorders, pelvic pain, hormonal imbalances, ovarian cysts, uterine fibroids, infections, infertility, and menopause-related concerns. Each patient receives individualized care tailored to their unique health needs and personal circumstances.\n\nCommitted to promoting women\'s health, this gynecologist emphasizes preventive care through routine examinations, cervical cancer screening, breast health awareness, family planning, and reproductive health education. Patients are encouraged to ask questions and actively participate in decisions regarding their care, ensuring they feel informed, respected, and supported throughout every consultation.\n\nUsing modern diagnostic techniques and evidence-based medical practices, this specialist provides accurate diagnoses and effective treatment options for both common and complex gynecological conditions. Dedicated to continuous professional development, the gynecologist stays current with the latest advances in women\'s healthcare to deliver the highest standard of care. Known for a caring, respectful, and professional approach, the goal is to create a safe and comfortable environment where patients can discuss sensitive health concerns with confidence. Through personalized treatment, preventive care, and ongoing support, this specialist strives to improve reproductive health, overall well-being, and quality of life for every patient.\n', 34343434, 'english,kiswahili', 'doc10w.jfif', '123456', '2026-06-27 18:02:43'),
(11, 'fred', 'jacob', 'shekh', '0712231232', '0789765643', 'fredshekh@gmail.com', 'Male', 'Meru', 'meru house,1st floor', 'Radiologist', 'A highly skilled radiologist specializing in the use of advanced medical imaging to diagnose and monitor a wide range of diseases and injuries. With extensive experience in interpreting X-rays, ultrasound scans, computed tomography (CT) scans, magnetic resonance imaging (MRI), and other diagnostic imaging techniques, this specialist plays a vital role in supporting accurate diagnoses and effective treatment planning. Every imaging study is carefully reviewed to provide detailed and reliable findings that assist healthcare providers in delivering the best possible patient care.\n\nCommitted to accuracy and excellence, this radiologist works closely with physicians and other medical specialists to ensure timely diagnosis and appropriate management of various medical conditions, including fractures, tumors, infections, cardiovascular diseases, neurological disorders, and abdominal abnormalities. Great attention is given to maintaining high standards of patient safety while utilizing modern imaging technology and evidence-based practices.\n\nDedicated to continuous professional development, this specialist remains up to date with the latest advancements in diagnostic imaging, image-guided procedures, and radiological techniques. Known for professionalism, precision, and attention to detail, the focus is on delivering high-quality diagnostic services that contribute to better patient outcomes. By combining technical expertise with a commitment to compassionate healthcare, this radiologist helps ensure that patients receive accurate diagnoses and effective treatment recommendations in a timely and efficient manner.\n', 87878787, 'english', 'picture5m.jpg', '123456', '2026-07-04 07:39:58'),
(12, 'liam', 'jack', 'oliver', '0716123443', '0721212132', 'liamoliver@gmail.com', 'Male', 'Mombasa', 'P.O. Box 45892–80100, Mombasa, Kenya Moi Avenue, Mvita Mombasa County, Kenya', 'Neurologist', 'A highly experienced neurologist dedicated to diagnosing, treating, and managing disorders of the brain, spinal cord, nerves, and muscles. With extensive clinical expertise, this specialist provides comprehensive care for patients with conditions such as stroke, epilepsy, migraines, Parkinson’s disease, multiple sclerosis, dementia, neuropathy, and other neurological disorders. Every patient receives a thorough evaluation, accurate diagnosis, and a personalized treatment plan designed to improve neurological function and overall quality of life.\r\n\r\nCommitted to patient-centered care, this neurologist emphasizes early diagnosis, preventive strategies, and ongoing management of both acute and chronic neurological conditions. Patients are provided with clear explanations of their condition, available treatment options, and practical lifestyle recommendations to help them better understand and manage their health. A compassionate and supportive approach ensures that every patient feels comfortable discussing their symptoms and concerns.\r\n\r\nUsing advanced diagnostic techniques and evidence-based medical practices, this specialist collaborates closely with other healthcare professionals to deliver coordinated and effective care. Dedicated to continuous professional development, the neurologist stays informed about the latest advancements in neurological research, diagnostic technology, and treatment methods. Known for professionalism, attention to detail, and compassionate care, the goal is to help patients achieve the best possible outcomes, preserve neurological function, and enhance their overall well-being through personalized, high-quality medical care.\r\n', 12121212, 'english,kiswahili', 'picture10m.jpg', '123456', '2026-07-06 07:26:35'),
(13, 'James', 'Mwangi', 'Kamau', '0201001001', '0712345001', 'jameskamau@gmail.co', 'Male', 'Nairobi', 'Westlands', 'Cardiologist', 'Dr. James Kamau is a consultant cardiologist with over twelve years of experience diagnosing and treating heart diseases. He has managed patients with hypertension, heart failure, arrhythmias, and coronary artery disease using evidence-based clinical practices. He is passionate about preventive cardiology and regularly educates patients on healthy lifestyles to reduce cardiovascular risks. His approach emphasizes compassion, accurate diagnosis, and personalized treatment plans for every patient. He is committed to providing quality cardiac care while supporting research and mentoring upcoming healthcare professionals.', 32547891, 'English, Swahili', 'man1.webp', '123456', '2026-08-01 10:07:47'),
(14, 'Mercy', 'Wanjiku', 'Njeri', '0201001002', '0712345002', 'mercynjeri@gmail.com', 'Female', 'Kiambu', 'Thika', 'Dermatologist', 'Dr. Mercy Njeri is a highly experienced dermatologist specializing in skin, hair, and nail disorders. She has successfully treated acne, eczema, psoriasis, fungal infections, and various allergic skin conditions for patients of all ages. She combines modern medical treatments with patient education to promote long-term skin health and confidence. Her clinic emphasizes accurate diagnosis, preventive care, and individualized treatment strategies. She continuously updates her knowledge through professional training and participation in dermatology conferences.', 32547892, 'English, Swahili', 'woman1.webp', '123456', '2026-08-01 10:07:47'),
(15, 'Peter', 'Otieno', 'Odhiambo', '0201001003', '0712345003', 'peterodhiambo@gmail.com', 'Male', 'Kisumu', 'Milimani', 'Neurologist', 'Dr. Peter Odhiambo is a neurologist with extensive experience managing disorders affecting the brain, spinal cord, and nervous system. His expertise includes stroke management, epilepsy, migraines, Parkinson’s disease, and multiple sclerosis. He believes in combining advanced diagnostic technology with compassionate patient care to improve treatment outcomes. He works closely with multidisciplinary teams to develop comprehensive rehabilitation plans. His dedication to neurological research ensures his patients benefit from current evidence-based medical practices.', 32547893, 'English, Swahili', 'man2.webp', '123456', '2026-08-01 10:07:47'),
(16, 'Grace', 'Achieng', 'Atieno', '0201001004', '0712345004', 'graceatieno@gmail.com', 'Female', 'Mombasa', 'Nyali', 'Pediatrician', 'Dr. Grace Atieno is a pediatrician committed to improving the health and well-being of infants, children, and adolescents. She provides preventive healthcare, immunization services, nutritional guidance, and treatment for common childhood illnesses. She believes that involving parents in medical decision-making leads to better health outcomes for children. Her friendly and reassuring approach helps young patients feel comfortable during consultations. She remains dedicated to promoting child health through education, research, and community outreach.', 32547894, 'English, Swahili', 'woman2.webp', '123456', '2026-08-01 10:07:47'),
(17, 'David', 'Kiprono', 'Chebet', '0201001005', '0712345005', 'davidchebet@gmail.co', 'Male', 'Uasin Gishu', 'Eldoret', 'Orthopedic Surgeon', 'Dr. David Chebet is an orthopedic surgeon specializing in the treatment of bone, joint, ligament, and muscle conditions. He has performed numerous successful procedures involving fractures, sports injuries, and joint replacement surgeries. He prioritizes restoring mobility while minimizing recovery time through modern surgical techniques. He also advises patients on injury prevention and long-term musculoskeletal health. His commitment to excellence has earned him the trust of patients across the region.', 32547895, 'English, Swahili', 'man3.webp', '123456', '2026-08-01 10:07:47'),
(18, 'Susan', 'Mutheu', 'Musyoka', '0201001006', '0712345006', 'susanmusyoka@gmail.com', 'Female', 'Machakos', 'Machakos Town', 'Gynecologist', 'Dr. Susan Musyoka is a gynecologist dedicated to providing comprehensive healthcare services for women of all ages. She specializes in reproductive health, antenatal care, fertility management, and minimally invasive gynecological procedures. She values patient privacy and believes in empowering women through education and preventive healthcare. Her compassionate communication style encourages patients to discuss sensitive health concerns openly. She strives to improve women’s health through high-quality clinical care and continuous professional development.', 32547896, 'English, Swahili', 'woman3.webp', '123456', '2026-08-01 10:07:47'),
(19, 'Brian', 'Kimani', 'Maina', '0201001007', '0712345007', 'brianmaina@gmail.com', 'Male', 'Nakuru', 'Nakuru Town', 'Psychiatrist', 'Dr. Brian Maina is a psychiatrist with extensive experience treating anxiety disorders, depression, bipolar disorder, and stress-related conditions. He provides confidential psychiatric assessments, counseling, psychotherapy, and medication management tailored to individual patient needs. He advocates for reducing mental health stigma through education and community awareness initiatives. His patient-centered approach promotes trust, empathy, and long-term emotional well-being. He is passionate about helping individuals achieve healthier and more productive lives.', 32547897, 'English, Swahili', 'man4.jpg', '123456', '2026-08-01 10:07:47'),
(20, 'Faith', 'Chepkemoi', 'Koech', '0201001008', '0712345008', 'faithkoech@gmail.com', 'Female', 'Kericho', 'Kericho Town', 'Ophthalmologist', 'Dr. Faith Koech is an ophthalmologist specializing in the diagnosis and treatment of eye diseases and vision disorders. She manages cataracts, glaucoma, diabetic eye disease, and refractive errors using modern diagnostic equipment. She believes early detection and routine eye examinations are essential for preserving vision throughout life. Her commitment to patient education ensures individuals understand their treatment options and preventive measures. She continues to advance her expertise through ongoing clinical training and research.', 32547898, 'English, Swahili', 'woman4.jpg', '123456', '2026-08-01 10:07:47'),
(21, 'Samuel', 'Muriithi', 'Karanja', '0201001009', '0712345009', 'samuelkaranja@gmail.com', 'Male', 'Nyeri', 'Nyeri Town', 'General Surgeon', 'Dr. Samuel Karanja is a general surgeon experienced in performing both emergency and elective surgical procedures. His areas of expertise include abdominal surgery, laparoscopic surgery, hernia repair, and gastrointestinal conditions. He follows internationally recognized surgical standards to ensure patient safety and successful recovery. He works collaboratively with other healthcare professionals to provide comprehensive perioperative care. His dedication to surgical excellence has earned him respect among colleagues and patients alike.', 32547899, 'English, Swahili', 'man5.jpg', '123456', '2026-08-01 10:07:47'),
(22, 'Lydia', 'Chebet', 'kosgei', '0201001010', '0712345010', 'lydiakosgei@gmail.com', 'Female', 'Meru', 'Meru Town', 'ENT Specialist', 'Dr. Lydia Jepkosgei is an ear, nose, and throat specialist with expertise in diagnosing and treating ENT disorders in both adults and children. She manages hearing problems, sinus diseases, throat infections, allergies, and voice disorders using evidence-based treatment methods. She believes in delivering compassionate, patient-focused care while maintaining high clinical standards. Her commitment to continuous learning allows her to provide modern and effective treatment options. She is dedicated to improving the quality of life of every patient through comprehensive ENT healthcare.', 32547900, 'English, Swahili', 'woman5.webp', '123456', '2026-08-01 10:07:47'),
(23, 'Alice', 'Wanjiru', 'Mutiso', '0201001011', '0712345011', 'alicemutiso@gmail.com', 'Female', 'Nairobi', 'Kilimani', 'Dentist', 'Dr. Alice Mutiso is a highly qualified dental surgeon dedicated to providing comprehensive oral healthcare for patients of all ages. She specializes in preventive dentistry, cosmetic dental procedures, tooth restoration, and gum disease treatment using modern dental technology. She believes that patient education and regular dental check-ups are essential in preventing serious oral health conditions. Her calm and friendly approach helps patients overcome anxiety and feel comfortable during every procedure. She continuously participates in professional development programs to remain updated with the latest techniques in restorative and cosmetic dentistry. Her goal is to improve every patient\'s smile while promoting lifelong oral health and confidence.', 32547901, 'English, Swahili', 'woman6.jpg', '123456', '2026-08-01 11:22:37'),
(24, 'Linda', 'Chebet', 'Kiptoo', '0201001012', '0712345012', 'lindakiptoo@gmail.com', 'Female', 'Uasin Gishu', 'Eldoret', 'Gynecologist', 'Dr. Linda Kiptoo is an experienced gynecologist committed to providing quality reproductive healthcare to women throughout every stage of life. She specializes in antenatal care, fertility assessment, family planning, and the treatment of gynecological disorders using evidence-based medical practices. She values patient privacy and believes in creating a comfortable environment where women can openly discuss their health concerns. She works closely with multidisciplinary healthcare teams to provide personalized treatment plans and improve maternal health outcomes. Through continuous medical education and research, she ensures her patients receive modern, safe, and compassionate care. Her dedication has earned her the trust and respect of both patients and colleagues.', 32547902, 'English, Swahili', 'woman7.jpg', '123456', '2026-08-01 11:22:37'),
(25, 'Kevin', 'Mwangi', 'Njoroge', '0201001013', '0712345013', 'kelvinnjoroge@gmail.com', 'Male', 'Kiambu', 'Ruiru', 'Dermatologist', 'Dr. Kevin Njoroge is a consultant dermatologist with extensive experience diagnosing and treating a wide range of skin, hair, and nail disorders. He provides specialized care for acne, eczema, psoriasis, skin allergies, fungal infections, and cosmetic skin concerns using advanced treatment methods. He believes in combining accurate diagnosis with personalized treatment plans to achieve lasting improvements for every patient. He regularly educates patients on proper skincare routines and preventive measures that support healthy skin throughout life. His commitment to research and continuous professional development enables him to deliver high-quality dermatological services. He is passionate about helping patients regain confidence through healthier skin.', 32547903, 'English, Swahili', 'man6.webp', '123456', '2026-08-01 11:22:37'),
(26, 'Michael', 'Ochieng', 'Otieno', '0201001014', '0712345014', 'michaelotieno@gmail.com', 'Male', 'Kisumu', 'Milimani', 'Radiologist', 'Dr. Michael Otieno is an experienced radiologist specializing in diagnostic imaging and image-guided medical procedures. He interprets X-rays, CT scans, MRI scans, ultrasound examinations, and other imaging studies with exceptional accuracy to support effective diagnosis and treatment. He collaborates closely with physicians from different specialties to ensure patients receive timely and appropriate medical care. He remains committed to maintaining high standards of patient safety while utilizing modern imaging technologies. Through ongoing training and professional development, he continues to improve his expertise in advanced radiological techniques. His dedication contributes significantly to early disease detection and better patient outcomes.', 32547904, 'English, Swahili', 'man7.webp', '123456', '2026-08-01 11:22:37'),
(27, 'Janet', 'Akinyi', 'Owino', '0201001015', '0712345015', 'janetowino@gmail.com', 'Female', 'Kisumu', 'Tom Mboya Estate', 'Psychiatrist', 'Dr. Janet Owino is a psychiatrist dedicated to promoting mental wellness through compassionate and evidence-based psychiatric care. She provides assessment, counseling, psychotherapy, and medication management for patients experiencing depression, anxiety, trauma, bipolar disorder, and other mental health conditions. She believes in treating every patient with dignity while encouraging family involvement whenever appropriate. She actively supports mental health awareness programs aimed at reducing stigma within communities and improving access to psychological care. Her patient-centered approach focuses on building trust and creating individualized treatment plans that promote long-term recovery. She continues to expand her knowledge through research and continuous professional education.', 32547905, 'English, Swahili', 'woman8.jpg', '123456', '2026-08-01 11:22:37'),
(28, 'Daniel', 'Kiplangat', 'ruto', '0201001016', '0712345016', 'danielruto@gmail.com', 'Male', 'Nakuru', 'Nakuru Town', 'Urologist', 'Dr. Daniel Cheruiyot is a consultant urologist with extensive experience in diagnosing and treating disorders affecting the urinary tract and male reproductive system. He manages kidney stones, urinary tract infections, prostate conditions, bladder disorders, and male infertility using modern diagnostic and surgical techniques. He believes in providing confidential, respectful, and patient-focused healthcare tailored to individual medical needs. He works collaboratively with other specialists to deliver comprehensive treatment and improve patient outcomes. He regularly participates in medical conferences and research activities to remain current with advancements in urological care. His commitment to excellence has earned him recognition as a trusted healthcare professional.', 32547906, 'English, Swahili', 'man9.webp', '123456', '2026-08-01 11:22:37'),
(30, 'irene', 'wangui', 'maina', '0201232321', '0721617766', 'irenemaina@gmail.com', 'Female', 'Meru', 'meru,town', 'Gynecologist', 'Dr. irene wangui is a dedicated gynecologist with over 10 years of experience in women\'s reproductive health. She specializes in prenatal care, family planning, menstrual disorders, and the diagnosis and treatment of gynecological conditions. She is committed to providing compassionate, confidential, and patient-centered care for women of all ages. Dr. Wanjiru believes in educating patients so they can make informed decisions about their health and well-being. She is known for her professionalism, empathy, and commitment to improving the quality of life for every patient she serves.', 77777771, 'english,kiswahili', 'woman10.avif', '123456', '2026-08-02 12:52:25');

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `notification_id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `is_read` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`notification_id`, `patient_id`, `message`, `is_read`, `created_at`) VALUES
(111, 9, 'Your appointment with Dr. Alice Mutiso on 2026-08-02 at 09:40 has been booked and is Pending confirmation.', 1, '2026-08-02 05:39:05'),
(113, 10, 'Your appointment with Dr. Brian Maina on 2026-08-03 at 09:40 has been booked and is Pending confirmation.', 1, '2026-08-02 05:42:15'),
(114, 11, 'Your appointment with Dr. Alice Mutiso on 2026-08-03 at 09:40 is now: Confirmed.', 1, '2026-08-02 05:43:17'),
(115, 11, 'Your appointment with Dr. Alice Mutiso on 2026-08-03 at 09:40 is now: Completed. Reason: done', 1, '2026-08-02 05:43:29'),
(116, 9, 'Your appointment with Dr. Alice Mutiso on 2026-08-02 at 09:40 is now: Confirmed.', 1, '2026-08-02 05:43:37'),
(118, 10, 'Your appointment with Dr. Brian Maina on 2026-08-03 at 09:40 is now: Confirmed.', 1, '2026-08-02 05:45:05'),
(119, 10, 'Your appointment with Dr. Brian Maina on 2026-08-03 at 09:40 is now: Completed. Reason: done', 1, '2026-08-02 05:45:33'),
(121, 11, 'Your appointment with Dr. Alice Mutiso on 2026-08-12 at 09:40 has been booked and is Pending confirmation.', 1, '2026-08-02 05:51:59'),
(122, 10, 'Your appointment with Dr. Brian Maina on 2026-08-12 at 09:40 has been booked and is Pending confirmation.', 1, '2026-08-02 05:53:36'),
(123, 11, 'Your appointment with Dr. Alice Mutiso on 2026-08-12 at 09:40 is now: Confirmed.', 1, '2026-08-02 05:55:41'),
(124, 11, 'Your appointment with Dr. Alice Mutiso on 2026-08-12 at 09:40 is now: Completed. Reason: done', 1, '2026-08-02 05:55:55'),
(127, 10, 'Your appointment with Dr. Brian Maina on 2026-08-12 at 09:40 is now: Confirmed.', 1, '2026-08-02 05:57:02'),
(128, 10, 'Your appointment with Dr. Brian Maina on 2026-08-12 at 09:40 is now: Completed. Reason: done', 1, '2026-08-02 05:57:11'),
(129, 11, 'Dr. Alice Mutiso has set up a follow-up appointment for you on 2026-08-24 at 11:00.', 1, '2026-08-02 11:09:36'),
(130, 11, 'Your appointment with Dr. Alice Mutiso on 2026-08-24 at 11:00 is now: Confirmed.', 1, '2026-08-02 11:10:27'),
(132, 10, 'Your appointment with Dr. Alex  peter on 2026-08-17 at 11:00 has been booked and is Pending confirmation.', 1, '2026-08-02 12:20:56'),
(133, 10, 'Your appointment with Dr. Alex  peter on 2026-08-17 at 11:00 is now: Confirmed.', 0, '2026-08-02 12:23:23'),
(134, 10, 'Your appointment with Dr. Alex  peter on 2026-08-17 at 11:00 is now: Completed.', 0, '2026-08-02 12:23:57'),
(135, 10, 'Dr. Alex  peter has referred you to Dr. Daniel ruto. Reason: needs screening machines. Please book an appointment with Dr. Daniel ruto to continue your consultation.', 0, '2026-08-02 12:24:45'),
(136, 10, 'Dr. Daniel has accepted the referral from Dr. Alex  peter. You have been referred to Dr. Daniel. They will schedule your appointment shortly.', 0, '2026-08-02 12:27:14'),
(137, 10, 'Dr. Daniel has scheduled your referred appointment for 2026-08-10 at 11:00.', 0, '2026-08-02 12:29:16'),
(138, 10, 'Your appointment with Dr. Daniel ruto on 2026-08-10 at 11:00 is now: Completed. Reason: ok', 0, '2026-08-02 12:34:46'),
(139, 11, 'Your appointment with Dr. Alice Mutiso on 2026-08-17 at 11:00 has been booked and is Pending confirmation.', 1, '2026-08-16 01:59:53'),
(144, 11, 'Your appointment with Dr. Alice Mutiso on 2026-08-17 at 11:00 is now: Declined. Reason: not feeling well i was attending another doc but i canreffer you to another dentist', 1, '2026-08-25 21:04:53'),
(152, 9, 'Your appointment with Dr. Samuel Karanja on 2026-10-19 at 11:00 has been booked and is Pending confirmation.', 1, '2026-10-17 07:19:15'),
(153, 11, 'Your appointment with Dr. Susan Musyoka on 2026-10-21 at 15:00 has been booked and is Pending confirmation.', 1, '2026-10-17 07:25:24');

-- --------------------------------------------------------

--
-- Table structure for table `patients`
--

CREATE TABLE `patients` (
  `patient_id` int(11) NOT NULL,
  `firstname` varchar(100) NOT NULL,
  `lastname` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(100) NOT NULL,
  `address` varchar(255) NOT NULL,
  `county` varchar(100) NOT NULL,
  `dob` date DEFAULT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `patients`
--

INSERT INTO `patients` (`patient_id`, `firstname`, `lastname`, `email`, `phone`, `address`, `county`, `dob`, `password`) VALUES
(9, 'benson', 'maina', 'bensonmaina@gmail.com', '0790061452', 'meru', 'Mombasa', '2000-07-11', '909090'),
(10, 'mark', 'do', 'markdo@gmail.com', '0790061452', 'nyeri123', 'Nyeri', '2000-12-11', '909090'),
(11, 'mwangi', 'plus', 'mwangiplus@gmail.com', '0712345678', '00100', 'Kiambu', '2005-06-15', '909090'),
(12, 'Benjamin', 'maina', 'benjaminmaina@gmail.com', '0722601867', 'nyeri town', 'Nyeri', '2000-08-10', '909090');

-- --------------------------------------------------------

--
-- Table structure for table `referrals`
--

CREATE TABLE `referrals` (
  `referral_id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `referring_doctor_id` int(11) NOT NULL,
  `referred_to_doctor_id` int(11) NOT NULL,
  `appointment_id` int(11) DEFAULT NULL,
  `reason` text NOT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `resulting_appointment_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `referrals`
--

INSERT INTO `referrals` (`referral_id`, `patient_id`, `referring_doctor_id`, `referred_to_doctor_id`, `appointment_id`, `reason`, `status`, `created_at`, `resulting_appointment_id`) VALUES
(11, 10, 6, 28, 62, 'needs screening machines', 'Accepted', '2026-08-02 12:24:45', 63);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admins`
--
ALTER TABLE `admins`
  ADD PRIMARY KEY (`admin_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `appointments`
--
ALTER TABLE `appointments`
  ADD PRIMARY KEY (`appointment_id`),
  ADD UNIQUE KEY `unique_doctor_slot` (`doctor_id`,`appointment_date`,`appointment_time`),
  ADD KEY `fk_appointments_patient` (`patient_id`);

--
-- Indexes for table `audit_log`
--
ALTER TABLE `audit_log`
  ADD PRIMARY KEY (`log_id`);

--
-- Indexes for table `doctors`
--
ALTER TABLE `doctors`
  ADD PRIMARY KEY (`doctor_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `id_number` (`id_number`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`notification_id`),
  ADD KEY `fk_notifications_patient` (`patient_id`);

--
-- Indexes for table `patients`
--
ALTER TABLE `patients`
  ADD PRIMARY KEY (`patient_id`);

--
-- Indexes for table `referrals`
--
ALTER TABLE `referrals`
  ADD PRIMARY KEY (`referral_id`),
  ADD KEY `fk_referrals_patient` (`patient_id`),
  ADD KEY `fk_referrals_referring_doctor` (`referring_doctor_id`),
  ADD KEY `fk_referrals_referred_to_doctor` (`referred_to_doctor_id`),
  ADD KEY `fk_referrals_appointment` (`appointment_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admins`
--
ALTER TABLE `admins`
  MODIFY `admin_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `appointments`
--
ALTER TABLE `appointments`
  MODIFY `appointment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=72;

--
-- AUTO_INCREMENT for table `audit_log`
--
ALTER TABLE `audit_log`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=156;

--
-- AUTO_INCREMENT for table `doctors`
--
ALTER TABLE `doctors`
  MODIFY `doctor_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `notification_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=154;

--
-- AUTO_INCREMENT for table `patients`
--
ALTER TABLE `patients`
  MODIFY `patient_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `referrals`
--
ALTER TABLE `referrals`
  MODIFY `referral_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `appointments`
--
ALTER TABLE `appointments`
  ADD CONSTRAINT `fk_appointments_doctor` FOREIGN KEY (`doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_appointments_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE;

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `fk_notifications_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE;

--
-- Constraints for table `referrals`
--
ALTER TABLE `referrals`
  ADD CONSTRAINT `fk_referrals_appointment` FOREIGN KEY (`appointment_id`) REFERENCES `appointments` (`appointment_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `fk_referrals_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_referrals_referred_to_doctor` FOREIGN KEY (`referred_to_doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `fk_referrals_referring_doctor` FOREIGN KEY (`referring_doctor_id`) REFERENCES `doctors` (`doctor_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
