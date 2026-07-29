<?php

// Include the credentials file. Using require_once ensures the script 
// will halt if the login details file is missing.
require_once '../login_details/login_details.php';

$host="localhost"; // Host name 
$db_name="paddygoat_weedinator_2024"; // Database name 
$tbl_name="control"; // Table name

// Authenticate the request via custom header
$providedPassword = isset($_SERVER['HTTP_X_API_PASSWORD']) ? $_SERVER['HTTP_X_API_PASSWORD'] : '';

if ($providedPassword !== EXPECTED_PASSWORD) {
    http_response_code(401);
    die("Unauthorized access.");
}


// --- Original SECTION: Echo all tables in the current database ---
// This section remains for informational purposes, separate from the data insertion logic.
// echo "\n";
// echo "\n--- Database Tables ---\n";
try
{
    // Re-establish PDO connection if necessary (or use the existing $db object if still valid)
    // This ensures the table list is always attempted, even if the POST data was not present.
    if (!isset($db) || !$db) {
        $db = new PDO('mysql:host=localhost;dbname=paddygoat_weedinator_2024', $username, $password);
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }

    // Query to get all table names
    $tables_query = "SHOW TABLES";
    $statement = $db->query($tables_query);

    // Fetch all table names
    $tables = $statement->fetchAll(PDO::FETCH_COLUMN);

    if (count($tables) > 0) 
    {
        // echo "Tables in 'paddygoat_weedinator_2024':\n";
        foreach ($tables as $table) 
        {
            echo $table . "?";
        }
    }
    else
    {
        echo "No tables found in 'paddygoat_weedinator_2024'.\n";
    }
}
catch(PDOException $e)
{
    echo "Error listing tables: " . $e->getMessage() . "\n"; // Error handling for table listing
}
   

// Close the database connection (optional, PHP closes it automatically at script end)
$db = null;
?>


