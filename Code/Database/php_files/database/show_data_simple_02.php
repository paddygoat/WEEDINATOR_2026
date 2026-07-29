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

$host="localhost"; // Host name 
$db_name="paddygoat_weedinator_2024"; // Database name 
$tbl_name="weedinator"; // Table name

if (isset($_POST['ID_from_value'])) 
{
  // Data from python mapping app:
  $ID_from_value = $_POST['ID_from_value'];
  echo"Data from weedinator database: ID_from_value: ";echo $ID_from_value;
  $ID_to_value = $_POST['ID_to_value'];
  echo" ,ID_to_value: ";echo $ID_to_value;echo"\n";
} 
else 
{
  // Handle the case where 'ID_from_value' is not present in $_POST
  // You can set a default value, log an error, or take other actions.
  $ID_from_value = null; // Example: Set to null if not present
  // error_log("Missing data: 'ID_from_value' not found in \$_POST");
  echo "No data from python mapping app was received";
}


// Access the data sent from the Python script:
// $ID_from_value= $_POST['ID_from_value'];
// Access data sent from WEEDINATOR machine:
// $ID_from_value= $_GET['ID_from_value'];

// echo "\nData received from Python: " . $data;

// Establish your database connection here using mysqli
// Replace with your actual database credentials
$con = mysqli_connect("localhost", "paddygoat_mushrooms", "sayno2drugs", "paddygoat_weedinator_2024");

// Check connection
if (mysqli_connect_errno()) {
    echo "Failed to connect to MySQL:" . mysqli_connect_error();
    exit();
}

// $query12 = "SELECT * FROM weedinator ORDER BY id DESC LIMIT $ID_from_value";
$query12 = "SELECT * FROM weedinator WHERE id BETWEEN $ID_from_value AND $ID_to_value ORDER BY id DESC";
$result12 = mysqli_query($con, $query12);

if ($result12) {
    while ($row12 = mysqli_fetch_assoc($result12)) {
        $id = $row12['ID'];
        $act_lat = $row12['act_lat'];
        $act_lon = $row12['act_lon'];
        $myRelPosAcc = $row12['myRelPosAcc'];
        echo "ID:" . $id;
        echo "act_lat:" . $act_lat;
        echo "act_lon:" . $act_lon;
        echo "myRelPosAcc:" . $myRelPosAcc;
        echo "?";
    }
} else {
    echo "Error:" . mysqli_error($con);
}

$query13 = "SELECT * FROM weedinator ORDER BY id DESC LIMIT 1";
$result13 = mysqli_query($con, $query13);

if ($result13) {
    while ($row13 = mysqli_fetch_assoc($result13)) {
        $id = $row13['ID'];
        echo"\n";
        echo "latest_id:" . $id;
    }
} else {
    echo "Error:" . mysqli_error($con);
}

// close MySQL connection
mysqli_close($con);

?>
