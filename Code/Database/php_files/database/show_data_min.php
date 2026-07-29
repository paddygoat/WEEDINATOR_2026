<?php

// Include the credentials file. Using require_once ensures the script 
// will halt if the login details file is missing.
require_once '../login_details/login_details.php';

$host="localhost"; // Host name 
$db_name="paddygoat_weedinator_2024"; // Database name 
$tbl_name="weedinator"; // Table name

// 1. Connect to server and select database using mysqli_connect
// Ensure $username and $password are defined in login_details.php
$conn = mysqli_connect($host, $username, $password, $db_name);

// Check the connection and kill the script if it fails
if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}

$query12 = "SELECT * FROM weedinator ORDER BY id DESC LIMIT 1";

// 2. Execute the query (requires the $conn variable)
$result12 = mysqli_query($conn, $query12);

// 3. Check if the query returned results
if ($result12) {
    // 4. Use mysqli_fetch_assoc for cleaner associative array mapping
    while($row12 = mysqli_fetch_assoc($result12)) {  
       $id = $row12['ID'];
       $time_stamp = $row12['TIME'];
       $act_lat = $row12['act_lat'];
       $act_lon = $row12['act_lon'];
       $act_heading = $row12['act_heading'];
       $act_steer_angle = $row12['act_steer_angle'];
       $act_throtA_val = $row12['act_throtA_val'];
       $sig_str = $row12['sig_str'];
       $act_speed = $row12['act_speed'];
       $myRelPosAcc = $row12['myRelPosAcc'];
    }
    
    // Free up the result set memory
    mysqli_free_result($result12);
} else {
    // Handle query errors
    die("Error running query: " . mysqli_error($conn));
}

// Use DateTime object to convert to Unix timestamp
$dateTime = new DateTime($time_stamp);
$unixTime = $dateTime->getTimestamp();

// echo "Unix timestamp: $unixTime";

echo "ID:"; echo $id;
echo "TIME:"; echo $unixTime;
echo "act_lat:"; echo $act_lat;
echo "act_lon:"; echo $act_lon;
echo "act_heading:"; echo $act_heading;
echo "act_steer_angle:"; echo $act_steer_angle;
echo "act_throtA_val:"; echo $act_throtA_val;
echo "sig_str:"; echo $sig_str;
echo "act_speed:"; echo $act_speed;
echo "myRelPosAcc:"; echo $myRelPosAcc;

// 5. close MySQL connection (requires the $conn variable)
mysqli_close($conn);

?>