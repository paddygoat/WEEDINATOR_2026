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
$tableName="control"; // Table name

if (isset($_POST['myData_json']))
{
    // Data from python mapping app:
    $myData_json = $_POST['myData_json'];
    echo"myData_json from python mapping app:";echo $myData_json;echo"\n";
  
    // Decode the JSON string directly into a PHP array (which is the coordinate list)
    $myData = json_decode($myData_json, true);
    echo"myData from python mapping app:";echo $myData;echo"\n";
    try
    {
        // $db = new PDO('mysql:host=localhost;dbname=$db_name', $username, $password);
        $db = new PDO('mysql:host=localhost;dbname=paddygoat_weedinator_2024', $username, $password);
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    } 
        catch(PDOException $e) 
    {
        echo "Error: " . $e->getMessage(); // Error handling
    }
    
    // SQL statement to delete all rows and reset the auto-increment counter
    // TRUNCATE is faster and more efficient than DELETE FROM when clearing an entire table.
    $sql = "TRUNCATE TABLE $tableName";
    
    // Prepare and execute the statement
    $stmt = $db->prepare($sql);
    $stmt->execute();

    echo "All rows deleted successfully from the table '$tableName'";echo"\n";

    echo "Start of code for parsing JSON:\n";
    try 
    {
        // Check if JSON decoding was successful and if it's an array
        if (json_last_error() === JSON_ERROR_NONE && is_array($myData)) 
        {
            // Prepare the SQL INSERT statement
            $sql = "INSERT INTO $tableName (throttAVal, throttBVal) VALUES (?, ?)";
            $stmt = $db->prepare($sql);

            // Bind the values and execute the statement
            // Note: The structure of your myData array is unconventional for this type of operation.
            // We will assume that the first element of myData is the throttleA value and the second is throttleB.
            // Example: myData[0][1] = "34", myData[1][1] = "62"
    
            $throttAVal = $myData[0][1];
            $throttBVal = $myData[1][1];
    
            $stmt->execute(array($throttAVal, $throttBVal));

            echo "New record created successfully";
        }
        else
        {
            echo "Error: Failed to decode JSON data or data is not an array. JSON Error: " . json_last_error_msg() . ". No data inserted into " . $tableName . "\n";
        }
    }

    catch (PDOException $e)
    {
        echo "Error updating table '" . $tableName . "': " . $e->getMessage() . "\n";
    }
  
} 
else 
{
  // Handle the case where 'GSM_session_data' is not present in $_POST
  // You can set a default value, log an error, or take other actions.
  $GSM_session_data = null; // Example: Set to null if not present
  // error_log("Missing data: 'GSM_session_data' not found in \$_POST");
  echo "No data from python mapping app was received";
}


// Access the data sent from the Python script:
// $GSM_session_data= $_POST['GSM_session_data'];
// Access data sent from WEEDINATOR machine:
// $GSM_session_data= $_GET['GSM_session_data'];

// echo "\nData received from Python: " . $data;


// Connect to server and select database.
mysql_connect("$host", "$username", "$password")or die("cannot connect"); 
mysql_select_db("$db_name")or die("cannot select DB");


//$query12="SELECT * FROM weedinator ORDER BY id DESC LIMIT 1";
$query12="SELECT * FROM control ORDER BY id DESC LIMIT 1";
$result12=mysql_query($query12);
$counter = 0; // Initialize counter variable outside the loop


// Delete all rows from the table control_room_test_apr_21
// $delete_query = "DELETE FROM control_room_test_apr_21";
// $result = mysql_query($delete_query) or die("Error deleting rows: " . mysql_error());

// if ($result) 
// {
    // echo "\nAll rows successfully deleted from the table 'control_room_test_apr_21'.";
// }


while($row12=mysql_fetch_array($result12))
    {  
    $throttAVal = $row12['throttAVal'];
    $throttBVal= $row12['throttBVal'];
    // $GSM_session_num  = $row12['GSM_session_num'];

    // echo"\nline_num:";echo $counter;
    echo"\nthrottAVal:";echo $throttAVal;
    echo",throttBVal:";echo $throttBVal;
    // echo",GSM_session_num:";echo $GSM_session_num;
   
    // Prepare the insert query
    // $insert_query = "INSERT INTO control_room_test_apr_21 (des_lat, des_lon) 
    //               VALUES ('$act_lat', '$act_lon')";

    // Execute the insert query
    // $insert_result = mysql_query($insert_query);
   
    // $counter++;
    }
   
   

mysql_close();
?>
