<?php

// Include the credentials file. Using require_once ensures the script 
// will halt if the login details file is missing.
require_once '../login_details/login_details.php';

// Authenticate the request via custom header
$providedPassword = isset($_SERVER['HTTP_X_API_PASSWORD']) ? $_SERVER['HTTP_X_API_PASSWORD'] : '';

if ($providedPassword !== EXPECTED_PASSWORD) {
    http_response_code(401);
    die("Unauthorized access.");
}

$host = "localhost"; // Host name
$db_name = "paddygoat_weedinator_2024"; // Database name
$tbl_name = "control_room"; // Table name

// 1. Connect to server and select database using mysqli_connect
// $username and $password are inherited from login_details.php
$conn = mysqli_connect($host, $username, $password, $db_name);

// Check connection
if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}

// 2. Delete all rows from the table
$delete_query = "DELETE FROM $tbl_name";

// In mysqli, the connection variable ($conn) must be the first argument
$result = mysqli_query($conn, $delete_query);

if ($result) 
{
    echo "All rows successfully deleted from the table 'control_room'.";
}
else 
{
    // Handle error using mysqli_error
    die("Error deleting rows: " . mysqli_error($conn));
}

// 3. Close MySQL connection
mysqli_close($conn);

?>