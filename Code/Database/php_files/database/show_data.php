<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">

  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="0">
  
  <meta http-equiv='refresh' content='60';url='showdata.php'> <!-- Refreshes page every 60 seconds -->
  <META NAME="description" CONTENT="WEEDINATOR">

  <META NAME="keywords" CONTENT="WEEDINATOR">

  <link REL="SHORTCUT ICON" HREF="http://www.goatindustries.co.uk/goat.ico">
  <title>WEEDINATOR - Show Data</title>


</html>

<?php

// Include the credentials file. Using require_once ensures the script 
// will halt if the login details file is missing.
require_once '../login_details/login_details.php';

$host="localhost"; // Host name 
// $username="paddygoat_mushrooms"; // Mysql username 
// $password="sayno2drugs"; // Mysql password 
$db_name="paddygoat_weedinator_2024"; // Database name 
$tbl_name="weedinator"; // Table name

// Connect to server and select database.
mysql_connect("$host", "$username", "$password")or die("cannot connect"); 
mysql_select_db("$db_name")or die("cannot select DB");


$query12="SELECT * FROM weedinator ORDER BY id DESC LIMIT 1";
$result12=mysql_query($query12);
while($row12=mysql_fetch_array($result12))
   {  
   $id = $row12['ID'];
   $time_stamp = $row12['TIME'];
   $act_lat = $row12['act_lat'];
   $act_lon = $row12['act_lon'];
   $act_lat = $row12['act_steer_angle'];
   $act_lon = $row12['act_throtA_val'];
   $sig_str = $row12['sig_str'];
   }
   
$query13="SELECT * FROM weedinator ORDER BY id DESC LIMIT 2";
$result13=mysql_query($query13);
while($row13=mysql_fetch_array($result13))
   {  
   $id_previous = $row12['ID'];
   $time_stamp_previous = $row13['TIME'];
   $lat_previous = $row13['act_lat'];
   $lon_previous = $row13['act_lon'];
   }
   
// Time stuff:
$time_stamp_previous2 = strtotime($time_stamp_previous);
// echo(date("M-d h:i:s",$time_stamp_previous2));

$localTime = time();
// echo(date("M-d h:i:s",$localTime));

$timestamp2 = strtotime($time_stamp);
// echo(date("M-d H:i:s",$timestamp2));

$timeDifference = $localTime - $timestamp2;
// echo $timeDifference;

$timeDifference2 = $timestamp2 - $time_stamp_previous2;
// echo $timeDifference2;


// Fetch the latest data in reverse order then flip it over:
$result2 = mysql_query("SELECT * FROM (
                      SELECT *
                      FROM weedinator ORDER BY ID 
                      DESC LIMIT 250) result 
                      ORDER BY ID DESC   
                    ");

?>

<style type="text/css">
<!--
.style1 {font-size: 10px}  <!-- Data font size -->
-->
</style>

<style type="text/css">
<!--
.style2 {font-size: 10px}  <!-- Readings font size -->
-->
</style>

<style type="text/css">
<!--
.style3 {font-size: 14px; text-decoration: underline; font-weight: bold; opacity: 0.7}  <!-- Heading -->
-->
</style>

<style type="text/css">
.blink_me {
  color: green;
  font-size: 14px
  font-weight: bold;
  animation: blinker 1s linear infinite;
}

@keyframes blinker {
  50% {
    opacity: 0;
  }
}
</style>

<body>
	
<table width="580">
  <tr><span class="style2">
    <td><div align="center"><span class="style3">WEEDINATOR</td>
  </tr>
</table>

<table width="580">
  <tr><span class="style2">
    <td><span class="style2">Last update: <?php echo(date("M-d H:i:s",$timestamp2)); ?></td>
    <td><span class="style2">UTC (GMT) time: <?php echo(date("M-d H:i:s",$localTime)); ?></td>
	<?php

	if ($timeDifference < "1200000")
	{
		?> <td><div align="center"><div class="blink_me">NOW LIVE !</div></td> <?php
	} else {
		?> <td><div align="right"><span class="style2">NOT LIVE</td><td><span class="style2">... Please check later.</td> <?php
	}
	?>
    
  </tr>
  <tr>
    <td><span class="style2">Signal strength: <?php echo $sig_str; ?> </td>
  </tr>
</table>


<table width="680" border="1" cellspacing="0" cellpadding="0">
	<tr>
		<td width="6%"><span class="style1"><div align="center">Id </div></td>
		<td width="12%"><span class="style1"><div align="center">Time Stamp </div></td>
		<td width="9%"><span class="style1"><div align="center">Act_Lat </div></td>
		<td width="8%"><span class="style1"><div align="center">Act_Lon </div></td>
		<td width="9%"><span class="style1"><div align="center">Act_Steer_Angle </div></td>
		<td width="8%"><span class="style1"><div align="center">Act_ThrotA_Val </div></td>
		<td width="8%"><span class="style1"><div align="center">Sig Str </div></td>
		<td width="8%"><span class="style1"><div align="center">GPSFixTime </div></td>
		<td width="8%"><span class="style1"><div align="center">myRelPosAcc </div></td>		
	</tr>
</table>
<table width="680" border="1" cellspacing="0" cellpadding="0"> 
 
<?php

// Start looping rows in mysql database.
while($rows=mysql_fetch_array($result2))
{

?>

 <tr>
 <td bgcolor="#cce2ff" width="6%"><div align="center"><span class="style1"><? echo $rows['ID']; ?></span></td>
 <td bgcolor="#FFFFCC" width="12%"><div align="center"><span class="style1"><? echo $rows['TIME']; ?></span></td>
 <td bgcolor="#ccffcd" width="9%"><div align="center"><span class="style1"><? echo $rows['act_lat']; ?></span></td>
 <td bgcolor="#ffccd9" width="8%"><div align="center"><span class="style1"><? echo $rows['act_lon']; ?></span></td>
 <td bgcolor="#ccffcd" width="9%"><div align="center"><span class="style1"><? echo $rows['act_steer_angle']; ?></span></td>
 <td bgcolor="#ffccd9" width="8%"><div align="center"><span class="style1"><? echo $rows['act_throtA_val']; ?></span></td>
 <td bgcolor="#ffccd9" width="8%"><div align="center"><span class="style1"><? echo $rows['sig_str']; ?></span></td>
 <td bgcolor="#FFFFCC" width="8%"><div align="center"><span class="style1"><? echo $rows['GPSFixTime']; ?></span></td>
 <td bgcolor="#FFFFCC" width="8%"><div align="center"><span class="style1"><? echo $rows['myRelPosAcc']; ?></span></td>
 </tr>

<?php
// close while loop 
}

?>
</table>
</body>
</html>

<p><span class="style2"><?
echo"Time interval = ";
echo(date("H:i:s",$timeDifference2));
?></p>

<p><span class="style2"><?
echo"Next update due at: ";
$next_update = $timeDifference2 + $timestamp2;
echo(date("M-d H:i:s",$next_update));
?></p><?

// close MySQL connection 
mysql_close();
 ?>
