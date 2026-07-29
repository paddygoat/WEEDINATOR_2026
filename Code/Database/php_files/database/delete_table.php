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
$tbl_name="control"; // Table name

// --- Section to handle data from Python mapping app ---
if (isset($_POST['delete_table_name']))
{
    // Data from python mapping app:
    $delete_table_name = $_POST['delete_table_name'];
    echo "delete_table_name from python mapping app: " . $delete_table_name . "\n";

    try
    {
        // Establish PDO connection
        $db = new PDO('mysql:host=localhost;dbname=paddygoat_weedinator_2024', $username, $password);
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // --- VALIDATION SECTION: Check if myData is a table name ---
        $tables_query = "SHOW TABLES";
        $statement = $db->query($tables_query);
        $tables = $statement->fetchAll(PDO::FETCH_COLUMN);

        $is_table_name = false;
        foreach ($tables as $table) {
            if (strtolower($delete_table_name) === strtolower($table)) { // Case-insensitive comparison
                $is_table_name = true;
                break;
            }
        }

        if ($is_table_name)  
        {
            echo "The provided data '" . $delete_table_name . "' is a valid table name !.\n";
            // SQL to drop table
            $sql = "DROP TABLE " . $delete_table_name;
            
            // This will throw an exception on error, which the catch block handles.
            $db->exec($sql);
            echo "Table " . $delete_table_name . " dropped successfully";
        }
        else
        {
            echo "Error: The provided data '" . $delete_table_name . "' is not a valid table name. Please choose a different name !!.\n";    
        }
    }
    catch(PDOException $e)
    {
        echo "Error: " . $e->getMessage() . "\n"; // Error handling for initial connection/update
    }
}
else
{
    // Handle the case where 'mydata' is not present in $_POST
    $mydata = null; // Example: Set to null if not present
    echo "After trying to delete a table, error: No data from python mapping app was received !!!\n";
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////






// --- Original SECTION: Echo all tables in the current database ---
// This section remains for informational purposes, separate from the data insertion logic.
echo "\n";
echo "\n--- Database Tables ---\n";
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

    if (count($tables) > 0) {
        echo "Tables in 'paddygoat_weedinator_2024':\n";
        foreach ($tables as $table) {
            echo "- " . $table . "\n";
        }
    } else {
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


