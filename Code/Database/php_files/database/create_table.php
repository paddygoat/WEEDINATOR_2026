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
if (isset($_POST['new_table_name']))
{
    // Data from python mapping app:
    $new_table_name = $_POST['new_table_name'];
    echo "new_table_name from python mapping app: " . $new_table_name . "\n";

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
            if (strtolower($new_table_name) === strtolower($table)) { // Case-insensitive comparison
                $is_table_name = true;
                break;
            }
        }

        if ($is_table_name) 
        {
            echo "Error: The provided data '" . $new_table_name . "' cannot be a table name as it already exists. Please choose a different name !!.\n";
        }
        else 
        {
            // Proceed with the UPDATE query only if myData is not a table name
            // $insert_query = "UPDATE control SET session = :myData WHERE ID = 1";
            // $statement = $db->prepare($insert_query);

            // Bind the data to the placeholder
            // $statement->bindParam(':myData', $myData);

            // Execute the prepared statement
            // $statement->execute();

            // echo "Data inserted successfully!\n"; // Success message

            // --- NEW SECTION: Create a new table with myData as the table name ---
            echo "\n";
            echo "\n--- Attempting to create new table: " . $new_table_name . " ---\n";
            // IMPORTANT SECURITY NOTE: Dynamically creating table names from user input
            // without very strict validation can be a SQL injection risk.
            // A basic sanitization is applied here, but for production, consider
            // a whitelist of allowed names or more robust validation.
            $tableName = preg_replace('/[^a-zA-Z0-9_]/', '', $new_table_name); // Basic alphanumeric and underscore sanitization

            if (empty($tableName)) 
            {
                echo "Error: Invalid table name derived from new_table_name. Table creation aborted.\n";
            } 
            else 
            {
                // The full SQL for table creation, with dynamic table name
                $create_table_sql = "
                    SET SQL_MODE = \"NO_AUTO_VALUE_ON_ZERO\";
                    START TRANSACTION;
                    SET time_zone = \"+00:00\";

                    /*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
                    /*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
                    /*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
                    /*!40101 SET NAMES utf8mb4 */;

                    --
                    -- Database: `paddygoat_weedinator_2024`
                    --

                    -- --------------------------------------------------------

                    --
                    -- Table structure for table `" . $tableName . "`
                    --

                    CREATE TABLE `" . $tableName . "` (
                        `ID` int(10) NOT NULL,
                        `TIME` timestamp NOT NULL DEFAULT current_timestamp(),
                        `des_lat` text CHARACTER SET latin1 COLLATE latin1_general_cs NOT NULL DEFAULT '0',
                        `des_lon` text CHARACTER SET latin1 COLLATE latin1_general_cs NOT NULL DEFAULT '0'
                    ) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

                    --
                    -- Indexes for dumped tables
                    --

                    --
                    -- Indexes for table `" . $tableName . "`
                    --
                    ALTER TABLE `" . $tableName . "`
                        ADD PRIMARY KEY (`ID`);

                    --
                    -- AUTO_INCREMENT for dumped tables
                    --

                    --
                    -- AUTO_INCREMENT for table `" . $tableName . "`
                    --
                    ALTER TABLE `" . $tableName . "`
                        MODIFY `ID` int(10) NOT NULL AUTO_INCREMENT;
                    COMMIT;

                    /*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
                    /*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
                    /*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
                ";

                try 
                {
                    // PDO's exec() is used for executing SQL statements that do not return a result set,
                    // and it can handle multiple statements separated by semicolons.
                    $db->exec($create_table_sql);
                    echo "Table '" . $tableName . "' created successfully!\n";
                } 
                catch (PDOException $e) 
                {
                    echo "Error creating table '" . $tableName . "': " . $e->getMessage() . "\n";
                }
                
                
////////////////////////////////////////////////////////////////////////////////////////////////////////////
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

                catch (PDOException $e)
                {
                    echo "Error creating table '" . $tableName . "': " . $e->getMessage() . "\n";
                }              
////////////////////////////////////////////////////////////////////////////////////////////////////////////
                
            }
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
    echo "After trying to create a table, error: No data from python mapping app was received !!!\n";
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


