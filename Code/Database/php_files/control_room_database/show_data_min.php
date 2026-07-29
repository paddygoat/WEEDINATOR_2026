

<?php

// Include the credentials file. Using require_once ensures the script 
// will halt if the login details file is missing.
require_once '../login_details/login_details.php';

$host="localhost"; // Host name 
// $username="paddygoat_mushrooms"; // Mysql username 
// $password="sayno2drugs"; // Mysql password 
$db_name="paddygoat_weedinator_2024"; // Database name 
$tbl_name="control_room"; // Table name

// Connect to server and select database.
mysql_connect("$host", "$username", "$password")or die("cannot connect"); 
mysql_select_db("$db_name")or die("cannot select DB");


$query12="SELECT * FROM control_room ORDER BY id ASC LIMIT 100";
$result12=mysql_query($query12);
while ($row12 = mysql_fetch_array($result12)) {
  $id = $row12['ID'];
  $time_stamp = $row12['TIME'];
  $des_lat = $row12['des_lat'];
  $des_lon = $row12['des_lon'];
  
  // Print or process the retrieved data here
  // echo "ID: $id, Time: $time_stamp, Latitude: $des_lat, Longitude: $des_lon <br>";
  echo "id: $id; des_lat: $des_lat; des_lon: $des_lon; <br>";
}

// Use DateTime object to convert to Unix timestamp
// $dateTime = new DateTime($time_stamp);
// $unixTime = $dateTime->getTimestamp();

// echo "Unix timestamp: $unixTime";


// close MySQL connection 
mysql_close();
?>
