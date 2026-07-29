<?php

// Include the credentials file.
require_once '../login_details/login_details.php';

// 1. PHP 5.3 Compatible Security Check
$providedPassword = isset($_SERVER['HTTP_X_API_PASSWORD']) ? $_SERVER['HTTP_X_API_PASSWORD'] : '';
if ($providedPassword !== EXPECTED_PASSWORD) {
    // PHP 5.3 way of setting a 401 status code
    header('HTTP/1.1 401 Unauthorized', true, 401);
    die("Unauthorized access.");
}

// Database credentials setup
$host="localhost"; 
$db_name="paddygoat_weedinator_2024"; 
$tbl_name="weedinator"; 

// Connect to server using mysqli_connect
$dbhandle = mysqli_connect($host, $username, $password, $db_name);
if (!$dbhandle) {
    die("Unable to connect to MySQL: " . mysqli_connect_error());
}

// Retrieve data from database 
$sql3="SELECT * FROM weedinator ORDER BY id DESC LIMIT 1";
$result3=mysqli_query($dbhandle, $sql3);
while($row13=mysqli_fetch_array($result3))
{
    $data = $row13['GSM_session_num'];
}
echo "GSM_session_num: ";
echo $data;

$box = 2;

////////////////////////////////////////////////////////////////////////////////

try {
    $pdo = new PDO("mysql:host=$host;dbname=$db_name", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Python is sending a POST request, so we look for POST
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        
        // Fixed the act_speed database column name
        $stmt = $pdo->prepare("INSERT INTO weedinator 
            (act_lat, act_lon, act_steer_angle, act_throtA_val, act_heading, act_speed, GPSspeed_calc, encoderSteerVal, GSM_session_num, carrierSolutionType, GPSFixTime, myRelPosAcc) 
            VALUES 
            (:act_lat, :act_lon, :act_steer_angle, :act_throtA_val, :act_heading, :mySpeed, :GPSspeed_calc, :encoderSteerVal, :GSM_session_num, :carrierSolutionType, :GPSFixTime, :myRelPosAcc)");
        
        $stmt->execute(array(
            ':act_lat' => isset($_POST['act_lat']) ? $_POST['act_lat'] : 0,
            ':act_lon' => isset($_POST['act_lon']) ? $_POST['act_lon'] : 0,
            ':act_steer_angle' => isset($_POST['act_steer_angle']) ? $_POST['act_steer_angle'] : 0,
            ':act_throtA_val' => isset($_POST['act_throtA_val']) ? $_POST['act_throtA_val'] : 0,
            ':act_heading' => isset($_POST['act_heading']) ? $_POST['act_heading'] : 0,
            ':mySpeed' => isset($_POST['mySpeed']) ? $_POST['mySpeed'] : 0,
            ':GPSspeed_calc' => isset($_POST['GPSspeed_calc']) ? $_POST['GPSspeed_calc'] : 0,
            ':encoderSteerVal' => isset($_POST['encoderSteerVal']) ? $_POST['encoderSteerVal'] : 0,
            ':GSM_session_num' => isset($_POST['GSM_session_num']) ? $_POST['GSM_session_num'] : 0,
            ':carrierSolutionType' => isset($_POST['carrierSolutionType']) ? $_POST['carrierSolutionType'] : '',
            ':GPSFixTime' => isset($_POST['GPSFixTime']) ? $_POST['GPSFixTime'] : '',
            ':myRelPosAcc' => isset($_POST['myRelPosAcc']) ? $_POST['myRelPosAcc'] : 0
        ));
        
        echo "Data inserted successfully.";
    }
} catch (PDOException $e) {
    // If the database fails (e.g., column doesn't exist), send a 500 error back to Python
    header('HTTP/1.1 500 Internal Server Error', true, 500);
    echo "Database error: " . $e->getMessage();
}
//////////////////////////////////////////////////////////////////////////////////

$query12="SELECT * FROM weedinator ORDER BY id DESC LIMIT 1";
$result12=mysqli_query($dbhandle, $query12);
while($row12=mysqli_fetch_array($result12))
   {  
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

echo"weedinator table current ID:";echo $id;

// close MySQL connection 
mysqli_close($dbhandle);
?>