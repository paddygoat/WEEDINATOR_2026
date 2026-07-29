<?php

// Include the credentials file. Using require_once ensures the script 
// will halt if the login details file is missing.[cite: 3]
require_once '../login_details/login_details.php';

// Expected server password (ensure this matches what is read by passwords.py on the Jetson Nano)
// You can also move this definition into login_details.php for better centralization.
// define('EXPECTED_PASSWORD', 'YourSecurePasswordHere');

// 1. Authenticate the request via custom header
$providedPassword = isset($_SERVER['HTTP_X_API_PASSWORD']) ? $_SERVER['HTTP_X_API_PASSWORD'] : '';

if ($providedPassword !== EXPECTED_PASSWORD) {
    http_response_code(401);
    die("Unauthorized access.");
}

$host = "localhost"; // Host name[cite: 3]
// $username and $password are pulled from the required file above[cite: 3]
$db_name = "paddygoat_weedinator_2024"; // Database name[cite: 3]
$tbl_name = "des_coords"; // Table name[cite: 3]

try {
    // 2. Connect to server and select database using PDO for improved security
    $dsn = "mysql:host=$host;dbname=$db_name;charset=utf8mb4";
    $options = array(
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false, // Disables emulated prepared statements, enforcing true database-level prep
    );
    
    $pdo = new PDO($dsn, $username, $password, $options);

    $query12 = "SELECT * FROM des_coords ORDER BY id DESC LIMIT 1"; //[cite: 3]

    // 3. Execute the query
    $stmt = $pdo->query($query12);

    // 4. Check if the query actually returned results before looping[cite: 3]
    if ($stmt) {
        // Use fetch() instead of mysqli_fetch_assoc[cite: 3]
        while ($row12 = $stmt->fetch()) {
            $id = $row12['ID'];
            $time_stamp = $row12['TIME'];
            $des_lat = $row12['des_lat'];
            $des_lon = $row12['des_lon'];
            
            // Print or process the retrieved data here[cite: 3]
            // echo "ID: $id, Time: $time_stamp, Latitude: $des_lat, Longitude: $des_lon <br>";[cite: 3]
            echo "id: $id; time_stamp: $time_stamp; des_lat: $des_lat; des_lon: $des_lon; <br>"; //[cite: 3]
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

// 5. Close MySQL connection
// PDO connections are closed automatically when the object is destroyed, 
// but you can explicitly close it by setting the PDO object to null.
$pdo = null;

?>