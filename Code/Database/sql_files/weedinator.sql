-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jul 29, 2026 at 02:58 PM
-- Server version: 10.3.39-MariaDB
-- PHP Version: 8.1.34

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `paddygoat_weedinator_2024`
--

-- --------------------------------------------------------

--
-- Table structure for table `weedinator`
--

CREATE TABLE `weedinator` (
  `ID` int(10) NOT NULL,
  `TIME` timestamp NOT NULL DEFAULT current_timestamp(),
  `sig_str` int(5) NOT NULL DEFAULT 0,
  `operator` text NOT NULL,
  `act_heading` float NOT NULL DEFAULT 0,
  `des_heading` float NOT NULL,
  `act_steer_angle` float NOT NULL DEFAULT 0,
  `des_steer_angle` float NOT NULL,
  `act_lat` longtext NOT NULL DEFAULT '0',
  `des_lat` longtext NOT NULL,
  `act_lon` longtext NOT NULL DEFAULT '0',
  `des_lon` longtext NOT NULL,
  `act_throtA_val` int(11) NOT NULL DEFAULT 0,
  `des_throtA_val` int(11) NOT NULL,
  `act_speed` float NOT NULL DEFAULT 0,
  `GPSspeed_calc` longtext NOT NULL DEFAULT '0',
  `GPSspeedlimit` float NOT NULL DEFAULT 0,
  `encoderSteerVal` longtext NOT NULL DEFAULT '0',
  `GSM_session_num` int(10) NOT NULL DEFAULT 0,
  `carrierSolutionType` mediumtext NOT NULL DEFAULT 'Not Available',
  `GPSFixTime` mediumtext NOT NULL DEFAULT '\'Not Available\'',
  `myRelPosAcc` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `weedinator`
--
ALTER TABLE `weedinator`
  ADD PRIMARY KEY (`ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `weedinator`
--
ALTER TABLE `weedinator`
  MODIFY `ID` int(10) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
