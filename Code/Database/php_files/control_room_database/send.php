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
$tableName="control_room"; // Table name

// --- Section to handle data from Python mapping app ---
if (isset($_POST['coords_data']))
{
    // Data from python mapping app:
    $coords_data = $_POST['coords_data'];
    echo "coords_data from python mapping app: " . $coords_data . "\n";

    try
    {
        // Establish PDO connection
        $db = new PDO('mysql:host=localhost;dbname=paddygoat_weedinator_2024', $username, $password);
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
        // SQL statement to delete all rows and reset the auto-increment counter
        // TRUNCATE is faster and more efficient than DELETE FROM when clearing an entire table.
        $sql = "TRUNCATE TABLE $tableName";
    
        // Prepare and execute the statement
        $stmt = $db->prepare($sql);
        $stmt->execute();

        echo "All rows deleted successfully from the table '$tableName'";echo"\n";

        // --- Start of code for parsing JSON ---
        // TODO: copy and paste the table entry code from below into here:
        echo "\n";
        echo "Start of code for parsing JSON:\n";
        try 
        {
            $coords_data = $_POST['coords_data'];
            echo "coords_data: " . $coords_data ."\n";
            // Decode the JSON string directly into a PHP array (which is the coordinate list)
            $des_coords_list = json_decode($coords_data, true);
            echo "des_coords_list: " . $des_coords_list ."\n";

            // Check if JSON decoding was successful and if it's an array
            if (json_last_error() === JSON_ERROR_NONE && is_array($des_coords_list)) 
            {
                if (count($des_coords_list) > 0) 
                {
                    // Determine the starting index. If the first element is [None, None], skip it.
                    // Otherwise, start from the first element.
                    $startIndex = 0;
                    // Fix for "syntax error, unexpected '['" in older PHP versions
                    // Instead of $des_coords_list[0] === [null, null], check elements individually
                    if (isset($des_coords_list[0]) &&
                        is_array($des_coords_list[0]) &&
                        count($des_coords_list[0]) === 2 &&
                        $des_coords_list[0][0] === null &&
                        $des_coords_list[0][1] === null) 
                        {
                        $startIndex = 1;
                        }

                    // Prepare the INSERT query for the 'test5' table
                    // This assumes '$tableName' table has 'des_lat' and 'des_lon' columns
                    $insert_coords_query = "INSERT INTO $tableName (des_lat, des_lon) VALUES (:des_lat, :des_lon)";
                    $coords_statement = $db->prepare($insert_coords_query);

                    $rows_inserted = 0;
                    // Iterate through the coordinate list starting from the determined index
                    for ($i = $startIndex; $i < count($des_coords_list); $i++) 
                    {
                        $coord_pair = $des_coords_list[$i];

                        // Ensure the pair is an array and has two elements (latitude and longitude)
                        if (is_array($coord_pair) && count($coord_pair) === 2) 
                        {
                            $des_lat = $coord_pair[0];
                            $des_lon = $coord_pair[1];

                            // Bind the values for the current coordinate pair
                            $coords_statement->bindParam(':des_lat', $des_lat);
                            $coords_statement->bindParam(':des_lon', $des_lon);

                            // Execute the prepared statement for each row
                            $coords_statement->execute();
                            $rows_inserted++;

                            echo "Inserted des_lat: " . $des_lat . ", des_lon: " . $des_lon . " into ". $tableName. "\n";
                        }
                        else 
                        {
                                    echo "Warning: Invalid coordinate pair format at index " . $i . ". Skipping this entry.\n";
                        }
                    }
                    echo "Successfully inserted " . $rows_inserted . " coordinate rows into " . $tableName . " table.\n";

                }
                else
                {
                    echo "Warning: The coordinate list is empty. No data inserted into " . $tableName . "\n";
                }
            }
            else
            {
                echo "Error: Failed to decode JSON data or data is not an array. JSON Error: " . json_last_error_msg() . ". No data inserted into " . $tableName . "\n";
            }
        }
        catch(PDOException $e)
        {
            echo "Error: " . $e->getMessage() . "\n"; // Error handling for initial connection/update
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
    echo "No data from python mapping app was received !!!\n";
}


$db = null;
?>


