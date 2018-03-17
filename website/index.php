<html>
    <head>
        <title>Consumer Program</title>
    </head>
    <body>
<?php
	$username = "phptest";
	$password = "1234567890";
	$data = array("username" => $username, "password" => $password);
	$url = "http://laptop-service/api/register";
	$postdata = http_build_query($data);  
	$opts = array('http' =>   
		array( 'method'  => 'POST','header'  => 'Content-type: application/x-www-form-urlencoded', 'content' => $postdata));  
	$context = stream_context_create($opts);  
	$result = file_get_contents($url, false, $context);


	$url1 = "http://laptop-service/api/login";
	$data1 = array("username" => $username, "password" => $password, "remember" => True);
	$postdata1 = http_build_query($data1);
	$opts1 = array('http' =>   
		array( 'method'  => 'POST','header'  => 'Content-type: application/x-www-form-urlencoded', 'content' => $postdata1));
	$context1 = stream_context_create($opts1);
	$result1 = file_get_contents($url1, false, $context1);

	$json = file_get_contents("http://laptop-service/api/token");
	$obj = json_decode($json);

	echo "<h2>listAll</h2>";
	$json = file_get_contents("http://laptop-service/listAll");
	$obj = json_decode($json);
	$Opens = $obj->open;
	$Closes = $obj->close;
	echo "Open Time:";
	foreach ($Opens as $o) {
		echo "<li>$o</li>";
	}
	echo "Close Time:";
	foreach ($Closes as $c) {
		echo "<li>$c</li>";
	}

	echo "<h2>listAll Top=2</h2>";
	$json = file_get_contents("http://laptop-service/listAll?top=2");
	$obj = json_decode($json);
	$Opens = $obj->open;
    $Closes = $obj->close;
	echo "Open Time:";
	foreach ($Opens as $o) {
		echo "<li>$o</li>";
	}
	echo "Close Time:";
	foreach ($Closes as $c) {
		echo "<li>$c</li>";
	}

	echo "<h2>listAll/Csv Top=2</h2>";
	echo file_get_contents("http://laptop-service/listAll/csv?top=2");

	echo "<h2>listOpenOnly</h2>";
	$json = file_get_contents("http://laptop-service/listOpenOnly");
	$obj = json_decode($json);
	$Opens = $obj->open;
	echo "Open Time:";
	foreach ($Opens as $o) {
		echo "<li>$o</li>";
	}

	echo "<h2>listOpenOnly Top=4</h2>";
	$json = file_get_contents("http://laptop-service/listOpenOnly?top=4");
	$obj = json_decode($json);
	$Opens = $obj->open;
	echo "Open Time:";
	foreach ($Opens as $o) {
		echo "<li>$o</li>";
	}

	echo "<h2>listOpenOnly/Csv Top=4</h2>";
	echo file_get_contents("http://laptop-service/listOpenOnly/csv?top=4");

	echo "<h2>listCloseOnly</h2>";
	$json = file_get_contents("http://laptop-service/listCloseOnly");
	$obj = json_decode($json);
	$Closes = $obj->close;
	echo "Close Time:";
	foreach ($Closes as $c) {
		echo "<li>$c</li>";
	}

	echo "<h2>listCloseOnly Top=3</h2>";
	$json = file_get_contents("http://laptop-service/listCloseOnly?top=3");
	$obj = json_decode($json);
	$Closes = $obj->close;
	echo "Close Time:";
	foreach ($Closes as $c) {
		echo "<li>$c</li>";
	}

	echo "<h2>listCloseOnly/Csv Top=3</h2>";
	echo file_get_contents("http://laptop-service/listCloseOnly/csv?top=3");
?>
    </body>
</html>