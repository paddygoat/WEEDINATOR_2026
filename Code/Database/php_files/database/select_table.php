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


// --- Section to handle data from Python mapping app ---
if (isset($_POST['selected_route']))
{
    // Data from python mapping app:
    $selected_route = $_POST['selected_route'];
    // echo "selected_route from python mapping app: " . $selected_route . "\n";

    try
    {
        // Establish PDO connection
        $db = new PDO('mysql:host=localhost;dbname=paddygoat_weedinator_2024', $username, $password);
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // Prepare the SQL query to get the last 100 rows
        $sql = "SELECT des_lat, des_lon FROM $selected_route ORDER BY ID ASC LIMIT 500";

        // Prepare the statement
        $stmt = $db->prepare($sql);

        // Execute the statement
        $stmt->execute();

        // Check if there are results
        if ($stmt->rowCount() > 0) 
        {
            // echo "Coordinates from the last 100 rows:\n";
            // Fetch and display all results
            while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) 
            {
                echo "des_lat:" . $row['des_lat'] . ",des_lon:" . $row['des_lon'] . ",";
            }
        }
        else
        {
            echo "No rows found in the table.\n";
        }
    }
    catch (PDOException $e)
    {
        // Output any connection or query errors
        echo "Error: " . $e->getMessage() . "\n";
    }
}