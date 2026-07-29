<?php

// Include the credentials file. Using require_once ensures the script 
// will halt if the login details file is missing.[cite: 4]
require_once '../login_details/login_details.php';

// Expected server password (ensure this matches what is read by passwords.py on the Jetson Nano)
// define('EXPECTED_PASSWORD', 'YourSecurePasswordHere');

// 1. Authenticate the request via custom header
$providedPassword = isset($_SERVER['HTTP_X_API_PASSWORD']) ? $_SERVER['HTTP_X_API_PASSWORD'] : '';

if ($providedPassword !== EXPECTED_PASSWORD) {
    http_response_code(401);
    die("Unauthorized access.");
}

$host = "localhost"; // Host name[cite: 4]
// $username and $password are pulled from the required file above[cite: 4]
$db_name = "paddygoat_weedinator_2024"; // Database name[cite: 4]
$tbl_name = "des_coords"; // Table name[cite: 4]

try {
    // 2. Connect to server and select database using PDO for improved security
    $dsn = "mysql:host=$host;dbname=$db_name;charset=utf8mb4";
    $options = array(
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false, 
    );
    
    $pdo = new PDO($dsn, $username, $password, $options);

    $query12 = "SELECT * FROM des_coords ORDER BY id DESC LIMIT 1000"; //[cite: 4]

    // 3. Execute the query
    $stmt = $pdo->query($query12);

    // 4. Check if the query actually returned results before looping[cite: 4]
    if ($stmt) {
        // Use fetch() instead of mysqli_fetch_assoc
        while ($row12 = $stmt->fetch()) {
            $id = $row12['ID']; //[cite: 4]
            $time_stamp = $row12['TIME']; //[cite: 4]
            $des_lat = $row12['des_lat']; //[cite: 4]
            $des_lon = $row12['des_lon']; //[cite: 4]
            
            // Print or process the retrieved data here[cite: 4]
            // echo "ID: $id, Time: $time_stamp, Latitude: $des_lat, Longitude: $des_lon <br>";[cite: 4]
            echo "id: $id; des_lat: $des_lat; des_lon: $des_lon; ?"; //[cite: 4]
        }
    } else {
        // If the query fails for a non-exception reason
        echo "Error running query.";
    }

} catch (PDOException $e) {
    // If the connection or query fails, print the error and set a 500 status code
    http_response_code(500);
    die("Database error: " . $e->getMessage());
}

// Use DateTime object to convert to Unix timestamp[cite: 4]
// $dateTime = new DateTime($time_stamp);[cite: 4]
// $unixTime = $dateTime->getTimestamp();[cite: 4]
// echo "Unix timestamp: $unixTime";[cite: 4]

// 5. Close MySQL connection
$pdo = null;

?>