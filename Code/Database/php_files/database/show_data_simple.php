<?php

// Include the credentials file. Using require_once ensures the script 
// will halt if the login details file is missing.
require_once '../login_details/login_details.php';

$host="localhost"; // Host name 
// $username="paddygoat_mushrooms"; // Mysql username 
// $password="sayno2drugs"; // Mysql password 
$db_name="paddygoat_weedinator_2024"; // Database name 
$tbl_name="weedinator"; // Table name


// Establish your database connection here using mysqli
// Replace with your actual database credentials
$con = mysqli_connect("localhost", "paddygoat_mushrooms", "sayno2drugs", "paddygoat_weedinator_2024");

// Check connection
if (mysqli_connect_errno()) {
    echo "Failed to connect to MySQL:" . mysqli_connect_error();
    exit();
}

$query12 = "SELECT * FROM weedinator ORDER BY id DESC LIMIT 10";
$result12 = mysqli_query($con, $query12);

if ($result12) {
    while ($row12 = mysqli_fetch_assoc($result12)) {
        $id = $row12['ID'];
        $act_lat = $row12['act_lat'];
        $act_lon = $row12['act_lon'];
        echo "ID:" . $id;
        echo "act_lat:" . $act_lat;
        echo "act_lon:" . $act_lon;
        echo "?";
    }
} else {
    echo "Error:" . mysqli_error($con);
}

// close MySQL connection
mysqli_close($con);

?>